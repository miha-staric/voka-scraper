# POST: https://potko.ekoplus.si/vs_uporabniki/login
# GET: https://potko.ekoplus.si/vs_uporabniki/dashboard

from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import requests
import toml
import urllib

def error_report(error_message: str):
    raise Exception(error_message)

def parse_json_dumping_data(json_data, chip_card_number) -> pd.DataFrame:
    json_data = json.loads(json_data)

    # Get the "dumpings" data and convert to a DataFrame
    dumpings_df = pd.DataFrame(json_data['props']['dumpings']['dumpings'])

    # Get the "dumpings" data and convert to a DataFrame
    dumpings_df = pd.DataFrame(json_data['props']['dumpings']['dumpings'])

    return dumpings_df

def parse_x_inertia_version(html_data) -> str:
    soup = BeautifulSoup(html_data, 'html.parser')
    data_page = soup.select_one('#app')['data-page']
    x_inertia_version = json.loads(data_page)['version']
    return x_inertia_version

def parse_xsrf_token(cookies) -> str:
    xsrf_token = urllib.parse.unquote(cookies['XSRF-TOKEN']) # This fixes the '%3D' encoding of '='
    return xsrf_token

def get_dumping_data() -> pd.DataFrame:
    post_headers = {
        'X-Inertia': 'true',
        'X-Inertia-Version': '',
    }

    payload = {
        'chipCardNumber': config['card']['chip_card_number'],
        'password': config['card']['password']
    }

    with requests.Session() as session:
        # GET page first to acquire the XSRF-TOKEN and X-Inertia-Version values for the subsequent headers
        response = session.get(url=config['server']['login_url'], allow_redirects=True)

        if response.status_code != 200:
            error_report('first GET request problem, status returned ' + str(response.status_code))

        x_inertia_version = parse_x_inertia_version(response.content)
        xsrf_token = parse_xsrf_token(response.cookies)

        post_headers['X-Inertia-Version'] = x_inertia_version
        post_headers['X-XSRF-TOKEN'] = xsrf_token

        # POST now with cookies from the GET request
        response = session.post(url=config['server']['login_url'], json=payload, headers=post_headers, allow_redirects=True)

        if response.status_code != 200:
            error_report('POST request problem, status returned ' + str(response.status_code))

        # GET for the specific dates
        dashboard_url = config['server']['dashboard_url_base'] + '?fromDate=' + config['dates']['date_from'] + '&untilDate=' + config['dates']['date_to']
        response = session.get(url=dashboard_url, headers=post_headers, allow_redirects=True)

        if response.status_code != 200:
            error_report('second GET request problem, status returned ' + str(response.status_code))

    return parse_json_dumping_data(response.text, config['card']['chip_card_number'])

def process_config():
    # Override with env vars if present
    config['dates']['date_from'] = os.getenv('date_from', config['dates']['date_from'])
    config['dates']['date_to'] = os.getenv('date_to', config['dates']['date_to'])
    config['card']['chip_card_number'] = os.getenv('chip_card_number', config['card']['chip_card_number'])
    config['card']['password'] = os.getenv('password', config['card']['password'])

    # Insert spaces after dots in dates (silly API developers)
    config['dates']['date_from'] = config['dates']['date_from'].replace(".", ". ")
    config['dates']['date_to'] = config['dates']['date_to'].replace(".", ". ")

def main():
    with open('config.toml', 'r') as file:
        global config
        config = toml.load(file)

        print('For dates between', config['dates']['date_from'], 'and', config['dates']['date_to'])
        print('\n')

        process_config()
        dumping_data = get_dumping_data()

        if dumping_data is None:
            print('No data retrieved')
            return

        print('Full data:')
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_columns', None)
        print(dumping_data)

        print('\nSummarized data:')
        pivot_summary = dumping_data.pivot_table(
            values='quantity',
            index=None,
            columns='fraction',
            aggfunc='sum',
            fill_value=0
        )
        print(pivot_summary)

if __name__ == "__main__":
    main()
