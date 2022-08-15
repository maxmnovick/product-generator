# Set product type
# if sale, append "-sale" to product type

import argparse

sale_type_suffix = "-sale"

sale_final_field = "Option3 Value" # no comma after final field
sale_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Variant Inventory Item ID", "Variant ID", "Variant Command",
	"Option1 Name", "Option1 Value",
	"Option2 Name", "Option2 Value",
	"Option3 Name", sale_final_field ]

# create an ArgumentParser object to read command line arguments
parser = argparse.ArgumentParser(description='Set product types for a collection of products.')
parser.add_argument('collection')
parser.add_argument('event')
args = parser.parse_args()
collection_arg = args.collection
event_arg = args.event

# get products collection file
products_filename = "../Data/" + collection_arg + "-products-export.csv"
#print("products_filename: " + products_filename)

sale_filename = "../Data/" + collection_arg + "-sale-import.csv"
sale_file = open(sale_filename, "w", encoding="utf8") # overwrite existing content

# =======sell collection=======
headers = ""
for field in sale_product_fields:
	headers += "\"" + field + "\""
	if field != sale_final_field:
		headers += ","

# display/export table csv
#print(headers)
sale_file.write(headers)
sale_file.write("\n")

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

if event_arg == "sale" or "normal":

	for product in products:

		init_product_info = product.split("\",") #["ID", "Handle", "Command", "Title", "Vendor", "Type", "Tags", "Tags Command", "Published", "Variant Inventory Tracker", "Variant Inventory Qty"]
		for info in range(len(init_product_info)):
			init_product_info[info] = init_product_info[info].replace("\"", "")

		product_type = init_product_info[6]
		if event_arg == "sale":
			# append sale to product type
			if not product_type.endswith(sale_type_suffix):
				product_type += sale_type_suffix
		if event_arg == "normal":
			# remove sale from product type
			if product_type.endswith(sale_type_suffix):
				product_type = product_type.replace(sale_type_suffix, "")

		# unchanged product info
		product_id = init_product_info[0]
		product_handle = init_product_info[1]
		product_title = init_product_info[3]
		product_vendor = init_product_info[5]
		product_command = "UPDATE"

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

		sale_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + product_command + "\",\"" + product_title + "\",\"" + product_vendor + "\",\"" + product_type + "\",\"" + variant_inv_item_id + "\",\"" + variant_id + "\",\"" + variant_command + "\",\"" + option1_name + "\",\"" + option1_value + "\",\"" + option2_name + "\",\"" + option2_value + "\",\"" + option3_name + "\",\"" + option3_value + "\""

		#print(disco_product_info + "\n")

		sale_file.write(sale_product_info)
		sale_file.write("\n")

	sale_file.close()

else:
	print("unrecognized event argument")
