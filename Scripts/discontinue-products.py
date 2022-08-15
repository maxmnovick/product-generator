# Discontinue products from a table by changing variable fields to assigned values
# Use Excelify to export Products with these data fields:
# - Basic Columns
# - Inventory / Variants
# - Variant Cost
#
# Usage: discontinue-products.py <name-of-collection-to-discontinue>

import collection
import datetime
import argparse

# create an ArgumentParser object to read command line arguments
parser = argparse.ArgumentParser(description='Discontinue a collection of products.')
parser.add_argument('collection')
args = parser.parse_args()
collection_arg = args.collection

# get products collection file
products_filename = "../Data/" + collection_arg + "-products-export.csv"
#print("products_filename: " + products_filename)

input_products = collection.read_collection(products_filename)

arranged_products = collection.arrange_products(input_products, [], "discontinue")

disco_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Tags", "Tags Command", "Variant Price", "Variant Compare At Price",
	"Variant Inventory Tracker", "Variant Inventory Qty",
	"Variant Inventory Item ID", "Variant ID", "Variant Command",
	"Option1 Name", "Option1 Value",
	"Option2 Name", "Option2 Value",
	"Option3 Name", "Option3 Value" ]

collection.write_collection(arranged_products, collection_arg, disco_product_fields)
