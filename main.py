# main.py

import asyncio
import logging
import json
import signal
import sys
from orchestrators.dexscreener_orchestrator import run_dexscreener_pipeline
from orchestrators.binance_orchestrator import run_binance_pipeline
from utils.logger import init_logger
from dashboard.dashboard_server import start_dashboard_server

# Load config
with open("config.json") as f:
    config = json.load(f)

# Initialize logging
init_logger()

# Handle graceful shutdown
def handle_sigint(signal, frame):
    logging.info("🛑 Keyboard interrupt received. Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

async def main():
    logging.info("🚀 Starting Crypto Monitor System")

    # Start dashboard in background
    dashboard_task = asyncio.create_task(start_dashboard_server())

    # Start Binance + Dexscreener pipelines concurrently
    await asyncio.gather(
        run_dexscreener_pipeline(config=config),
        run_binance_pipeline(config=config),
        dashboard_task
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Interrupted by user")
    except Exception as e:
        logging.error(f"❌ Unhandled exception: {e}")
