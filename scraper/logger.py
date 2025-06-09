from config import config
import logging
import os

# Create logger
logger = logging.getLogger("scraper")
logger.setLevel(config.LOG_LEVEL)
logger.propagate = False
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(f"{log_dir}/scraper.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)