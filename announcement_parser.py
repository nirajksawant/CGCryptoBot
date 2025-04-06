# announcement_parser.py

import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CoinMonitorBot/1.0)"
}

def parse_announcement_page(url):
    """
    Parse a Binance announcement page to extract symbol, pairs, and listing time.

    Args:
        url (str): URL of the Binance announcement.

    Returns:
        dict: Parsed data like symbol, trading pairs, and listing time.
    """
    logging.info(f"🌐 Fetching announcement page: {url}")
    
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            logging.error(f"❌ Failed to fetch page. Status: {resp.status_code}")
            return {}

        soup = BeautifulSoup(resp.text, 'html.parser')

        text_content = soup.get_text(separator="\n")
        result = {
            "url": url,
            "symbol": None,
            "pairs": [],
            "listing_time": None,
            "raw": text_content[:1000]  # For debugging purpose
        }

        # Extract coin symbol (usually all caps + 3-5 letters)
        symbol_match = re.search(r"\b([A-Z]{3,5})/USDT\b", text_content)
        if symbol_match:
            result["symbol"] = symbol_match.group(1)

        # Extract all mentioned trading pairs
        pairs = re.findall(r"\b[A-Z]{3,10}/[A-Z]{2,5}\b", text_content)
        result["pairs"] = list(set(pairs))  # Unique

        # Look for listing time
        time_match = re.search(r"at\s+(\d{2}:\d{2})\s+UTC\s+on\s+(\w+\s\d{1,2},\s\d{4})", text_content)
        if time_match:
            result["listing_time"] = f"{time_match.group(2)} {time_match.group(1)} UTC"

        logging.info(f"✅ Parsed announcement: {result}")
        return result

    except Exception as e:
        logging.error(f"❌ Error parsing announcement page: {e}")
        return {}
