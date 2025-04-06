# Module: dexscreener_ingest.py
# Purpose: This file is responsible for ingesting top tokens from dexscreener
# and storing them into the database by using methods from dexscreener_api.py

import logging
import aiohttp
from dexscreener_api import store_token_profiles

# -------------------------------------------------------------
# Fetch trending pairs/tokens from Dexscreener public endpoint
# -------------------------------------------------------------
async def fetch_dexscreener_trending():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("pairs", [])
                else:
                    logging.warning(f"Non-200 from Dex trending API: {response.status}, URL: {url}")
    except Exception as e:
        logging.warning(f"Error fetching trending pairs from {url}: {e}")
    return []

# --------------------------------------------------------
# Extract relevant token profile info from pair metadata
# --------------------------------------------------------
def extract_token_info(pair):
    try:
        base_token = pair.get("baseToken", {})
        return {
            "symbol": base_token.get("symbol"),
            "name": base_token.get("name"),
            "token_address": base_token.get("address"),
            "chain_id": pair.get("chainId"),
            "created_at": pair.get("pairCreatedAt"),
            "icon": base_token.get("icon"),
            "header": pair.get("pairName"),
            "open_graph": pair.get("url"),
            "description": "",
            "links": base_token.get("links", {})
        }
    except Exception as e:
        logging.debug(f"Error extracting token info: {e}, pair data: {pair}")
        return None

# ----------------------------------------------------------------------
# Ingest trending tokens and store profiles using store_token_profiles
# ----------------------------------------------------------------------
async def ingest_dexscreener_top_tokens():
    logging.info("Starting Dexscreener token ingestion...")

    pairs = await fetch_dexscreener_trending()
    if not pairs:
        logging.info("No pairs returned by Dexscreener API.")
        return

    # Deduplicate tokens by address
    token_profiles = []
    seen_addresses = set()

    for pair in pairs:
        token_info = extract_token_info(pair)
        if token_info and token_info["token_address"] not in seen_addresses:
            token_profiles.append(token_info)
            seen_addresses.add(token_info["token_address"])

    if not token_profiles:
        logging.info("No new unique tokens to ingest.")
        return

    await store_token_profiles(token_profiles)
    logging.info("Dexscreener ingestion complete.")
