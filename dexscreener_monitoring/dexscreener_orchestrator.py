# dexscreener_orchestrator.py

import asyncio
import logging
from dexscreener_utils import fetch_token_profiles
from notification_filtering import filter_legit_tokens
from notification_framework import process_and_dispatch_alerts

logging.basicConfig(level=logging.INFO)

async def orchestrate_dexscreener_discovery(symbols):
    try:
        logging.info("🚀 Starting Dexscreener discovery workflow...")

        all_profiles = []

        for symbol in symbols:
            profiles = await fetch_token_profiles(symbol)
            if profiles:
                all_profiles.extend(profiles)
            else:
                logging.info(f"ℹ️ No profiles found for {symbol}")

        # Filter legit tokens
        legit_tokens = filter_legit_tokens(all_profiles)
        logging.info(f"✅ {len(legit_tokens)} legit tokens identified")

        # Send notifications
        if legit_tokens:
            logging.info(f"📢 Sending alerts for {len(legit_tokens)} legit tokens")
            process_and_dispatch_alerts(legit_tokens)
        else:
            logging.info("ℹ️ No legit tokens to notify.")

    except Exception as e:
        logging.error(f"❌ Error in Dexscreener orchestrator: {e}")

if __name__ == "__main__":
    test_symbols = ["DOGE", "ETH", "ABC123"]  # Replace with real inputs or CLI args
    asyncio.run(orchestrate_dexscreener_discovery(test_symbols))
