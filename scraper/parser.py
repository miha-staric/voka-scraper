import json
import pandas as pd

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
