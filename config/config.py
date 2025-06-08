import os
import toml

# Load configuration from file
with open('config.toml', 'r') as file:
        config = toml.load(file)

# Override with env vars if present 
DATE_FROM = os.getenv('date_from', config['dates']['date_from'])
DATE_TO = os.getenv('date_to', config['dates']['date_to'])
CHIP_CARD_NUMBER = os.getenv('chip_card_number', config['card']['chip_card_number'])
PASSWORD = os.getenv('password', config['card']['password'])
MODE = os.getenv('mode', config['output']['mode'])
BIO = os.getenv('bio', config['cost']['bio'])
MKO = os.getenv('mko', config['cost']['mko'])
MIN_BIO = os.getenv('min_bio', config['cost']['min_bio'])
MIN_MKO = os.getenv('min_mko', config['cost']['min_mko'])
LOGIN_URL = config['server']['login_url']
DASHBOARD_URL_BASE = config['server']['dashboard_url_base']