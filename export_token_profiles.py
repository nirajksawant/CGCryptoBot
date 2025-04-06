# Module: export.py
# Purpose: Export token profiles to JSON, potentially for dashboard or external services.

import json
import logging
import os
import psycopg2
from datetime import datetime

EXPORT_PATH = "exports/token_profiles.json"

# --------------------------------------------------------
# Connect to PostgreSQL (adjust connection params as needed)
# --------------------------------------------------------
def connect_db():
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME", "coins_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432)
        )
    except Exception as e:
        logging.error(f"Failed to connect to DB: {e}")
        return None

# --------------------------------------------------------
# Export all token profiles to a JSON file
# --------------------------------------------------------
def export_token_profiles_to_json():
    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, name, chain_id, token_address, created_at, icon, header, open_graph, description, links, links_extra FROM token_profiles")
        rows = cursor.fetchall()

        keys = [desc[0] for desc in cursor.description]
        result = [dict(zip(keys, row)) for row in rows]

        # Convert datetime and JSON fields properly
        for entry in result:
            if isinstance(entry["created_at"], datetime):
                entry["created_at"] = entry["created_at"].isoformat()
            if isinstance(entry.get("links"), str):
                try:
                    entry["links"] = json.loads(entry["links"])
                except:
                    pass
            if isinstance(entry.get("links_extra"), str):
                try:
                    entry["links_extra"] = json.loads(entry["links_extra"])
                except:
                    pass

        os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
        with open(EXPORT_PATH, "w") as f:
            json.dump(result, f, indent=2)

        logging.info(f"Exported {len(result)} token profiles to {EXPORT_PATH}")

    except Exception as e:
        logging.error(f"Error exporting token profiles: {e}")
    finally:
        cursor.close()
        conn.close()
