import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client(credentials_file: str):
    creds = Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def get_worksheet(
    spreadsheet_id: str,
    worksheet_name: str,
    credentials_file: str
):
    client = get_client(credentials_file)
    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=20
        )

    return worksheet

def append_rows(worksheet, rows: list, header: list, dedup_key: str = "url"):
    """
    rows: list[dict]
    header: ordered list of column names
    dedup_key: column name used to avoid duplicates
    """

    existing_values = worksheet.get_all_values()

    # --- Header handling ---
    if not existing_values:
        worksheet.append_row(header)
        existing_urls = set()
    else:
        first_row = existing_values[0]
        if first_row != header:
            raise ValueError(
                "Header mismatch detected in Google Sheet. "
                "Refusing to append rows."
            )

        # --- Read existing URLs (column index) ---
        try:
            url_col_idx = header.index(dedup_key)
        except ValueError:
            raise ValueError(f"Dedup key '{dedup_key}' not found in header")

        existing_urls = {
            row[url_col_idx]
            for row in existing_values[1:]
            if len(row) > url_col_idx and row[url_col_idx]
        }

    # --- Filter new rows ---
    values = []
    new_count = 0

    for r in rows:
        url = r.get(dedup_key, "")
        if not url or url in existing_urls:
            continue

        values.append([r.get(h, "") for h in header])
        existing_urls.add(url)
        new_count += 1

    if values:
        worksheet.append_rows(values, value_input_option="RAW")

    print(f"🟢 Appended {new_count} new rows (deduplicated)")
