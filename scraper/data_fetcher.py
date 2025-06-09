from config import config
from scraper.exceptions import DataFetchError
from scraper.parser import parse_voka_json
import pandas as pd

def fetch_dumping_data(session, post_headers, date_from, date_to) -> pd.DataFrame:
    """
    Fetches dumping data from the VoKa API for particular dates.

    Args:
        session (_type_): _description_
        post_headers (_type_): _description_

    Returns:
        pd.DataFrame: Dumping data in pandas DataFrame format.
    """
    # GET for the specific dates
    date_from = date_from.replace(".", ". ") # inserts spaces after dots in dates (VoKa API bug)
    date_to = date_to.replace(".", ". ") # inserts spaces after dots in dates (VoKa API bug)
    dashboard_url = config.DASHBOARD_URL_BASE + '?fromDate=' + date_from + '&untilDate=' + date_to
    response = session.get(url=dashboard_url, headers=post_headers, allow_redirects=True)

    if response.status_code != 200:
        raise DataFetchError(f'second GET request problem, status returned {response.status_code}')

    return parse_voka_json(response.text)
