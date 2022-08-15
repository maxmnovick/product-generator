# Discontinue products from a table by changing variable fields to assigned values

import datetime

# =======Global Variables========

current_date = datetime.datetime.now()

disco_type = "DISCONTINUED"
disco_command = "UPDATE"
disco_published = "FALSE"
disco_var_inv_tracker = "shopify"
disco_var_inv_qty = "0"
disco_tags_command = "REPLACE"

disco_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Tags", "Tags Command", "Published", "Variant Inventory Tracker",
	"Variant Inventory Qty"]

# =======discontinue collection=======
headers = ""
for field in disco_product_fields:
	headers += "\"" + field + "\""
	if field != "Variant Inventory Qty":
		headers += ","

# display/export table csv
print(headers)

# get products collection file
products_file = open("../Data/HomeElegance-products-export.csv")

for product_info in products_file:
	init_product_info = product_info.split(",") #["ID", "Handle", "Command", "Title", "Vendor", "Type", "Tags", "Tags Command", "Published", "Variant Inventory Tracker", "Variant Inventory Qty"]

	# get values for product to be discontinued
	# sample product: allura-night-stand
	#init_product_info = ["nightstands", "HomeElegance", "color-white, style-modern"] # sample table row with given product info

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

	# alter vendor
	disco_vendor = init_product_info[5] + "-Dropped"

	disco_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + disco_command + "\",\"" + product_title + "\",\"" + disco_vendor + "\",\"" + disco_type + "\",\"" + disco_tags + "\",\"" + disco_tags_command + "\",\"" + disco_published + "\",\"" + disco_var_inv_tracker + "\",\"" + disco_var_inv_qty + "\""

	print(disco_product_info)

products_file.close()
