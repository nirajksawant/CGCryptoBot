# binance_announcement_utils.py

import logging
import re
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from collectors.dexscreener_collector import fetch_token_profiles

BINANCE_ANNOUNCEMENT_RSS = "https://www.binance.com/en/support/announcement/rss"

async def fetch_latest_announcement_links():
    """
    Fetches new listing announcement links from Binance RSS feed.
    """
    try:
        logging.info("📡 Fetching Binance announcements RSS...")
        feed = feedparser.parse(BINANCE_ANNOUNCEMENT_RSS)

        links = []
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            if "Will List" in title:
                logging.debug(f"🧲 Matched listing title: {title}")
                links.append(link)

        logging.info(f"✅ Found {len(links)} potential listing announcements")
        return links

    except Exception as e:
        logging.error(f"❌ Error fetching Binance announcements: {e}")
        return []


async def parse_announcement_details(url):
    """
    Parses the token symbol from the Binance listing announcement page.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.warning(f"⚠️ Non-200 response while parsing {url}: {response.status}")
                    return {}

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                title_tag = soup.find("title")

                if title_tag:
                    title = title_tag.text
                    logging.debug(f"🔍 Parsing title: {title}")
                    match = re.search(r'Binance Will List\s+([A-Z0-9]+)', title)
                    if match:
                        symbol = match.group(1)
                        return {"symbol": symbol, "url": url}
                    else:
                        logging.warning(f"⚠️ Symbol not found in title: {title}")
                else:
                    logging.warning("⚠️ Title tag not found in HTML")

        return {}

    except Exception as e:
        logging.error(f"❌ Error parsing announcement URL {url}: {e}")
        return {}


async def enrich_token_details(symbol):
    """
    Enrich token with details from Dexscreener.
    """
    try:
        logging.info(f"🧠 Enriching token: {symbol} using Dexscreener")
        enriched_tokens = await fetch_token_profiles(query=symbol)
        logging.info(f"✅ Found {len(enriched_tokens)} tokens enriched for {symbol}")
        return enriched_tokens

    except Exception as e:
        logging.error(f"❌ Error enriching token {symbol}: {e}")
        return []


def filter_legit_tokens(token_list):
    """
    Apply rough filters to exclude obvious scams. This is just framework.
    """
    try:
        logging.info("🔍 Filtering legit tokens from enriched list")
        filtered = []

        for token in token_list:
            if token.get("fdv") and token["fdv"] > 1_000_000 and token.get("liquidity") > 5000:
                filtered.append(token)
            else:
                logging.debug(f"🧹 Skipped token: {token.get('symbol')} due to weak metrics")

        return filtered

    except Exception as e:
        logging.error(f"❌ Error filtering legit tokens: {e}")
        return []
