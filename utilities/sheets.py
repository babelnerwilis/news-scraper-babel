import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

FIELDNAMES = [
    "day",
    "publication_datetime",
    "category",
    "title",
    "url",
    "tags",
    "total_pages",
    "content"
]

def get_worksheet(spreadsheet_name, worksheet_name):
    creds_json = os.environ["GOOGLE_SERVICE_JSON"]
    creds_dict = json.loads(creds_json)

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    gc = gspread.authorize(creds)
    sh = gc.open(spreadsheet_name)

    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=1, cols=len(FIELDNAMES))
        ws.append_row(FIELDNAMES)

    return ws

def get_existing_urls(ws):
    try:
        return set(ws.col_values(5)[1:])  # url column
    except Exception:
        return set()

def append_row(ws, row_dict):
    ws.append_row(
        [row_dict[f] for f in FIELDNAMES],
        value_input_option="RAW"
    )

