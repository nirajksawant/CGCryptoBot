# File: tests/test_token_profiles.py

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN_PROFILE_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

async def test_fetch_token_profiles():
    logging.info(f"Testing Dexscreener token profiles from {TOKEN_PROFILE_URL}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TOKEN_PROFILE_URL) as resp:
                if resp.status != 200:
                    logging.error(f"❌ Unexpected status code: {resp.status}")
                    return
                data = await resp.json()
                if not isinstance(data, list):
                    logging.error("❌ Unexpected data structure. Expected a list.")
                    return
                logging.info(f"✅ Total token profiles received: {len(data)}")
                if data:
                    logging.debug(f"Sample profile:\n{data[0]}")
    except Exception as e:
        logging.error(f"❌ Error testing token profiles: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch_token_profiles())
