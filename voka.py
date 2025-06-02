# POST: https://potko.ekoplus.si/vs_uporabniki/login
# GET: https://potko.ekoplus.si/vs_uporabniki/dashboard

import json
import os
import requests
import toml
import urllib

from bs4 import BeautifulSoup

class Dumpings:
    mko_count = int(0)
    bio_count = int(0)

    def __init__(self, mko_count, bio_count):
        self.mko_count = mko_count
        self.bio_count = bio_count

    def __eq__(self, other):
        return self.mko_count == other.mko_count and \
               self.bio_count == other.bio_count

def error_report(error_message: str):
    raise Exception(error_message)

def parse_json_dumping_data(json_data, chip_card_number) -> Dumpings:
    dumpings_data = Dumpings(0, 0)
    json_data = json.loads(json_data)
    dumpings = json_data['props']['dumpings']['dumpings']
    for dumping in dumpings:
        if dumping['chipNumber'] == chip_card_number:
            if dumping['fraction'] == 'MKO':
                dumpings_data.mko_count += dumping['quantity']
            elif dumping['fraction'] == 'BIO':
                dumpings_data.bio_count += dumping['quantity']
    return dumpings_data

def parse_x_inertia_version(html_data) -> str:
    soup = BeautifulSoup(html_data, 'html.parser')
    data_page = soup.select_one('#app')['data-page']
    x_inertia_version = json.loads(data_page)['version']
    return x_inertia_version

def parse_xsrf_token(cookies) -> str:
    xsrf_token = urllib.parse.unquote(cookies['XSRF-TOKEN']) # This fixes the '%3D' encoding of '='
    return xsrf_token

def get_dumping_data() -> Dumpings:
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
        
def print_dumping_data(data, date_from, date_to):
    if data is None:
        print('No data retrieved')
        return

    print('For dates between', date_from, 'and', date_to)
    print('MKO:', data.mko_count, '\nBIO:', data.bio_count)
        
def main():
    with open('config.toml', 'r') as file:
        global config
        config = toml.load(file)
        process_config()
        data = get_dumping_data()
        print_dumping_data(data, config['dates']['date_from'], config['dates']['date_to'])

if __name__ == "__main__":
    main()