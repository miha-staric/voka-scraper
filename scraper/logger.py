import logging

logger = logging.getLogger("scraper")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()  # Or use FileHandler if needed
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)