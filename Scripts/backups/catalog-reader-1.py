# catalog-reader.py
# description: read catalog of vendor products so each piece of data is a variable
#
# usage: catalog-reader.py <name-of-vendor>
#
# Example 1: display ESF catalog data for user to analyze
# catalog-reader.py esf
#
# put <vendor>-catalog.csv in Data folder next to Scripts folder

import catalog

vendor = "ESF" # user input

# read catalog headers to determine meaning of the catalog values
#catalog.display_headers(vendor) # display only the headers for that vendor

# read each row of the catalog and classify it so it can be treated with an understanding of how the data can be used to compute final values

# extract a single row from the catalog
#row_num = 2
#catalog.display_row(vendor, row_num)

#catalog.display_data(vendor)

# if we see the name in the vendor catalog contains "SET", that tells us to create a new product in our catalog

input_catalog = catalog.extract_catalog_data(vendor) # split catalog rows

arranged_catalog = catalog.arrange_catalog(input_catalog, vendor)

# import_fields = ["Handle", "Command", "Title", "Vendor", "Type",
# 	"Tags", "Published", "Image Src", "Variant SKU", "Variant Price",
# 	"Variant Inventory Tracker",
# 	"Option1 Name", "Option1 Value"]
#
# catalog.write_catalog(arranged_catalog, import_fields, vendor)
