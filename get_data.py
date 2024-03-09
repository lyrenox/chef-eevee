# Pokemon Cafe Remix database by TalonMallon
# https://docs.google.com/spreadsheets/d/1SxDpFfGX6VsFucnUyCf8rcw_puSOWGK8EBw3aHHEj5s

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json

def get_values(spreadsheet_id, range_name):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    """
    creds = Credentials.from_authorized_user_file("token.json") 
    # To get your own token, see instructions on https://developers.google.com/sheets/api/quickstart/python
    try:
        service = build("sheets", "v4", credentials=creds)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f'{len(rows)} rows retrieved')
        return result
    except HttpError as error:
        print(f'An error occurred: {error}')
        return error


if __name__ == "__main__":
    # Pass: spreadsheet_id, and range_name
    data = get_values('1SxDpFfGX6VsFucnUyCf8rcw_puSOWGK8EBw3aHHEj5s', 'A:R')['values']
    # Convert data into a dictionary list
    pkmn = []
    for row in data[1:]: # Ignore the first row, i.e. column names
        try:
            pkmn.append({
                    'name_en': row[4], # column 5 aka. column E
                    'dex_number': row[1],
                    'costume_id': row[2],
                    'type': row[3],
                    'date_added': row[0],
                    'obtain_method': row[5],
                    'date_end': row[7],
                    'specialty': row[8],
                    'base_score': row[9],
                    'score_increase': row[10],
                    'ol_bonus': row[11],
                    'gimmicks': (row[12], row[13], row[14], row[15]),
                    'score_plus': (row[16], row[17])
                })
        except Exception as error:
            print(f'An error occured: {error}')
    print(f'{len(pkmn)} entries created')
    
    with open('pkmn.json', 'w') as outfile: # Convert and write JSON object to file
        json.dump(pkmn, outfile)
        outfile.close()
        print('Updated pkmn.json')
