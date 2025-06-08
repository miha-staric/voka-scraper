# POST: https://potko.ekoplus.si/vs_uporabniki/login
# GET: https://potko.ekoplus.si/vs_uporabniki/dashboard

from config import config
from scraper.auth import login
from scraper.data_fetcher import fetch_dumping_data
from scraper.output import handle_default_printing, handle_months_printing, handle_years_printing
import pandas as pd

def print_dumping_data(dumping_data):
    mode = config.MODE
    dispatch = {
        'default': handle_default_printing,
        'months': handle_months_printing,
        'years': handle_years_printing
    }
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', None)
    dispatch.get(mode, handle_default_printing)(dumping_data)

def main():
        print('For dates between', config.DATE_FROM, 'and', config.DATE_TO)
        login_data = login(config.CHIP_CARD_NUMBER, config.PASSWORD, config.LOGIN_URL)
        dumping_data = fetch_dumping_data(login_data[0], login_data[1])

        if dumping_data is None:
            print('No data retrieved')
            return

        print_dumping_data(dumping_data)

if __name__ == "__main__":
    main()