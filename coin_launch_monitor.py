import asyncio
import logging
import json
import websockets
import requests
from datetime import datetime, timedelta
from db_operations import store_coins
import time

# Load config
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as file:
    CONFIG = json.load(file)

# Configure logging
LOG_FILE = CONFIG.get("logging", {}).get("log_file", "CGcryptobot.log")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

BINANCE_WS_URL = CONFIG["api"]["binance"]["websocket_url"]
DEX_SCREENER_API_URL = CONFIG["api"]["dexscreener_url"]


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


async def fetch_new_coins_from_dex():
    """
    Fetch newly launched coins from Dex Screener API and store them.
    Filters coins launched within the last 10 minutes.
    """
    logging.info("Fetching new coins from Dex Screener...")
    try:
        response = requests.get(DEX_SCREENER_API_URL)
        logging.info(f"Dex Screener API status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            new_coins = []

            if 'pairs' in data:
                for token in data['pairs']:
                    if 'pairCreatedAt' in token:
                        timestamp = int(token['pairCreatedAt']) / 1000  # ms to s
                        created_at = datetime.fromtimestamp(timestamp)
                        if created_at >= datetime.utcnow() - timedelta(minutes=10):
                            new_coins.append({
                                "symbol": token.get("baseToken", {}).get("symbol", ""),
                                "name": token.get("baseToken", {}).get("name", ""),
                                "source": "dexscreener",
                                "created_at": created_at
                            })

            logging.info(f"Found {len(new_coins)} new coins from Dex Screener.")
            if new_coins:
                await store_coins(new_coins, "dexscreener")
        else:
            logging.error(f"Dex Screener API error: {response.status_code}")

    except Exception as e:
        logging.error(f"Error fetching from Dex Screener: {e}")


async def start_binance_websocket():
    """
    Listen to Binance WebSocket for newly listed coins and store them.
    """
    try:
        async with websockets.connect(BINANCE_WS_URL) as websocket:
            logging.info("Connected to Binance WebSocket.")
            while True:
                try:
                    time.sleep(5)
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    new_coins_data = [
                        {
                            "symbol": coin["s"],
                            "name": coin["n"],
                            "source": "binance",
                            "created_at": datetime.utcnow()
                        }
                        for coin in data if "s" in coin and "n" in coin
                    ]

                    if new_coins_data:
                        #logging.info(f"New Binance coins detected: {[c['symbol'] for c in new_coins_data]}")
                        await store_coins(new_coins_data, "binance")

                except Exception as e:
                    logging.error(f"WebSocket Error: {e}")
                    await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"Failed to connect to Binance WebSocket: {e}")


async def monitor_coins():
    """
    Run Binance WebSocket and Dex Screener polling in parallel.
    """
    async def periodic_dex_screener():
        while True:
            await fetch_new_coins_from_dex()
            await asyncio.sleep(300)  # poll every 5 minutes

    binance_task = asyncio.create_task(start_binance_websocket())
    dex_task = asyncio.create_task(periodic_dex_screener())

    try:
        await asyncio.gather(binance_task, dex_task)
    except asyncio.CancelledError:
        logging.info("Tasks cancelled.")
        binance_task.cancel()
        dex_task.cancel()
        await asyncio.gather(binance_task, dex_task, return_exceptions=True)

