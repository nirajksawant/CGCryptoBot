# binance_announcement_orchestrator.py

import asyncio
import logging
from announcement_monitor import fetch_latest_announcement_links
from announcement_parser import parse_announcement_details
from announcement_enricher import enrich_token_details
from notification_framework import process_and_dispatch_alerts
from notification_filtering import filter_legit_tokens

logging.basicConfig(level=logging.INFO)

async def orchestrate_binance_announcement_workflow():
    try:
        logging.info("🚀 Starting Binance announcement workflow...")

        # Step 1: Fetch new Binance listing announcements
        announcement_links = await fetch_latest_announcement_links()
        logging.info(f"📰 Fetched {len(announcement_links)} announcement links")

        all_enriched_tokens = []

        # Step 2: Parse each announcement link to extract token symbol
        for link in announcement_links:
            token_info = await parse_announcement_details(link)
            if token_info and "symbol" in token_info:
                symbol = token_info["symbol"]
                logging.info(f"🔎 Extracted token symbol: {symbol} from {link}")

                # Step 3: Enrich details via Dexscreener
                enriched_data = await enrich_token_details(symbol)
                for enriched in enriched_data:
                    enriched["source_announcement"] = link  # Track source
                    all_enriched_tokens.append(enriched)
            else:
                logging.warning(f"⚠️ Could not extract token info from: {link}")

        # Step 4: Filter legit-looking tokens
        filtered_tokens = filter_legit_tokens(all_enriched_tokens)
        logging.info(f"✅ {len(filtered_tokens)} tokens passed legitimacy filter")

        # Step 5: Alert users via notification framework
        if filtered_tokens:
            logging.info(f"📢 Sending alerts for {len(filtered_tokens)} legit tokens")
            process_and_dispatch_alerts(filtered_tokens)
        else:
            logging.info("ℹ️ No legit new tokens to alert.")

    except Exception as e:
        logging.error(f"❌ Error in Binance orchestrator: {e}")

if __name__ == "__main__":
    asyncio.run(orchestrate_binance_announcement_workflow())
