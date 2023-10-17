from dbfread import DBF
import pprint
import json
import datetime
import time
import config

def get_data_from_dbf(dbf_path):
    data_list = []
    # Load the DBF file
    table = DBF(dbf_path)

    # Print the field names
    print(table.field_names)

    # Print the records
    for record in table:
        # print(record)
        data_str = record['JSON']
        data_str = data_str.strip().replace(" ","")
        # print(data_str)
        chunks = data_str.split("\r\n\r\n")
        # print(chunks)
        # Parsing the first JSON string
        dict1 = json.loads(chunks[0])
        
        # if appointmenttime or expectFinishedTime is not exist, skip this record
        if 'appointmenttime' not in dict1.keys() or 'expectFinishedTime' not in dict1.keys():
            continue
        
        if config.TEST is False:
            # if appointmenttime is before today, skip
            if dict1['appointmenttime'] < time.time() * 1000:
                continue

        # utilize datetime and turn appointmenttime 1695731400000 into readable time and add it to dict
        appointStr = datetime.datetime.fromtimestamp(dict1['appointmenttime'] / 1000)
        dict1['starttimeStr'] = appointStr.strftime("%Y-%m-%d %H:%M:%S")
        finishStr = datetime.datetime.fromtimestamp(dict1['expectFinishedTime'] / 1000)
        dict1['finishtimeStr'] = finishStr.strftime("%Y-%m-%d %H:%M:%S")

        dict1['startDate'] = appointStr.strftime("%Y-%m-%d")
        dict1['endDate'] = finishStr.strftime("%Y-%m-%d")

        # # Printing the results
        # # print(dict1)
        # for k, v in dict1.items():
        #     print(k, v)
        # print("*"*20)
        data_list.append(dict1)

    print(data_list)
    return data_list


if __name__ == "__main__":
    get_data_from_dbf('./data/sch_pin.DBF')