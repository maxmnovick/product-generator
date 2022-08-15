# collection.py
# functions for a collection,
# such as change condition, or sort products

import numpy as np
import datetime

def arrange_headers(fields):
	headers = ""
	for field in fields:
		headers += "\"" + field + "\""
		#print("field: " + field + ", fields[-1]: " + fields[-1])
		if field != fields[-1]:
			headers += ","

	#print(headers)
	return headers

# each input value must be surrounded by quotes
def read_collection(filename):

	print("=== Read Collection: " + filename.replace("../Data/", "") + " ===\n")

	collection = [] # initialize array to hold rows in collection table

	with open(filename, encoding="utf8") as collection_file:
		next(collection_file) # cast 1st line into oblivion

		current_line = ""
		current_row = 1
		for collection_info in collection_file:
			collection_info = collection_info.strip()

			current_line += collection_info
			# if the line ends with a quotation mark, we know it is the end of the row
			if "\"" in collection_info[-1:]:
				#print("Row " + str(current_row) + ":\t" + current_line + "\n")
				collection.append(current_line)
				current_line = ""
			else:
				pass

			current_row += 1

		collection_file.close()

	print("\n=== End Collection: " + filename.replace("../Data/", "") + " ===\n\n")

	return collection

def isolate_category(collection):
	# isolate first category

	print("=== Isolate Category ===")
	category_rows = []

	product_counts = isolate_collection_field(collection, "products count")
	#print("product_counts: " + str(product_counts))

	category_start_idx = 1
	category_stop_idx = int(product_counts[category_start_idx-1])
	#print("category_stop_idx: " + str(category_stop_idx))

	for row_idx in range(category_stop_idx):
		category_rows.append(collection[row_idx])

	return category_rows

def isolate_category_from_collection(collection, start_idx, stop_idx):
	# isolate first category
	category_rows = []

	for row_idx in range(start_idx, stop_idx):
		category_rows.append(collection[row_idx])

		#if row_idx == start_idx or row_idx == stop_idx:
			#print("Row " + str(row_idx) + ":\t" + collection[row_idx] + "\n")

	print()

	return category_rows

def isolate_categories(collection):

	print("=== Isolate Categories ===\n")

	categories = []

	#product_counts = isolate_collection_field(collection, "products count")
	#print("product_counts: " + str(product_counts))

	collection_handles = np.array(isolate_collection_field(collection, "handle"))

	_, idx, cnt = np.unique(collection_handles, return_index=True, return_counts=True)

	unique_category_handles = collection_handles[np.sort(idx)]
	counts = cnt[np.argsort(idx)]
	indices = np.sort(idx)

	#unique_category_handles = collection_handles[np.sort(idx)]
	print("Unique Category Handles: " + str(unique_category_handles))

	#unique_category_handles, indices, counts = count_categories(collection)

	num_categories = len(unique_category_handles)
	print("Number of Categories:\t" + str(num_categories) + "\n")

	print("Number of Rows per Category: ")
	for category_idx in range(num_categories):
		print(unique_category_handles[category_idx] + ": " + str(counts[category_idx]))
	print()

	print("Indices of Category: ")
	for category_idx in range(num_categories):
		print(unique_category_handles[category_idx] + ": " + str(indices[category_idx]))
	print()



	for category_idx in range(num_categories):
		category_start_idx = indices[category_idx]
		#print("category_start_idx: " + str(category_start_idx))
		category_stop_idx = category_start_idx + counts[category_idx]
		#print("category_stop_idx: " + str(category_stop_idx))

		#print("Category:\n Handle: " + unique_category_handles[category_idx] + ",\n Rows: [ " + str(category_start_idx) + ", " + str(category_stop_idx) + " )\n")
		category_rows = isolate_category_from_collection(collection, category_start_idx, category_stop_idx)

		category_start_idx = category_stop_idx

		categories.append(category_rows)

		if category_start_idx > len(collection) - 1:
			break

	print("\n=== End Isolate Categories ===\n\n")

	return categories

def count_categories(collection):

	collection_handles = isolate_collection_field(collection, "handle")

	return np.unique(collection_handles, return_index=True, return_counts=True)

#	product_counts = isolate_collection_field(collection, "products count")
#
#	n = 0
#
#	category_start_idx = 0
#
#	if len(collection) > int(product_counts[category_start_idx]):
#
#		print("collection length > products count: " + str(len(collection)) + " > " + str(product_counts[category_start_idx]))
#
#		for row_idx in range(len(collection)):
#
#			if row_idx == category_start_idx:
#				n += 1
#
#				category_start_idx += int(product_counts[category_start_idx])
#
#				if category_start_idx > len(collection) - 1:
#					break
#
#	else: n = 1
#
#	return n

# can use for exported Products, Smart Collections, and probably others but untested
def isolate_collection_field(collection, field_title):

	print("=== Isolate Collection Field: " + field_title + " ===\n")

	collection_field_values = []

	# need to know order of data fields
	handle_idx = 1
	products_count_idx = 15
	product_id_idx = 22
	product_handle_idx = 23

	# set default values
	default_idx = handle_idx
	default_idx_start = product_id_idx
	default_idx_stop = product_handle_idx + 1

	# set init column idx to default
	column_idx = default_idx
	column_idx_start = default_idx_start
	column_idx_stop = default_idx_stop

	category_start_idx = 0

	for row_idx in range(len(collection)):
		#print("original collection row: " + collection[row_idx])

		init_collection_row = format_collection_row(collection, row_idx)

		if field_title == "handle":
			column_idx = handle_idx
			handle = init_collection_row[column_idx]
			collection_field_values.append(handle)

			#print("Handle:\t" + handle)

		elif field_title == "products count":
			column_idx = products_count_idx
			products_count = init_collection_row[column_idx]
			collection_field_values.append(products_count)

			#print("Products Count:\t" + products_count)

		elif field_title == "linked products":


			column_idx_start = product_id_idx
			column_idx_stop = product_handle_idx + 1

			#print("Linked Product Handle:\t" + init_collection_row[product_handle_idx])

			linked_product = init_collection_row[column_idx_start:column_idx_stop]
			collection_field_values.append(linked_product)

			#print("Linked Product:\t" + str(linked_product))

		else:
			print("unrecognized field title parameter")

	print("\n=== End Collection Field: " + field_title + " ===\n\n")

	return collection_field_values

def format_collection_row(collection, idx):
	row = collection[idx].split("\",")
	for field_idx in range(len(row)):
		row[field_idx] = row[field_idx].replace("\"", "")

	return row
	#print("init_collection_info: " + str(init_collection_info))

def sort_linked_products(init_linked_products, product_handles, sort_value):

	print("=== Sort Linked Products ===\n")

	linked_products = init_linked_products
	#print("linked_products: " + str(linked_products))

	for linked_product in linked_products:

		linked_product_id = linked_product[0]
		linked_product_handle = linked_product[1]
		#print("linked_product_handle: \"" + linked_product_handle + "\"")

		linked_product_value = ""
		for product_handle in product_handles:
			if product_handle == linked_product_handle:
				linked_product_value = sort_value
				break

		if linked_product_value == sort_value:
			#print(linked_product_handle + ": Mstar")
			# put product in position 1 of collection and shift other products to fill the empty space
			linked_product.append("Mstar")
			linked_products.insert(0, linked_products.pop(linked_products.index(linked_product)))
		else:
			linked_product.append("not Mstar")

	#for linked_product in linked_products:
		#print("Sorted Linked Product:\t" + linked_product[1])

	print("\n=== End Linked Products ===\n\n")

	return linked_products

# gather info for sorted category from different sources and format uniformly for import
def arrange_collection(collection, linked_products):
	# replace original linked product fields with sorted version

	print("=== Arrange Collection ===\n")

	print("Length of Collection: " + str(len(collection)) + "\n")

	categories = []

	for row_idx in range(len(collection)):
		#print("Row: " + str(row_idx))

		init_collection_row = format_collection_row(collection, row_idx)

		# unchanged collection info
		collection_id = init_collection_row[0]
		collection_handle = init_collection_row[1]
		collection_command = init_collection_row[2]
		collection_title = init_collection_row[3]
		collection_sort_order = init_collection_row[5]
		collection_published = init_collection_row[8]
		collection_match = init_collection_row[18]
		collection_rule_product_column = init_collection_row[19]
		collection_rule_relation = init_collection_row[20]
		collection_rule_condition = init_collection_row[21]

		# sorted linked product info
		linked_product_id = linked_products[row_idx][0]
		linked_product_handle = linked_products[row_idx][1]
		linked_product_vendor = linked_products[row_idx][2]

		# unchanged linked product position order b/c id and handle shifted instead
		linked_product_position = init_collection_row[24]

		sorted_category_info = "\"" + collection_id + "\",\"" + collection_handle + "\",\"" + collection_command + "\",\"" + collection_title + "\",\"" + collection_sort_order + "\",\"" + collection_published + "\",\"" + collection_match + "\",\"" + collection_rule_product_column + "\",\"" + collection_rule_relation + "\",\"" + collection_rule_condition + "\",\"" + linked_product_id + "\",\"" + linked_product_handle + "\",\"" + linked_product_position + "\""

		sorted_products = linked_product_handle + ", " + linked_product_vendor
		#print("Row " + str(row_idx) + ": " + sorted_products)

		categories.append(sorted_category_info)

	print("\n=== End Collection ===\n\n")

	return categories

def set_disco_prices(collection_row):

	disco_prices = []

	# set variant price and compare price, if field not empty string
	if collection_row[33] != "":
		init_variant_price = collection_row[33]
	else:
		print("Alert! Variant price appears to be set to 0! Correct price immediately!")
	init_variant_compare_price = collection_row[34] if collection_row[34] != "" else "0"

	disco_price = init_variant_compare_price if float(init_variant_compare_price) > float(init_variant_price) else init_variant_price
	disco_compare_price = ""

	disco_prices.append(disco_price)
	disco_prices.append(disco_compare_price)

	return disco_prices

def set_disco_vendor(collection_row):

	disco_vendor = ""
	disco_vendor_suffix = "-Dropped"

	# alter vendor if not already set to "Dropped" version
	if collection_row[5].endswith(disco_vendor_suffix):
		init_product_vendor = collection_row[5].split("-")
		if len(init_product_vendor) > 2:
			disco_vendor = init_product_vendor[0] + disco_vendor_suffix
		else:
			disco_vendor = collection_row[5]
	else:
		disco_vendor = collection_row[5] + disco_vendor_suffix

	return disco_vendor

def set_disco_tags(collection_row, disco_date):
	# alter tags
	disco_tags = collection_row[7]
	disco_date_metrics = ["year", "month", "day of month", "day of week"]
	# =======get date values from calendar=======
	disco_date_values = [disco_date.year, disco_date.month, disco_date.day, disco_date.strftime("%A")]
	for index in range(len(disco_date_metrics)):
		disco_date_tag = "discontinued-" + disco_date_metrics[index] + "-" + str(disco_date_values[index])
		disco_tags += ", " + disco_date_tag
	#print("tags: " + disco_tags)

	return disco_tags

def change_product_properties(init_products, init_properties, action, value):
	pass


def arrange_products(init_products, changed_properties, change_property):

	print("=== Arrange Products ===\n")

	print("Length of Collection: " + str(len(init_products)) + "\n")

	products = []

	current_date = datetime.datetime.now()

	for row_idx in range(len(init_products)):

		init_collection_row = format_collection_row(init_products, row_idx)

		# unchanged product info
		product_id = init_collection_row[0]
		product_handle = init_collection_row[1]
		product_title = init_collection_row[3]

		# changed product info
		product_command = ""
		product_vendor = ""
		product_type = ""
		product_tags = ""
		product_tags_command = ""
		product_var_inv_tracker = ""
		product_var_inv_qty = ""

		# generally unchanged variant info, needed for Excelify import
		variant_inv_item_id = init_collection_row[18]
		variant_id = init_collection_row[19]
		variant_command = init_collection_row[20]
		option1_name = init_collection_row[21]
		option1_value = init_collection_row[22]
		option2_name = init_collection_row[23]
		option2_value = init_collection_row[24]
		option3_name = init_collection_row[25]
		option3_value = init_collection_row[26]

		variant_price = variant_compare_price = ""
		variant_prices = [variant_price, variant_compare_price]
		if change_property == "discontinue":
			variant_prices = set_disco_prices(init_collection_row)

			product_vendor = set_disco_vendor(init_collection_row)

			product_command = "UPDATE"

			product_type = "DISCONTINUED"

			product_tags = set_disco_tags(init_collection_row, current_date)

			product_tags_command = "REPLACE"

			product_var_inv_tracker = "shopify"

			product_var_inv_qty = "0"

		elif change_property == "tags":

			product_tags = changed_properties

		if len(variant_prices) == 2:
			variant_price = variant_prices[0]
			variant_compare_price = variant_prices[1]
		else:
			print("Warning: Variant price and compare price not set.")

		changed_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + product_command + "\",\"" + product_title + "\",\"" + product_vendor + "\",\"" + product_type + "\",\"" + product_tags + "\",\"" + product_tags_command + "\",\"" + variant_price + "\",\"" + variant_compare_price + "\",\"" + product_var_inv_tracker + "\",\"" + product_var_inv_qty + "\",\"" + variant_inv_item_id + "\",\"" + variant_id + "\",\"" + variant_command + "\",\"" + option1_name + "\",\"" + option1_value + "\",\"" + option2_name + "\",\"" + option2_value + "\",\"" + option3_name + "\",\"" + option3_value + "\""

		products.append(changed_product_info)

	print("\n=== End Products ===\n\n")

	return products

def write_collection(collection, category_handle, collection_headers):

	import_type = "Smart-Collections-sorted" if collection_headers[-1] == "Product: Position" else "Products-changed"
	category_filename = "../Data/" + category_handle.lower() + "-" + import_type + "-import.csv"
	category_file = open(category_filename, "w", encoding="utf8") # overwrite existing content

	collection_headers = arrange_headers(collection_headers)

	category_file.write(collection_headers)
	category_file.write("\n")
	#print(collection_headers)

	for row_idx in range(len(collection)):
		#print(sorted_category_info + "\n")
		category_file.write(collection[row_idx])
		category_file.write("\n")
		#print(collection[row_idx])

	category_file.close()
