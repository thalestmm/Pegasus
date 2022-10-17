import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

from pprint import pprint

from googleapiclient import discovery
from google.oauth2 import service_account

import json


class SheetsConnection:
    sheet_id: str
    sheet_name: str

    def __init__(self, sheet_id: str, sheet_name: str):
        self.sheet_id   = sheet_id
        self.sheet_name = sheet_name

    def connect(self):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        SPREADSHEET_ID = self.sheet_id
        SHEET_NAME = self.sheet_name
        GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

        file = open('credentials.json')
        info = json.load(file)['web']

        info['client_email'] = 'meier.thales@gmail.com'

        # print(info['web'])

        credentials = service_account.Credentials.from_service_account_info(info=info)

        service = discovery.build('sheets', 'v4', credentials=credentials)

        # The ID of the spreadsheet to retrieve data from.
        spreadsheet_id = self.sheet_id  # TODO: Update placeholder value.

        # The A1 notation of the values to retrieve.
        range_ = self.sheet_name  # TODO: Update placeholder value.

        # How values should be represented in the output.
        # The default render option is ValueRenderOption.FORMATTED_VALUE.
        value_render_option = ''  # TODO: Update placeholder value.

        # How dates, times, and durations should be represented in the output.
        # This is ignored if value_render_option is
        # FORMATTED_VALUE.
        # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
        date_time_render_option = ''  # TODO: Update placeholder value.

        request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
        response = request.execute()

        # TODO: Change code below to process the `response` dict:
        pprint(response)


if __name__ == "__main__":
    ranking_id = "1dohhVTDsUTXYb-K4EsFFHtT-3NRTW-3YB3QlMUmal9I"
    sc = SheetsConnection(sheet_id=ranking_id,sheet_name='pilotos')
    sc.connect()
