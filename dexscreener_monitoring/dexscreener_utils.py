# dexscreener_utils.py

import logging
import aiohttp

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search"

async def fetch_token_profiles(query: str):
    """
    Queries Dexscreener API to fetch enriched token data for a given symbol or address.
    """
    try:
        logging.info(f"🌐 Querying Dexscreener for: {query}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DEXSCREENER_API}?q={query}") as response:
                if response.status != 200:
                    logging.warning(f"⚠️ Non-200 response from Dexscreener: {response.status}")
                    return []

                data = await response.json()
                pairs = data.get("pairs", [])
                enriched = []

                for pair in pairs:
                    enriched.append({
                        "symbol": pair.get("baseToken", {}).get("symbol"),
                        "dex": pair.get("dexId"),
                        "pairAddress": pair.get("pairAddress"),
                        "priceUsd": pair.get("priceUsd"),
                        "liquidity": pair.get("liquidity", {}).get("usd"),
                        "fdv": pair.get("fdv"),
                        "chain": pair.get("chainId"),
                        "url": pair.get("url"),
                    })

                return enriched

    except Exception as e:
        logging.error(f"❌ Error fetching token profiles from Dexscreener: {e}")
        return []
