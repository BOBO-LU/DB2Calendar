import datetime
import json
import time

from dbfread import DBF

import config

from loguru import logger
def get_data_from_dbf(dbf_path):
    if config.TEST is True:
        # read data_list.txt
        with open(r"D:\行事曆同步\schk_pin.dbf", "r") as f:
            data_list = eval(f.read())
        return data_list

    data_list = []
    # Load the DBF file
    table = DBF(dbf_path)
    # for record in table:
    #     print(record)
    #     print("*"*10)
    # Print the records
    for record in table:
        if record["JSON"] is None:
            continue
        # print("record: ", record)
        data_str = record["JSON"]
        
        data_str = data_str.strip().replace(" ", "")
        # print("data_str: ", data_str)
        chunks = data_str.split("}")
        
        # print("chunks: ", chunks)
        # Parsing the first JSON string
        dict1 = json.loads(chunks[0] + "}")

        # if appointmenttime or expectFinishedTime is not exist, skip this record
        if (
            "appointmenttime" not in dict1.keys()
            or "expectFinishedTime" not in dict1.keys()
        ):
            continue

        if config.TEST is False:
            # if appointmenttime is before today, skip
            if dict1["appointmenttime"] < time.time() * 1000:
                continue

        # utilize datetime and turn appointmenttime 1695731400000 into readable time and add it to dict
        appointStr = datetime.datetime.fromtimestamp(dict1["appointmenttime"] / 1000)
        dict1["starttimeStr"] = appointStr.strftime("%Y-%m-%d %H:%M:%S")
        finishStr = datetime.datetime.fromtimestamp(dict1["expectFinishedTime"] / 1000)
        dict1["finishtimeStr"] = finishStr.strftime("%Y-%m-%d %H:%M:%S")

        dict1["startDate"] = appointStr.strftime("%Y-%m-%d")
        dict1["endDate"] = finishStr.strftime("%Y-%m-%d")

        dict1[
            "calendar"
        ] = f"{dict1['id']}\n{dict1['name']}\n{dict1['phone']}\n{dict1['note']}"

        logger.debug(dict1)
        # if not in dental opening time, skip
        if appointStr.hour < 10:
            logger.debug(f"appointment not in opening times")
            continue
        # Printing the results

        # for k, v in dict1.items():
        #     print(k, v)
        # print("*" * 20)

        data_list.append(dict1)

    # print(data_list)
    # write data_list to txt
    # with open("data_list.txt", "w") as f:
    #     f.write(str(data_list))
    return data_list


if __name__ == "__main__":
    get_data_from_dbf("D:\行事曆同步\schk_pin.dbf")
