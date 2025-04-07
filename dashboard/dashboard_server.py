# utils/logger.py

import logging

def init_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log", mode="a", encoding="utf-8")
        ]
    )
