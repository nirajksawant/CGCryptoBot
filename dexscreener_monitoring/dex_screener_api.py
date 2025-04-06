import aiohttp
from datetime import datetime
import logging
import json
from psycopg2.extras import execute_values
from db import connect_db  # Assuming connect_db is defined in db.py

# -------------------------------------------
# Fetch DEX Pair Metadata (e.g., pairCreatedAt)
# -------------------------------------------
async def fetch_dexscreener_pair_metadata(token_address, chain_id):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{token_address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("pairCreatedAt")
                else:
                    logging.warning(f"Non-200 from Dex pair metadata API: {response.status}, URL: {url}")
    except Exception as e:
        logging.warning(f"Error fetching pair metadata from {url}: {e}")
    return None

# ------------------------------------------------------
# Fetch DEX Token Profile (links and social media info)
# ------------------------------------------------------
async def fetch_dexscreener_links_extra(token_address):
    url = f"https://api.dexscreener.com/token-profiles/latest/v1/{token_address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("links")
                else:
                    logging.debug(f"Dexscreener profile not found for token: {token_address}, status: {response.status}, URL: {url}")
    except Exception as e:
        logging.warning(f"Error fetching token profile from {url}: {e}")
    return {}

# ------------------------------------------------------
# Store Token Profiles in token_profiles Table
# ------------------------------------------------------
async def store_token_profiles(token_data_list):
    conn = connect_db()
    if not conn:
        logging.error("Failed to connect to DB for storing token profiles.")
        return

    try:
        cursor = conn.cursor()

        values = []
        for token in token_data_list:
            token_address = token.get("token_address")
            if not token_address:
                logging.debug("Skipping token with missing address.")
                continue

            created_at = token.get("created_at")
            if not created_at:
                created_at = await fetch_dexscreener_pair_metadata(token_address, token.get("chain_id"))
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except Exception as e:
                    logging.debug(f"Failed to parse created_at for {token_address}: {e}")
                    created_at = datetime.utcnow()
            if not created_at:
                created_at = datetime.utcnow()

            links_extra = await fetch_dexscreener_links_extra(token_address)

            values.append((
                token_address,
                token.get("symbol"),
                token.get("name"),
                token.get("chain_id"),
                created_at,
                datetime.utcnow(),
                token.get("icon"),
                token.get("header"),
                token.get("open_graph"),
                token.get("description"),
                json.dumps(token.get("links", {})),
                json.dumps(links_extra)
            ))

        if not values:
            logging.info("No token profiles to insert.")
            return

        query = """
        INSERT INTO token_profiles (
            token_address, symbol, name, chain_id, created_at, fetched_at,
            icon, header, open_graph, description, links, links_extra
        ) VALUES %s
        ON CONFLICT (token_address) DO UPDATE SET
            symbol = EXCLUDED.symbol,
            name = EXCLUDED.name,
            chain_id = EXCLUDED.chain_id,
            created_at = EXCLUDED.created_at,
            fetched_at = EXCLUDED.fetched_at,
            icon = EXCLUDED.icon,
            header = EXCLUDED.header,
            open_graph = EXCLUDED.open_graph,
            description = EXCLUDED.description,
            links = EXCLUDED.links,
            links_extra = EXCLUDED.links_extra;
        """

        execute_values(cursor, query, values)
        conn.commit()
        logging.info(f"Inserted/updated {len(values)} token profiles.")

    except Exception as e:
        logging.error(f"Error storing token profiles: {e}")
    finally:
        cursor.close()
        conn.close()
