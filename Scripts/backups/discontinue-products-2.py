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
	"Tags", "Tags Command", "Published", "Variant Price",
	"Variant Compare At Price", "Variant Inventory Tracker",
	"Variant Inventory Qty"]

# get products collection file
products_filename = "../Data/HomeElegance-products-export.csv"

disco_file = open("../Data/HomeElegance-disco-import.csv", "w") # overwrite existing content

# =======discontinue collection=======
headers = ""
for field in disco_product_fields:
	headers += "\"" + field + "\""
	if field != "Variant Inventory Qty":
		headers += ","

# display/export table csv
print(headers)
disco_file.write(headers)

products = []

with open(products_filename) as products_file:
	next(products_file) # cast into oblivion

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

	init_variant_price = init_product_info[33]
	init_variant_compare_price = init_product_info[34]

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

	disco_price = init_variant_compare_price if float(init_variant_compare_price) > float(init_variant_price) else init_variant_price
	disco_compare_price = ""

	disco_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + disco_command + "\",\"" + product_title + "\",\"" + disco_vendor + "\",\"" + disco_type + "\",\"" + disco_tags + "\",\"" + disco_tags_command + "\",\"" + disco_published + "\",\"" + disco_price + "\",\"" + disco_compare_price + "\",\"" + disco_var_inv_tracker + "\",\"" + disco_var_inv_qty + "\""

	print(disco_product_info + "\n")

	disco_file.write(disco_product_info)

disco_file.close()
