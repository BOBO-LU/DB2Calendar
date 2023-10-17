from __future__ import print_function
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_sheet_id_by_name(spreadsheet_id, sheet_name, credentials):
    """Retrieve the sheetId for a given sheet name.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_name (str): The name of the sheet.
        credentials (object): OAuth2 credentials for accessing the API.

    Returns:
        int: The sheetId of the sheet. None if the sheet name doesn't exist.
    """
    service = build('sheets', 'v4', credentials=credentials)

    # Fetch the spreadsheet details
    spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet_metadata.get('sheets', '')

    # Iterate over sheets to find the matching sheet name and return its sheetId
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


def append_rows(spreadsheet_id, sheet_id, creds, length):
    """Append empty rows to a specific sheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_id (int): The sheetId of the target sheet.
        num_rows (int): The number of rows to append.
        credentials (object): OAuth2 credentials for accessing the API.
    """
    
    service = build('sheets', 'v4', credentials=creds)

    # Prepare the request body
    body = {
        'requests': [{
            'appendDimension': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'length': length
            }
        }]
    }

    # Make the request to append the rows
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    return response



def delete_rows(spreadsheet_id, sheet_id, start_row, end_row, credentials):
    """Delete rows in a specific Google Sheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_name (str): The name of the sheet from which rows should be deleted.
        start_row (int): The start row index to delete (0-based).
        end_row (int): The end row index to delete (0-based).
        credentials (object): OAuth2 credentials for accessing the API.
    """
    service = build('sheets', 'v4', credentials=credentials)

    # Create the delete request
    body = {
        'requests': [{
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': start_row,
                    'endIndex': end_row + 1
                }
            }
        }]
    }

    # Send the delete request
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print(f"Deleted rows from {start_row} to {end_row} in {sheet_name}.")
    return response

    

def create_sheet(spreadsheet_id, sheet_name, creds):
    service = build('sheets', 'v4', credentials=creds)

    # Request body for adding a new sheet
    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_name
                }
            }
        }]
    }

    # Make the request to add the new sheet
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    return response


def sheet_exists(spreadsheet_id, sheet_name, creds):
    service = build('sheets', 'v4', credentials=creds)

    # Fetch the spreadsheet details
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id).execute()

    # Check for the existence of the sheet by its name
    for sheet in spreadsheet.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return True
    return False


def get_values(spreadsheet_id, range_name, creds):

    try:
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)} rows retrieved by get_values.")
        # print(rows)
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def batch_get_values(spreadsheet_id, range_names, creds):

    try:
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id, ranges=range_names).execute()
        ranges = result.get('valueRanges', [])
        print(f"{len(ranges)} ranges retrieved by batch_get_values.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def update_values(spreadsheet_id, range_name, values,
                  value_input_option, creds):
    try:
        service = build('sheets', 'v4', credentials=creds)

        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def batch_update_values(spreadsheet_id, range_name, values,
                        value_input_option, creds):

    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)

        data = [
            {
                'range': range_name,
                'values': values
            },
            # Additional ranges to update ...
        ]
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()
        print(f"{(result.get('totalUpdatedCells'))} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error