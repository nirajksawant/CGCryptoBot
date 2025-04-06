# announcement_enricher.py

import aiohttp
import logging
from datetime import datetime
from utils.dexscreener_utils import filter_search_results

DEXSCREENER_SEARCH_API = "https://api.dexscreener.com/latest/dex/search?q="

async def enrich_token_details(symbol: str) -> list:
    """
    Searches Dexscreener using the token symbol, enriches the result with trading metadata,
    filters relevant pairs, and returns a list of enriched dictionaries.
    """
    try:
        search_url = f"{DEXSCREENER_SEARCH_API}{symbol}"
        logging.info(f"🔍 Calling Dexscreener search API: {search_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    logging.error(f"❌ Failed to fetch Dexscreener data for {symbol}. Status code: {response.status}")
                    return []

                result = await response.json()
                raw_pairs = result.get("pairs", [])
                if not raw_pairs:
                    logging.warning(f"⚠️ No matching pairs found for {symbol}")
                    return []

                filtered = filter_search_results(symbol, raw_pairs)

                # Normalize results
                enriched = []
                for pair in filtered:
                    enriched.append({
                        "symbol": symbol,
                        "pair": pair.get("baseToken", {}).get("symbol") + "/" + pair.get("quoteToken", {}).get("symbol"),
                        "chain": pair.get("chainId"),
                        "dex": pair.get("dexId"),
                        "priceUsd": pair.get("priceUsd"),
                        "liquidity": pair.get("liquidity", {}).get("usd"),
                        "volume24h": pair.get("volume", {}).get("h24"),
                        "source": "dexscreener",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                logging.info(f"✅ Found {len(enriched)} relevant trading pairs for {symbol}")
                return enriched

    except Exception as e:
        logging.error(f"❌ Error enriching token {symbol}: {e}")
        return []
