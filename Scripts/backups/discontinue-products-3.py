# Discontinue products from a table by changing variable fields to assigned values
# Use Excelify to export Products with these data fields:
# - Basic Columns
# - Inventory / Variants
# - Variant Cost
#
# Usage: discontinue-products.py <name-of-collection-to-discontinue>

import datetime
import argparse

# =======Global Variables========

current_date = datetime.datetime.now()

disco_type = "DISCONTINUED"
disco_command = "UPDATE"
disco_var_inv_tracker = "shopify"
disco_var_inv_qty = "0"
disco_tags_command = "REPLACE"

disco_final_field = "Option3 Value" # no comma after final field

disco_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Tags", "Tags Command", "Variant Price", "Variant Compare At Price",
	"Variant Inventory Tracker", "Variant Inventory Qty",
	"Variant Inventory Item ID", "Variant ID", "Variant Command",
	"Option1 Name", "Option1 Value",
	"Option2 Name", "Option2 Value",
	"Option3 Name", disco_final_field ]

# create an ArgumentParser object to read command line arguments
parser = argparse.ArgumentParser(description='Discontinue a collection of products.')
parser.add_argument('collection')
args = parser.parse_args()
collection_arg = args.collection

# get products collection file
products_filename = "../Data/" + collection_arg + "-products-export.csv"
#print("products_filename: " + products_filename)

disco_filename = "../Data/" + collection_arg + "-disco-import.csv"
disco_file = open(disco_filename, "w", encoding="utf8") # overwrite existing content

# =======discontinue collection=======
headers = ""
for field in disco_product_fields:
	headers += "\"" + field + "\""
	if field != disco_final_field:
		headers += ","

# display/export table csv
#print(headers)
disco_file.write(headers)
disco_file.write("\n")

products = []

with open(products_filename, encoding="utf8") as products_file:
	next(products_file) # cast 1st line into oblivion

	current_line = ""
	for product_info in products_file:
		product_info = product_info.strip()
		#print("product_info: " + product_info)
		#print("last character in line: " + product_info[-1:])
		current_line += product_info
		if "\"" in product_info[-1:]:
			#print('NEW')
			products.append(current_line)
			#print("products: " + str(products))
			current_line = ""
		else:
			#print('CONTINUE')
			pass

	products_file.close()


for product in products:
	#print("original product: " + product)

	init_product_info = product.split("\",") #["ID", "Handle", "Command", "Title", "Vendor", "Type", "Tags", "Tags Command", "Published", "Variant Inventory Tracker", "Variant Inventory Qty"]
	for info in range(len(init_product_info)):
		init_product_info[info] = init_product_info[info].replace("\"", "")
	#print("init_product_info: " + str(init_product_info))
	# get values for product to be discontinued
	# sample product: allura-night-stand
	#init_product_info = ["nightstands", "HomeElegance", "color-white, style-modern"] # sample table row with given product info

	# set variant price and compare price, if field not empty string
	if init_product_info[33] != "":
		init_variant_price = init_product_info[33]
	else:
		print("Alert! Variant price appears to be set to 0! Correct price immediately!")
	init_variant_compare_price = init_product_info[34] if init_product_info[34] != "" else "0"

	# unchanged product info
	product_id = init_product_info[0]
	product_handle = init_product_info[1]
	product_title = init_product_info[3]

	# alter tags
	disco_tags = init_product_info[7]
	disco_date_metrics = ["year", "month", "day of month", "day of week"]
	# =======get date values from calendar=======
	disco_date_values = [current_date.year, current_date.month, current_date.day, current_date.strftime("%A")]
	for index in range(4):
		disco_date_tag = "discontinued-" + disco_date_metrics[index] + "-" + str(disco_date_values[index])
		disco_tags += ", " + disco_date_tag
	#print("tags: " + disco_tags)

	disco_vendor_suffix = "-Dropped"
	# alter vendor if not already set to "Dropped" version
	if init_product_info[5].endswith(disco_vendor_suffix):
		init_product_vendor = init_product_info[5].split("-")
		if len(init_product_vendor) > 2:
			disco_vendor = init_product_vendor[0] + disco_vendor_suffix
		else:
			disco_vendor = init_product_info[5]
	else:
		disco_vendor = init_product_info[5] + disco_vendor_suffix

	disco_price = init_variant_compare_price if float(init_variant_compare_price) > float(init_variant_price) else init_variant_price
	disco_compare_price = ""

	# generally unchanged variant info, needed for Excelify import
	variant_inv_item_id = init_product_info[18]
	variant_id = init_product_info[19]
	variant_command = init_product_info[20]
	option1_name = init_product_info[21]
	option1_value = init_product_info[22]
	option2_name = init_product_info[23]
	option2_value = init_product_info[24]
	option3_name = init_product_info[25]
	option3_value = init_product_info[26]

	disco_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + disco_command + "\",\"" + product_title + "\",\"" + disco_vendor + "\",\"" + disco_type + "\",\"" + disco_tags + "\",\"" + disco_tags_command + "\",\"" + disco_price + "\",\"" + disco_compare_price + "\",\"" + disco_var_inv_tracker + "\",\"" + disco_var_inv_qty + "\",\"" + variant_inv_item_id + "\",\"" + variant_id + "\",\"" + variant_command + "\",\"" + option1_name + "\",\"" + option1_value + "\",\"" + option2_name + "\",\"" + option2_value + "\",\"" + option3_name + "\",\"" + option3_value + "\""

	#print(disco_product_info + "\n")

	disco_file.write(disco_product_info)
	disco_file.write("\n")

disco_file.close()
