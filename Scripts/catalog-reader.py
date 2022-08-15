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

vendor = "Aico" # user input

input_catalog = catalog.extract_catalog_data(vendor) # split catalog rows

input_collections = catalog.isolate_collections(input_catalog, vendor) # now we have an array of isolated collections

arranged_catalog = catalog.arrange_catalog(input_collections, vendor)

import_fields = ["Handle", "Command", "Title", "Body HTML", "Vendor", "Type",
	"Tags", "Published", "Published Scope", "Image Src", "Variant SKU",
	"Variant Price", "Variant Compare At Price", "Variant Cost",
	"Variant Inventory Tracker", "Variant Inventory Policy",
	"Variant Weight", "Variant Weight Unit",
	"Option1 Name", "Option1 Value"]

catalog.write_catalog(arranged_catalog, import_fields, vendor)
