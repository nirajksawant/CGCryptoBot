import asyncio
import logging
import json
from flask import Flask, jsonify
from threading import Thread
from coin_launch_monitor import monitor_coins
from db_operations import connect_db

# Load configuration
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as file:
    CONFIG = json.load(file)

LOG_FILE = CONFIG.get("logging", {}).get("log_file", "CGcryptobot.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__)

@app.route('/coins', methods=['GET'])
def get_coins():
    """Retrieve stored coins from the database and return as JSON."""
    conn = connect_db()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT symbol, name, source, created_at FROM coins ORDER BY created_at DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([
        {"symbol": row[0], "name": row[1], "source": row[2], "created_at": row[3]}
        for row in rows
    ])


def run_flask():
    """Run the Flask app in a separate thread."""
    app.run(debug=False, port=5000)


async def main():
    # Start Flask dashboard in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run the async coin monitoring loop
    await monitor_coins()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Exiting gracefully...")