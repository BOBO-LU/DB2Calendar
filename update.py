import datetime

import gspread
import loguru
from oauth2client.service_account import ServiceAccountCredentials

import config
from sheet_operation import (
    append_rows,
    batch_update_values,
    copy_and_rename_sheet,
    delete_rows,
    get_sheet_id_by_name,
    get_values,
    sheet_exists,
    update_values,
)
from try_dbf import get_data_from_dbf
from utils_logging import getexception

# Authenticate with Google Sheets API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(config.keyfile, scope)
client = gspread.authorize(credentials)

# Open your Google Sheet by title or URL
sheet_name = config.sheet_name
sheet_id = config.sheet_id  # means spreadsheet_id in google api

# path
dbf_path = "sch_pin.DBF"


def sync_process():
    print("start update calandar")

    # read data
    record_list = get_data_from_dbf(dbf_path)

    # get all unique doctors, and aggregate data by doctor
    record_dict = agg_data_by_doctor(record_list)

    # iterate each doctor
    for doctor_name in record_dict.keys():
        print(f"start process doctor: {doctor_name}")
        try:
            # find the sheet to update. if sheet not exist, create sheet
            if sheet_exists(sheet_id, doctor_name, credentials) is False:
                # create_sheet(sheet_id, doctor_name, credentials)
                copy_and_rename_sheet(sheet_id, 1872246998, doctor_name, credentials)
                update_values(
                    sheet_id, doctor_name, [[doctor_name]], "USER_ENTERED", credentials
                )

            # means sheet_id in google api
            doctor_sheet_id = get_sheet_id_by_name(sheet_id, doctor_name, credentials)

            # rotate calandar
            rotate_calandar(sheet_id, doctor_name, doctor_sheet_id)

            date_list = get_all_date_by_doctor(doctor_name)

            # get calandar data
            # TODO: get calandar data

            # find difference between data and calandar
            # TODO: find difference

            # itearte each data
            for row in record_dict[doctor_name]:
                print("row: ", row)
                # find the row, column to update
                range_str = get_range_by_data(row, date_list)
                print(f"range: {doctor_name}!{range_str}")
                # parse the data and update the row
                result = update_values(
                    sheet_id,
                    f"{doctor_name}!{range_str}",
                    [[row["calendar"]]],
                    "USER_ENTERED",
                    credentials,
                )
                print(result)

        except Exception as e:
            loguru.logger.error(getexception(e))


def agg_data_by_doctor(data_list):
    record_dict = {}
    for data in data_list:
        if (data["doctor"] in record_dict.keys()) is False:
            record_dict[data["doctor"]] = []

        record_dict[data["doctor"]].append(data)
    return record_dict


def get_all_date_by_doctor(doctor_name):
    # get date range list from calandar
    result = get_values(sheet_id, f"{doctor_name}!A:A", credentials)
    date_list = []
    for date in result.get("values", []):
        date_list.append(date[0])
    return date_list[1:]


def get_range_by_data(record: dict, date_list: list) -> str:
    # find the row, column to update by using the starttimeStr and finishtimeStr
    start_date = record["startDate"]
    end_date = record["endDate"]
    start_time = record["starttimeStr"].split(" ")[1]
    end_time = record["finishtimeStr"].split(" ")[1]
    range = "B2:B2"
    # TODO: detect outlier, the time should only locate between 10am to 10pm
    if start_date != end_date:
        # start date is not the same as end date, need to update multiple rows
        pass
    else:
        # start date is the same as end date, only need to update one row
        # plus 2 because the first row is doctor name, and it starts from index 1
        # print(date_list)
        row = date_list.index(start_date) + 2

        # find the column for start
        col_int = get_time_index(start_time) + 2
        col_start = index_to_excel_column(col_int)

        # find the column for end
        col_int = get_time_index(end_time) + 2
        col_end = index_to_excel_column(col_int)

        range = col_start + str(row) + ":" + col_end + str(row)
    return range


def get_time_index(given_time) -> int:
    # Convert the given time to total minutes since 10:00
    hh, mm = map(int, given_time.split(":")[:2])
    total_minutes_since_10 = (hh - 10) * 60 + mm

    # Divide by 15 to get the index
    index = total_minutes_since_10 // 15

    # Since you want the largest time smaller than the given time,
    # subtract 1 if the given time is not exactly on a 15-minute mark.
    if total_minutes_since_10 % 15 != 0:
        index -= 1

    return index


def index_to_excel_column(index) -> str:
    # Adjust the index to start from B (i.e., index 1)
    index += 1
    column = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        column = chr(65 + remainder) + column
    return column


def rotate_calandar(sheet_id, doctor_name, doctor_sheet_id):
    # delete rows and add new rows to the end
    date_list = get_all_date_by_doctor(
        doctor_name,
    )
    last_date_index = search_idx_before_today(date_list)

    if last_date_index == -1:
        return

    print("last_date_index: ", last_date_index)
    # 1 to 4 means delete B:D
    delete_rows(sheet_id, doctor_sheet_id, 1, last_date_index, credentials)
    append_rows(sheet_id, doctor_sheet_id, last_date_index, credentials)

    # get last date in calandar list, and update gsheet (last_date_index - 1) days after it
    last_date = datetime.datetime.strptime(date_list[-1], "%Y-%m-%d")
    new_dates = [
        (last_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(1, last_date_index + 1)
    ]
    result = update_values(
        sheet_id,
        f"{doctor_name}!A{len(date_list) - (last_date_index-2) }:A",
        [[date] for date in new_dates],
        "USER_ENTERED",
        credentials,
    )

    return result


def search_idx_before_today(dates):
    # binary search
    today = datetime.date.today()
    low, high = 1, len(dates) - 1

    # The answer will be stored in this variable
    ans = -1

    while low <= high:
        mid = (low + high) // 2
        current_date = datetime.datetime.strptime(dates[mid], "%Y-%m-%d").date()

        if current_date < today:
            ans = mid
            low = mid + 1
        else:
            high = mid - 1

    return ans


if __name__ == "__main__":
    # value = get_values(sheet_id, "林靜妤!A:A", credentials)
    # print(value)
    # value = get_values(sheet_id, "林靜妤!B1:AX1", credentials)
    # print(value)
    # value = batch_get_values(sheet_id, ["sheet1!A1:C2", "sheet1!A5:C6"], credentials)
    # print(value)

    print(get_sheet_id_by_name(sheet_id, "黃嫣", credentials))
    # copy_and_rename_sheet(sheet_id, 1872246998, '範例2', credentials)
    # print(search_idx_before_today(get_all_date_by_doctor("林靜妤")))
    # # Pass: spreadsheet_id, range_name value_input_option and _values)
    batch_update_values(
        sheet_id, "李融!AS41:AT42", [["F", "B"], ["C", "D"]], "USER_ENTERED", credentials
    )

    # # Pass: spreadsheet_id,  range_name, value_input_option and  _values
    update_values(
        sheet_id,
        "黃嫣!B5:D6",
        [["A\nA\nA", "B"], ["C", "D"]],
        "USER_ENTERED",
        credentials,
    )
