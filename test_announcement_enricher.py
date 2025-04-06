# test_announcement_enricher.py

import asyncio
from announcement_enricher import enrich_token_details

# Example test symbol (use real new listing symbol)
TEST_SYMBOL = "ALT"

async def main():
    results = await enrich_token_details(TEST_SYMBOL)
    print(f"\n🔬 Enriched Results for '{TEST_SYMBOL}':")
    for res in results:
        print(res)

if __name__ == "__main__":
    asyncio.run(main())
