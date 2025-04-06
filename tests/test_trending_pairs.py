# File: tests/test_trending_pairs.py

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.DEBUG)

DEX_TRENDING_URL = "https://api.dexscreener.com/latest/dex/pairs"

async def test_fetch_trending_pairs():
    logging.info(f"Testing Dexscreener trending pairs from {DEX_TRENDING_URL}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DEX_TRENDING_URL) as resp:
                if resp.status != 200:
                    logging.error(f"Unexpected status code: {resp.status}")
                    return
                data = await resp.json()
                pairs = data.get("pairs", [])
                logging.info(f"✅ Total pairs received: {len(pairs)}")
                if pairs:
                    logging.debug(f"Sample pair:\n{pairs[0]}")
    except Exception as e:
        logging.error(f"❌ Error testing trending pairs: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch_trending_pairs())
