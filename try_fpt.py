import pprint

from dbfread import DBF

# Load the DBF file
dbf_path = "sch_pin.DBF"
table = DBF(dbf_path)

# Load the FPT file
fpt_path = "sch_pin.FPT"

# Create a dictionary to store FPT records by record number
fpt_records = {}

# Read the FPT records and store them in the dictionary
with open(fpt_path, "rb") as fpt_file:
    record_number = 1
    while True:
        length_bytes = fpt_file.read(4)
        if not length_bytes:
            break
        length = int.from_bytes(length_bytes, "big")
        fpt_data = fpt_file.read(length)
        fpt_records[record_number] = fpt_data.decode("utf-8", errors="ignore")
        record_number += 1

# Print the FPT records
for record in table:
    # print(record)
    pprint.pprint(record["JSON"])
    # break
    # record_number = record['__record_number']
    # fpt_data = fpt_records.get(record_number, '')
    # print(f"Record Number: {record_number}")
    # print(f"FPT Data: {fpt_data}")
