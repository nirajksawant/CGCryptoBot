import asyncio
import logging
from announcement_enricher import enrich_token_details

logging.basicConfig(level=logging.INFO)

async def test_enrich(symbol: str):
    logging.info(f"🧪 Testing enrichment for symbol: {symbol}")
    enriched = await enrich_token_details(symbol)

    if not enriched:
        logging.warning("⚠️ No enriched data returned.")
    else:
        for item in enriched:
            print("🔹 Enriched Token Data:")
            for k, v in item.items():
                print(f"   {k}: {v}")
            print("-" * 40)

if __name__ == "__main__":
    # You can change this symbol to test others
    test_symbol = "PORTAL"
    asyncio.run(test_enrich(test_symbol))
