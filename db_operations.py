import psycopg2
import logging
import json
from datetime import datetime
from psycopg2.extras import execute_values


# Load config
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as file:
    CONFIG = json.load(file)

LOG_FILE = CONFIG.get("logging", {}).get("log_file", "CGcryptobot.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CACHE = {}

def connect_db():
    """Establish connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=CONFIG["database"]["dbname"],
            user=CONFIG["database"]["user"],
            password=CONFIG["database"]["password"],
            host=CONFIG["database"]["host"],
            port=CONFIG["database"]["port"]
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

def get_cached_coins():
    """Return coins from cache or load from DB if cache is empty."""
    if CACHE:
        return list(CACHE.values())

    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, name, source FROM coins ORDER BY created_at DESC LIMIT 50")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            coins = [{"symbol": row[0], "name": row[1], "source": row[2]} for row in rows]
            for coin in coins:
                CACHE[coin["symbol"]] = coin
            return coins
        except Exception as e:
            logging.error(f"Error fetching coins: {e}")
    return []

def get_existing_binance_symbols():
    conn = connect_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM coins WHERE source = 'binance'")
        results = cursor.fetchall()
        return {r[0] for r in results}
    except Exception as e:
        logging.error(f"Error checking existing symbols: {e}")
        return set()
    finally:
        cursor.close()
        conn.close()

async def fetch_dexscreener_pair_metadata(token_address, chain_id):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{token_address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.error(f"pair metadata {data}")
                    return data.get("pairCreatedAt")
    except Exception as e:
        logging.warning(f"Error fetching pair metadata: {e}")
    return None

    
async def store_coins(coin_list, source):
    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        if source == "binance":
            cursor.execute("SELECT symbol FROM coins WHERE source = 'binance'")
            existing_symbols = {row[0] for row in cursor.fetchall()}

            coin_list = [symbol for symbol in coin_list if symbol.get('symbol').endswith("USDT") and symbol.get('symbol') not in existing_symbols]
        
        
        values = []
        for coin in coin_list:
            if isinstance(coin, dict):  # Dex Screener style
                created_at = coin.get("created_at")

                if not created_at:
                    created_at = await fetch_dexscreener_pair_metadata(
                        coin.get("token_address"), coin.get("chain_id")
                    )
                if created_at is None:
                    created_at = datetime.utcnow()
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at)
                    except:
                        created_at = datetime.utcnow()

                values.append((
                    coin.get("symbol"),
                    coin.get("name"),
                    source,
                    created_at.isoformat(),
                    coin.get("chain_id"),
                    coin.get("token_address"),
                    coin.get("icon", ""),
                    coin.get("header"),
                    coin.get("open_graph", ""),
                    coin.get("description", ""),
                    json.dumps(coin.get("links", []))
                ))
            else:  # Binance style (symbol as string)
                values.append((
                    coin.get("symbol"),
                    coin.get("name"),
                    source,
                    datetime.utcnow().isoformat(),
                    None, None, None, None, None, None, None
                ))

        logging.debug(f"new coin values are {values}")

        query = """
        INSERT INTO coins (
            symbol, name, source, created_at,
            chain_id, token_address, icon, header, open_graph, description, links
        ) VALUES %s
        ON CONFLICT (symbol, source, created_at) DO NOTHING
        """
        logging.info(f"values are {values} query is {query}")
        execute_values(cursor, query, values)
        conn.commit()
        logging.info(f"Inserted {len(values)} coins into DB from {source}.")

    except Exception as e:
        logging.error(f"Error storing coins: {e}")
    finally:
        cursor.close()
        conn.close()
