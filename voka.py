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

def parse_json_dumping_data(json_data) -> pd.DataFrame:
    try:
      json_data = json.loads(json_data)
    except json.JSONDecodeError:
      raise ValueError("Invalid JSON response")
    if 'props' not in json_data or 'dumpings' not in json_data['props']:
      raise ValueError("Response JSON missing required keys 'props' or 'dumpings'")
    dumpings = json_data['props']['dumpings']['dumpings']
    if not isinstance(dumpings, list) or len(dumpings) == 0:
      raise ValueError("'dumpings' must be a non-empty list")

    # Get the "dumpings" data and convert to a DataFrame
    dumpings_df = pd.DataFrame(json_data['props']['dumpings']['dumpings'])

    # Delete the chipNumber column
    dumpings_df.drop(columns=['chipNumber'], inplace=True)

    # Fix for the error in the VoKa database
    dumpings_df['fraction'] = dumpings_df['fraction'].replace({
        'common.REST 2': 'MKO'
    })

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

    return parse_json_dumping_data(response.text)

def process_config():
    # Override with env vars if present
    config['dates']['date_from'] = os.getenv('date_from', config['dates']['date_from'])
    config['dates']['date_to'] = os.getenv('date_to', config['dates']['date_to'])
    config['card']['chip_card_number'] = os.getenv('chip_card_number', config['card']['chip_card_number'])
    config['card']['password'] = os.getenv('password', config['card']['password'])
    config['output']['mode'] = os.getenv('mode', config['output']['mode'])
    config['cost']['bio'] = os.getenv('bio', config['cost']['bio'])
    config['cost']['mko'] = os.getenv('mko', config['cost']['mko'])
    config['cost']['min_bio'] = os.getenv('min_bio', config['cost']['min_bio'])
    config['cost']['min_mko'] = os.getenv('min_mko', config['cost']['min_mko'])

    # Insert spaces after dots in dates (silly API developers)
    config['dates']['date_from'] = config['dates']['date_from'].replace(".", ". ")
    config['dates']['date_to'] = config['dates']['date_to'].replace(".", ". ")

def handle_months_printing(dumping_data):
    dumping_data['dumpedAtDate'] = pd.to_datetime(dumping_data['dumpedAtDate'])
    dumping_data['month'] = dumping_data['dumpedAtDate'].dt.to_period('M').astype(str)

    # Group by month and fraction summing quantity
    grouped = dumping_data.groupby(['month', 'fraction']).agg(
        quantity=('quantity', 'sum')
    ).reset_index()

    # Ensure every month has both fractions present
    months = grouped['month'].unique()
    fractions = ['BIO', 'MKO']

    # Create full index as cartesian product of months x fractions
    full_index = pd.MultiIndex.from_product([months, fractions], names=['month', 'fraction'])

    # Reindex grouped DataFrame to full index, filling missing quantities with 0
    grouped = grouped.set_index(['month', 'fraction']).reindex(full_index, fill_value=0).reset_index()

    # Costs map from config
    cost_map = {
        'BIO': float(config['cost']['bio']),
        'MKO': float(config['cost']['mko'])
    }

    # Calculate real cost per fraction per row
    grouped['real_cost_fraction'] = grouped.apply(
        lambda row: row['quantity'] * cost_map.get(row['fraction'], 0),
        axis=1
    )

    # Minimum cost thresholds
    min_costs = {
        'BIO': float(config['cost']['min_bio']),
        'MKO': float(config['cost']['min_mko'])
    }

    # Apply minimum cost per fraction per row
    grouped['total_cost_fraction'] = grouped.apply(
        lambda row: max(row['real_cost_fraction'], min_costs.get(row['fraction'], 0)),
        axis=1
    )

    # Sum costs by month
    real_costs = grouped.groupby('month')['real_cost_fraction'].sum().reset_index(name='real_cost')
    total_costs = grouped.groupby('month')['total_cost_fraction'].sum().reset_index(name='total_cost')

    # Pivot quantities to columns BIO and MKO as integers
    quantities = grouped.pivot_table(
        index='month', columns='fraction', values='quantity', aggfunc='sum', fill_value=0
    ).reset_index()
    quantities[['BIO', 'MKO']] = quantities[['BIO', 'MKO']].astype(int)

    # Merge quantities with cost summaries
    final_df = pd.merge(quantities, real_costs, on='month')
    final_df = pd.merge(final_df, total_costs, on='month')

    print('Months data:')
    print(final_df)

def compute_total_cost(group):
    min_costs = {'BIO': config['cost']['min_bio'], 'MKO': config['cost']['min_mko']}
    total = 0
    for frac in ['BIO', 'MKO']:
        qty = group[group['fraction'] == frac]['quantity'].sum()
        cost = group[group['fraction'] == frac]['cost'].max()  # Use actual cost if higher
        cost = max(cost, min_costs[frac])  # Enforce minimum
        total += qty * cost
    return total

def handle_years_printing(dumping_data):
    # Ensure date column is datetime
    dumping_data['dumpedAtDate'] = pd.to_datetime(dumping_data['dumpedAtDate'])
    
    # Extract year period as string
    dumping_data['year'] = dumping_data['dumpedAtDate'].dt.to_period('Y').astype(str)
    
    # Group by year and fraction and sum quantities
    yearly_summary = dumping_data.groupby(['year', 'fraction'])['quantity'].sum().reset_index()
    
    # Pivot so fractions become columns, fill missing with 0
    pivot = yearly_summary.pivot_table(
        index='year',
        columns='fraction',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Optional: convert quantity columns to int if all values are integer-like
    for col in ['BIO', 'MKO']:
        if col in pivot.columns:
            pivot[col] = pivot[col].astype(int)
        else:
            # If a fraction column is missing (e.g. no MKO data), add it with zeros
            pivot[col] = 0

    pivot.columns.name = None
    print("Years data:")
    print(pivot)

def handle_default_printing(dumping_data):
    print('Full data:')
    print(dumping_data)

    print('Summarized data:')
    pivot_summary = dumping_data.pivot_table(
        values='quantity',
        index=None,
        columns='fraction',
        aggfunc='sum',
        fill_value=0
    )
    print(pivot_summary)

def print_dumping_data(dumping_data):
    mode = config['output']['mode']
    dispatch = {
        'default': handle_default_printing,
        'months': handle_months_printing,
        'years': handle_years_printing
    }
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', None)
    dispatch.get(mode, handle_default_printing)(dumping_data)

def main():
    with open('config.toml', 'r') as file:
        global config
        config = toml.load(file)

        print('For dates between', config['dates']['date_from'], 'and', config['dates']['date_to'])

        process_config()
        dumping_data = get_dumping_data()

        if dumping_data is None:
            print('No data retrieved')
            return

        print_dumping_data(dumping_data)

if __name__ == "__main__":
    main()
