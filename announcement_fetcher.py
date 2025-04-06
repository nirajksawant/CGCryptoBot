# announcement_fetcher.py

import feedparser
import logging
from datetime import datetime
import re

BINANCE_RSS_FEED = "https://www.binance.com/en/support/announcement/rss"

# Keywords that usually indicate new listings
LISTING_KEYWORDS = ["will list", "lists", "Binance listing", "listed on Binance"]

# Setup logging
logging.basicConfig(level=logging.INFO)


def fetch_rss_announcements():
    """
    Fetch and parse announcements from Binance RSS feed.

    Returns:
        List of dicts with title, link, and published date for listing-related announcements.
    """
    logging.info(f"📡 Fetching Binance RSS feed from {BINANCE_RSS_FEED}")
    try:
        feed = feedparser.parse(BINANCE_RSS_FEED)

        if feed.bozo:
            logging.error(f"❌ Error parsing RSS feed: {feed.bozo_exception}")
            return []

        new_listings = []

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            published = entry.get("published", "")
            published_dt = None

            try:
                published_dt = datetime(*entry.published_parsed[:6])
            except Exception as e:
                logging.warning(f"⚠️ Failed to parse publish date for entry: {title}")

            if any(keyword.lower() in title.lower() for keyword in LISTING_KEYWORDS):
                logging.info(f"🆕 New listing found: {title}")
                new_listings.append({
                    "title": title,
                    "link": link,
                    "published": published_dt
                })

        logging.info(f"✅ Total new listings found: {len(new_listings)}")
        return new_listings

    except Exception as e:
        logging.error(f"❌ Exception while fetching RSS feed: {e}")
        return []
