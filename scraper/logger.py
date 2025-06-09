from config import config
import logging
import os

# Create logger
logger = logging.getLogger("scraper")
logger.setLevel(config.LOG_LEVEL)

# Prevent duplicate logs in some environments (like Jupyter)
logger.propagate = False

# Define formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler (already what you had)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (this is new)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(f"{log_dir}/scraper.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)