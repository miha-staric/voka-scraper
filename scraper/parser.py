from scraper.exceptions import DataFetchError
import json
import pandas as pd

def parse_voka_json(json_data) -> pd.DataFrame:
  """
  Parses and cleans dumping data from VoKa API JSON response.

  Args:
      json_data (str): JSON-formatted string returned from the VoKa API.

  Raises:
      ValueError: If the JSON is invalid or missing required keys or expected structure.

  Returns:
      pd.DataFrame: A cleaned DataFrame containing dumping data.
  """
  try:
    json_data = json.loads(json_data)
  except json.JSONDecodeError:
    raise DataFetchError('Invalid JSON response')
  if 'props' not in json_data or 'dumpings' not in json_data['props']:
    raise DataFetchError('Response JSON missing required keys "props" or "dumpings"')
  dumpings = json_data['props']['dumpings']['dumpings']
  if not isinstance(dumpings, list) or len(dumpings) == 0:
    raise DataFetchError("'dumpings' must be a non-empty list")

  # Get the "dumpings" data and convert to a DataFrame
  dumpings_df = pd.DataFrame(json_data['props']['dumpings']['dumpings'])

  # Delete the chipNumber column
  dumpings_df.drop(columns=['chipNumber'], inplace=True)

  # Fix for the error in the VoKa database
  dumpings_df['fraction'] = dumpings_df['fraction'].replace({
      'common.REST 2': 'MKO'
  })

  return dumpings_df
