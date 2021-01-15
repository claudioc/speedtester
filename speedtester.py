#!/usr/bin/env python3

import pickle
import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import subprocess
import speedtest
from dotenv import load_dotenv
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = os.getenv('SPEEDT_SPREADSHEET_ID')
range_append_from = os.getenv('SPEEDT_RANGE_APPEND_FROM')
google_client_id = os.getenv('SPEEDT_GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('SPEEDT_GOOGLE_CLIENT_SECRET')

credentials = {
    "installed": {
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}


def main():
    """
    Run the speedtests and write the results down in
    a google spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Check if the Spreadsheet is "initialized" with the headers
    request = sheet.values().get(spreadsheetId=spreadsheet_id, range='A1')
    header = request.execute()
    if 'values' not in header or header['values'][0][0] != 'Timestamp':
        body = {
            'values': [
                [
                    'Timestamp',
                    'Ping',
                    'Download',
                    'Upload',
                    'ISP'
                ]
            ]
        }
        sheet.values().append(
            range='A1',
            spreadsheetId=spreadsheet_id,
            valueInputOption='USER_ENTERED',
            body=body).execute()

    # If you want to use a single threaded test, use st_threads = 1
    st_threads = None
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download(threads=st_threads)
    s.upload(threads=st_threads)
    test_result = s.results.dict()

    body = {
        'values': [
            [
                test_result['timestamp'],
                round(test_result['ping']),
                round(test_result['download'] / 1000000, 2),
                round(test_result['upload'] / 1000000, 2),
                test_result['client']['isp']
            ]
        ]
    }

    result = sheet.values().append(
        range=range_append_from,
        spreadsheetId=spreadsheet_id,
        valueInputOption='USER_ENTERED',
        body=body).execute()


if __name__ == '__main__':
    main()
