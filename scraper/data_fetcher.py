from config import config
from scraper.parser import parse_json_dumping_data
from scraper.exceptions import DataFetchError
import pandas as pd

def fetch_dumping_data(session, post_headers) -> pd.DataFrame:
        # GET for the specific dates
        date_from = config.DATE_FROM.replace(".", ". ") # inserts spaces after dots in dates (VoKa API bug)
        date_to = config.DATE_TO.replace(".", ". ") # inserts spaces after dots in dates (VoKa API bug)
        dashboard_url = config.DASHBOARD_URL_BASE + '?fromDate=' + date_from + '&untilDate=' + date_to
        response = session.get(url=dashboard_url, headers=post_headers, allow_redirects=True)

        if response.status_code != 200:
                DataFetchError('second GET request problem, status returned ' + str(response.status_code))

        return parse_json_dumping_data(response.text)
