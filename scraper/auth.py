from bs4 import BeautifulSoup
from scraper.exceptions import AuthenticationError
import json
import requests
import urllib

def parse_x_inertia_version(html_data) -> str:
    soup = BeautifulSoup(html_data, 'html.parser')
    data_page = soup.select_one('#app')['data-page']
    x_inertia_version = json.loads(data_page)['version']
    return x_inertia_version

def parse_xsrf_token(cookies) -> str:
    xsrf_token = urllib.parse.unquote(cookies['XSRF-TOKEN']) # This fixes the '%3D' encoding of '='
    return xsrf_token

def login(chip_card_number: str, password: str, login_url: str) -> requests.Session:
    post_headers = {
        'X-Inertia': 'true',
        'X-Inertia-Version': '',
    }
    payload = {
        'chipCardNumber': chip_card_number,
        'password': password
    }

    with requests.Session() as session:
        # GET page first to acquire the XSRF-TOKEN and X-Inertia-Version values for the subsequent headers
        response = session.get(url=login_url, allow_redirects=True)

        if response.status_code != 200:
            AuthenticationError('first GET request problem, status returned ' + str(response.status_code))

        x_inertia_version = parse_x_inertia_version(response.content)
        xsrf_token = parse_xsrf_token(response.cookies)

        post_headers['X-Inertia-Version'] = x_inertia_version
        post_headers['X-XSRF-TOKEN'] = xsrf_token

        # POST now with cookies from the GET request
        response = session.post(url=login_url, json=payload, headers=post_headers, allow_redirects=True)

        if response.status_code != 200:
            AuthenticationError('POST request problem, status returned ' + str(response.status_code))

        return session, post_headers