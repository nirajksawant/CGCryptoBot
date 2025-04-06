# dexscreener_api.py

import logging
import aiohttp
from db_utils import upsert_token_profiles, upsert_token_metadata, upsert_links_extra
from utils import safe_get

TOKEN_PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

async def fetch_and_store_token_profiles():
    logging.info(f"📡 Fetching token profiles from {TOKEN_PROFILES_URL}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TOKEN_PROFILES_URL) as resp:
                if resp.status != 200:
                    logging.error(f"❌ Unexpected status code: {resp.status}")
                    return
                data = await resp.json()
                await upsert_token_profiles(data.get("tokens", []))
    except Exception as e:
        logging.error(f"❌ Error fetching token profiles: {e}")

async def fetch_and_store_token_metadata():
    # Placeholder, implemented for multiple metadata calls in future
    logging.info("ℹ️ Skipping metadata fetch (no metadata endpoint defined yet)")

async def fetch_and_store_links_extra():
    try:
        logging.info("📡 Fetching token profile links (embedded in token_profiles)")
        # Logic to extract 'links' from token_profiles and upsert
        await upsert_links_extra()
    except Exception as e:
        logging.error(f"❌ Error storing links extra: {e}")
