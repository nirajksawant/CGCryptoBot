
# dexscreener_orchestrator.py

import asyncio
import logging
from dexscreener_api import search_pairs
from notification_framework import filter_search_results, process_and_dispatch_alerts

logging.basicConfig(level=logging.INFO)

async def orchestrate_dexscreener_workflow():
    try:
        # Step 1: Fetch trending/search results
        logging.info("🔍 Fetching Dexscreener trending/search pairs...")
        raw_pairs = await search_pairs("")  # Can add search keyword here if needed

        # Step 2: Filter legit recent projects
        filtered_tokens = filter_search_results(raw_pairs)

        # Step 3: Process and send alerts
        process_and_dispatch_alerts(filtered_tokens)

    except Exception as e:
        logging.error(f"❌ Error in Dexscreener orchestrator: {e}")

if __name__ == "__main__":
    asyncio.run(orchestrate_dexscreener_workflow())
