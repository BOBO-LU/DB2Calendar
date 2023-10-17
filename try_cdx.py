import pyclipper

# Load the CDX file
cdx_path = 'sch_pin.CDX'

# Open the CDX file
with pyclipper.CDX(cdx_path) as cdx_file:
    # Iterate over records in the CDX file
    for record in cdx_file:
        print(record)
