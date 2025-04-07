# binance_announcement_orchestrator.py

import asyncio
import logging
import json
import os
from utils.logger import init_logger

from binance_announcement_utils import (
    fetch_latest_announcement_links,
    parse_announcement_details,
    enrich_token_details,
    filter_legit_tokens
)
# Load config
with open("config.json") as f:
    config = json.load(f)

# Initialize logging
init_logger()

async def orchestrate_binance_announcement_workflow():
    try:
        logging.info("🚀 Starting Binance announcement workflow")

        # STEP 1: Fetch latest Binance announcement links
        announcement_links = await fetch_latest_announcement_links(config=config)

        if not announcement_links:
            logging.warning("⚠️ No new Binance announcements found.")
            return

        logging.info(f"📰 Found {len(announcement_links)} potential new listings.")

        all_enriched_tokens = []

        # STEP 2: Parse each announcement to extract token symbols
        for link in announcement_links:
            try:
                token_info = await parse_announcement_details(link)
                if token_info and "symbol" in token_info:
                    symbol = token_info["symbol"]
                    logging.info(f"🔎 Extracted token symbol '{symbol}' from: {link}")

                    # STEP 3: Enrich token info from Dexscreener
                    enriched_list = await enrich_token_details(symbol)
                    for enriched in enriched_list:
                        enriched["source_announcement"] = link
                        all_enriched_tokens.append(enriched)
                else:
                    logging.warning(f"⚠️ No symbol found in announcement: {link}")
            except Exception as e:
                logging.error(f"❌ Error parsing announcement {link}: {e}")

        if not all_enriched_tokens:
            logging.info("ℹ️ No enriched token data to process.")
            return

        # STEP 4: Filter only legit-looking tokens using initial heuristics
        filtered_tokens = filter_legit_tokens(all_enriched_tokens)
        logging.info(f"✅ {len(filtered_tokens)} tokens passed legitimacy filters.")

        # STEP 5: Trigger notifications if any
        if filtered_tokens:
            logging.info(f"📢 Dispatching alerts for {len(filtered_tokens)} tokens.")
            process_and_dispatch_alerts(filtered_tokens, config=config)
        else:
            logging.info("ℹ️ No tokens passed filters. No alerts sent.")

    except Exception as e:
        logging.error(f"❌ Critical failure in Binance orchestrator: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(orchestrate_binance_announcement_workflow())
    except KeyboardInterrupt:
        logging.info("🛑 Interrupted by user")
