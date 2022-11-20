# isolator.py
# isolate objects, such as groups in lists, separate lists

import generator
import numpy as np

def isolate_product_from_details(all_details, start_idx, stop_idx):
	product_rows = []

	for variant_idx in range(start_idx, stop_idx):
		product_rows.append(all_details[variant_idx])

	return product_rows

def isolate_products(all_details):
	products = []

	field_title = "handle" # we know that all variants of the same product have the same handle

	#handles = np.array(isolate_detail_field(all_details, field_title))
	handles = np.array(generator.generate_all_handles(all_details))

	_, idx, cnt = np.unique(handles, return_index=True, return_counts=True)

	unique_handles = handles[np.sort(idx)]
	counts = cnt[np.argsort(idx)]
	indices = np.sort(idx)

	num_products = len(unique_handles)

	# isolate products and append to products array
	for product_idx in range(num_products):
		product_start_idx = indices[product_idx]
		product_stop_idx = product_start_idx + counts[product_idx]

		product_rows = isolate_product_from_details(all_details, product_start_idx, product_stop_idx)
		products.append(product_rows)

		product_start_idx = product_stop_idx
		if product_start_idx > len(all_details) - 1:
			break

	#print("Products: " + str(products) + "\n")
	return products

def isolate_detail_field(all_details, field_title):

	#print("\n=== Isolate Detail Field: " + field_title + " ===")

	detail_field_values = []

	handle_idx = 1 # shopify
	item_name_idx = 1 # zoho
	field_idx = 0
	if field_title == "handle":
		field_idx = handle_idx
	elif field_title == "title":
		field_idx = item_name_idx

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		#print("Item Details: " + str(item_details))
		field_value = item_details[field_idx]
		#print("Init Field Value: " + field_value)

		if field_title == "title": # zoho import where title is part of item name title/opt_value
			field_data = field_value.split("/")
			field_value = field_data[0]

		#print("Final Field Value: " + field_value)
		detail_field_values.append(field_value)

	#print("=== Isolated Detail Field: " + field_title + " ===\n")

	return detail_field_values

def isolate_product_strings(all_imports, import_type):
	products = []

	#print("All Imports: " + str(all_imports) + "\n")
	#print("Isolate Product Strings for Import Type: \"" + import_type + "\"")

	field_title = "handle" # we know that all variants of the same product have the same handle

	if import_type == "zoho":
		field_title = "title"

	all_import_data = []
	for variant_import in all_imports:
		import_data = []
		import_data = variant_import.split(";")
		all_import_data.append(import_data)

	handles = np.array(isolate_detail_field(all_import_data, field_title))
	#handles = np.array(generate_all_handles(all_details))

	_, idx, cnt = np.unique(handles, return_index=True, return_counts=True)

	unique_handles = handles[np.sort(idx)]
	counts = cnt[np.argsort(idx)]
	indices = np.sort(idx)

	num_products = len(unique_handles)

	# isolate products and append to products array
	for product_idx in range(num_products):
		product_start_idx = indices[product_idx]
		product_stop_idx = product_start_idx + counts[product_idx]

		product_rows = isolate_product_from_details(all_imports, product_start_idx, product_stop_idx)
		products.append(product_rows)

		product_start_idx = product_stop_idx
		if product_start_idx > len(all_imports) - 1:
			break

	#print("Products: " + str(products) + "\n")
	return products


# returns list of all unique variants no longer grouped into products
# def isolate_unique_variants(all_sorted_products, import_type):
# 	unique_variants = []
# 	for sorted_product in all_sorted_products:
# 		for variant in sorted_product:
# 			if generator.determine_unique_variant(variant, sorted_product, import_type):
# 				unique_variants.append(variant)

# 	return unique_variants