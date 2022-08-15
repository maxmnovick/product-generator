# catalog.py
# functions for a catalog,
# such as read catalog, isolate fields, extract data for manipulation
# read catalogs from different vendors, b/c they come in different formats

import re, string
import product, collection
import numpy as np

#======ESF=====
# read from csv [ "Code", "Name", "Description 2", "Price", "MAP price", "Default set qts", "Width", "Depth", "Height", "Weight", "Volume", "Manufacturer", "Category Type", "Stock Status", "New Arrivals", "Parent Category", "Category", "Refine Categories", "Image 1"]

def display_headers(vndr):

	print("=== Display Headers ===\n")

	catalog_headers = extract_catalog_headers(vndr)

	print(catalog_headers)

	print("=== Displayed Headers ===\n")

def display_data(vndr):

	print("=== Display Data ===\n")

	catalog_data = extract_catalog_data(vndr)

	print(catalog_data)

	print("=== Displayed Data ===\n")

def display_row(vndr, rwnm):

	print("=== Display Row " + str(rwnm) + " ===\n")

	catalog_row = extract_catalog_row(vndr, rwnm)

	print("Row " + str(rwnm) + ": " + str(catalog_row))

	print("=== Displayed Row " + str(rwnm) + " ===\n")

# display whole catalog, including headers
def display_catalog(vndr):

	print("=== Display Catalog ===\n")

	catalog_data = extract_catalog(vndr)

	print(catalog_data)

	print("=== Displayed Catalog ===\n")

# def extract_catalog_headers(vndr):
#
# 	print("=== Extract Catalog Headers ===\n")
#
# 	catalog_filename = "../Data/" + vndr + "-catalog-sample.tsv"
#
# 	catalog_headers = []
#
# 	with open(catalog_filename, encoding="UTF8") as catalog_file:
#
# 		current_line = ""
# 		for catalog_info in catalog_file:
# 			current_line = catalog_info.strip()
# 			catalog_headers.append(current_line)
# 			break
#
# 		catalog_file.close()
#
# 	print("=== Extracted Catalog Headers ===\n")
#
# 	return catalog_headers

def extract_catalog_data(vndr):

	print("=== Extract Catalog Data ===\n")

	catalog_rows = split_catalog_rows(vndr)

	print("Length of Catalog: " + str(len(catalog_rows)) + "\n")

	print("=== Extracted Catalog Data ===\n")

	return catalog_rows

def extract_catalog_row(vndr, rwnm):

	print("=== Extract Catalog Row " + str(rwnm) + " ===\n")

	catalog_rows = split_catalog_rows(vndr)

	catalog_row = catalog_rows[rwnm-2]

	print("=== Extracted Catalog Row " + str(rwnm) + " ===\n")

	return catalog_row

def split_catalog_rows(vndr):

	print("=== Split Catalog Rows ===\n")

	catalog_lines = split_catalog_lines(vndr)

	rows = []

	line_num = 1
	current_info = ""
	previous_info = ""
	for line in catalog_lines:
		#print("Line " + str(line_num) + ": " + line)
		if line_num != 1:
			new_row = determine_new_row(line, line_num, vndr)
			if new_row:
				# continue adding lines to current info string until next new line found
				if current_info != "":

					#print("\nPrevious Row: " + current_info + "\n")

					rows.append(current_info)
					current_info = ""

			elif vndr == "ESF" and line != '': # if new line but not new row, add period and space if not already
				line = line + ". "

			current_info += line

		line_num += 1

	rows.append(current_info)

	# row_num = 2
	# for row in rows:
	# 	print("Row " + str(row_num) + ": " + row + "\n")
	# 	row_num += 1

	print("=== Split Catalog Rows ===\n")

	return rows

def split_catalog_lines(vndr):

	print("=== Split Catalog Lines ===\n")

	catalog_filename = "../Data/" + vndr + "-catalog-sample.tsv"

	lines = []

	with open(catalog_filename, encoding="UTF8") as catalog_file:

		current_line = ""
		for catalog_info in catalog_file:
			current_line = catalog_info.strip()
			lines.append(current_line)

		catalog_file.close()

	# line_num = 1
	# for line in lines:
	# 	print("Line " + str(line_num) + ": " + line + "\n")
	#
	# 	line_num += 1

	print("=== Split Catalog Lines ===\n")

	return lines

def determine_new_row(ln, lnnm, vndr):
	new_row = False

	tsv = True

	# How to recognize when you have come to the end of a row in the ESF catalog?
	# Could check next line to see if first column is blank or all caps?
	# I know where the first row ends and the second begins b/c I know that the next row first cell is all caps. Plus the last entry in the row is a Finish, which has finite variations.
	# Problem is not all rows begin with all caps, so need exception rule.
	# Code field (column 1) is blank for Sets and Special Order items
	# the only field that uses multiple lines is the description field, so we could isolate that field to separate rows
	# when you come to the end of a line, check the first few letters of the next line. If they are all caps, then start a new row.
	if vndr == "ESF":

		if tsv:
			new_row = True
		else:
			blank_line = False
			blank_code = False
			uppercase_code = False

			# if first value in line is all caps, or only first value in line is blank, consider this new row
			#print(str(lnnm) + ": " + ln + "\n")

			#print("Is line " + str(lnnm) + " the start of a new row?")

			#print("Is line " + str(lnnm) + " blank?")
			if ln == "":
				#print("Yes, line " + str(lnnm) + " is blank. So, it is not the start of a new row.")
				blank_line = True
			else:
				#print("No, line " + str(lnnm) + " is not blank. So, it may be the start of a new row.")

				#print("What is the first character in line " + str(lnnm) + "?")

				char1 = ln[0]
				#print("The first character in line " + str(lnnm) + " is '" + char1 + "'.")

				#print("Is the first character in line " + str(lnnm) + " a comma?") # b/c comma indicates code is blank
				if char1 == ",":
					#print("Yes, the first character in line " + str(lnnm) + " is a comma. So, it is the start of a new row. It is also the start of a new collection.")
					blank_code = True
				else:
					#print("No, the first character in line " + str(lnnm) + " is not a comma. So, it may be the start of a new row.")
					blank_code = False

					# check if all uppercase code
					uppercase_code = product.check_uppercase_code(ln)

			if blank_line:
				new_row = False
			elif blank_code:
				new_row = True
			elif uppercase_code:
				new_row = True

	elif vndr == "Aico":
		if tsv:
			new_row = True

	decision = ""
	if new_row:
		decision = "is"
	else:
		decision = "is not"

	#print("Line " + str(lnnm) + " " + decision + " the start of a new row.\n")

	return new_row

def isolate_collections(catalog, vndr):

	print("=== Isolate Collections ===\n")

	collections = []

	if vndr == "ESF":

		parent_skus = np.array(isolate_catalog_field(catalog, "parent sku"))

		_, idx, cnt = np.unique(parent_skus, return_index=True, return_counts=True)

		unique_parent_skus = parent_skus[np.sort(idx)]
		counts = cnt[np.argsort(idx)]
		indices = np.sort(idx)

		#print("Unique Parent SKUs: " + str(unique_parent_skus))

		num_collections = len(unique_parent_skus) # determine the number of collections based on the number of unique parent skus
		print("Number of Collections:\t" + str(num_collections) + "\n")

		#print("Number of Rows per Collection: ")
		for collection_idx in range(num_collections):
			print(unique_parent_skus[collection_idx] + ": " + str(counts[collection_idx]))
		print()

		#print("Indices of Collection: ")
		for collection_idx in range(num_collections):
			print(unique_parent_skus[collection_idx] + ": " + str(indices[collection_idx]))
		print()

		# isolate collections and append to collections array
		for collection_idx in range(num_collections):
			collection_start_idx = indices[collection_idx]
			print("collection_start_idx: " + str(collection_start_idx))
			collection_stop_idx = collection_start_idx + counts[collection_idx]
			print("collection_stop_idx: " + str(collection_stop_idx))

			#print("Collection:\n Parent SKU: " + unique_parent_skus[collection_idx] + ",\n Rows: [ " + str(collection_start_idx) + ", " + str(collection_stop_idx) + " )\n")
			collection_rows = isolate_collection_from_catalog(catalog, collection_start_idx, collection_stop_idx)

			collection_start_idx = collection_stop_idx

			collections.append(collection_rows)

			if collection_start_idx > len(catalog) - 1:
				break

	elif vndr == "Aico": # 1 collection in entire catalog, technically b/c they are all the same style, separated by sender before sending us the catalog
		collections.append(catalog)
	else
		print("Warning: Unrecognized vendor while isolating collections!")

	# for row_idx in range(len(collections)):
	# 	print("Collection " + str(row_idx) + ": " + str(collections[row_idx]) + "\n")

	print("=== Isolated Collections ===\n")

	return collections

def isolate_catalog_field(catalog, field_title):

	print("=== Isolate Catalog Field: " + field_title + " ===\n")

	catalog_field_values = []

	# need to know order of data fields
	parent_sku_idx = 110

	# set default values
	default_idx = parent_sku_idx

	# set init column idx to default
	column_idx = default_idx

	# get values in the catalog for the given field
	for row_idx in range(len(catalog)):
		# add quotes around fields so we can split by quote-comma pairs instead of just comma, which is unreliable
		# split by tab if using tsv file as input
		init_catalog_row = catalog[row_idx].split("\t")
		row_num = row_idx + 2
		#print("Initial Row " + str(row_num) + ": " + str(init_catalog_row))
		#print("Number of Fields in Row " + str(row_num) + ": " + str(len(init_catalog_row)))

		cell1 = init_catalog_row[0] # name for parent row, code (all caps) for item rows
		cell2 = init_catalog_row[1] # use to determine special order
		cell3 = init_catalog_row[2] # description for item rows with a code, price for parent row and item rows with no code

		if field_title == "parent sku":
			# how to recognize first item in collection: need to isolate collections first
			# since this is before collections isolated, need to know that first value of parent item is not all caps (b/c no code), like all other first items with codes in all caps
			if determine_new_collection(cell1, cell2, cell3): # if parent or first item in collection
				print("New Collection")
				column_idx = parent_sku_idx - 2 # -2 b/c first value of set field "code" is blank, so the row shifts 1 to the left, on top of the parent sku already being 1 to the left for room set rows
			elif determine_special_order(cell2):
				print("Special Order found in cell2")
				column_idx = parent_sku_idx - 1
			elif determine_special_order(cell3):
				print("Special Order found in cell3")
				column_idx = parent_sku_idx
			else:
				column_idx = parent_sku_idx
			parent_sku = init_catalog_row[column_idx]
			catalog_field_values.append(parent_sku)

			if parent_sku == '':
				print("Parent SKU is blank!")
			else:
				print("Parent SKU:\t" + parent_sku + "\n")

		else:
			print("unrecognized field title parameter")

	print("\n=== Isolated Catalog Field: " + field_title + " ===\n\n")

	return catalog_field_values

def determine_new_collection(value1, value2, value3):

	#print("\n=== Determine New Collection ===\n")

	new_collection = True

	# if code is all numbers, not new collection, so do not remove numbers
	if value1.isdigit():
		print("Code is all digits")
		new_collection = False
	else:
		simple_value1 = re.sub('[\W_]+', '', value1) # only need first series of letters
		#print("value1: " + simple_value1)

		simple_value3 = value3.lower()
		#print("value3: " + simple_value3)

		item_key = "special order"

		if simple_value1.isupper():
			new_collection = False
		elif determine_special_order(value2):
			if not re.search("set", simple_value1.lower()):
				#print("Special Order and not a Set, so same collection")
				new_collection = False
		elif determine_special_order(value3):
			#print("Special Order, so same collection")
			new_collection = False

	#if new_collection:
		#print("\n=== Determined New Collection ===\n")
	#else:
		#print("\n=== Determined Same Collection ===\n")

	return new_collection

def determine_special_order(potential_name):
	special_key = "special order"

	return re.search(special_key, potential_name.lower())

def isolate_collection_from_catalog(catalog, start_idx, stop_idx):

	print("\n=== Isolate Collection from Catalog ===\n")

	collection_rows = []

	for row_idx in range(start_idx, stop_idx):
		#print("Catalog Row " + str(row_idx) + ": " + catalog[row_idx])
		collection_rows.append(catalog[row_idx])

	#for row_idx in range(len(collection_rows)):
		#print("Collection Row " + str(row_idx) + ": " + collection_rows[row_idx])

	print("\n=== Isolated Collection from Catalog ===\n")

	return collection_rows

def arrange_catalog(collections, vndr):

	print("\n=== Arrange Catalog ===\n")

	products = []

	all_types = [ "chests", "dressers", "mirrors", "nightstands" ] #read_types()

	# loop through collections in catalog
	for collection_idx in range(len(collections)):

		init_collection = collections[collection_idx] # now we have a single sample collection
		print("Initial Collection " + str(collection_idx+1) + ": " + str(init_collection) + "\n")

		variant_skus = []

		# loop through items in collection
		for item_idx in range(len(init_collection)):

			# only proceed for product types that the program has been verified to handle
			product_type = product.set_type(init_collection, all_types, item_idx, vndr)

			if determine_valid_product_type(product_type):

				print("\n=== Create Catalog Row ===\n")

				variant_option_names = collection.determine_valid_options(init_collection, product_type)
				variant_values = []

				if len(variant_option_names) != 0:
					variant_values = collection.determine_option_values(init_collection, product_type, variant_option_names)

				variant_options = collection.isolate_variant_options(variant_option_names, variant_values)

				variants = collection.isolate_variants(init_collection, product_type, variant_option_names, variant_skus)

				# product info to compute
				product_handle = product.set_handle(init_collection, item_idx, product_type)
				product_command = "NEW" # Use NEW Command b/c if duplicate handle, we want to create non-conflict name. W/ NEW, if duplicate, result Fails. We do not want to Replace, Update, or Delete b/c we know this product is not on our catalog yet. We know it is not in our catalog yet, b/c we received it in the context of new products from vendors we are now offering.
				product_title = product.set_title(init_collection, item_idx, product_type)
				product_description = product.set_description(init_collection) # enclose with double quotes b/c contains commas and quotes not meant to be separated
				product_vendor = vndr

				product_tags = product.set_tags(vndr)
				product_publish_status = "FALSE"
				product_publish_scope = "web" # for behavior, see https://excelify.io/tutorials/publish-or-unpublish-shopify-products-in-bulk/
				product_img_src = product.set_img_src(init_collection)

				for vrnt_idx in range(len(variants)):
					# variant info to compute
					variant_sku = product.set_sku(variants[vrnt_idx])
					if determine_unique_sku(variant_sku, variant_skus):
						variant_skus.append(variant_sku)
						variant_price = product.set_price(variants[vrnt_idx])
						if variant_price == '0':
							print("Price=0, so there are no standard variants in this collection.")
							break
						variant_compare_at_price = product.set_compare_at_price(variant_price)
						variant_cost = product.set_cost(variants[vrnt_idx])
						variant_inv_tracker = "shopify"
						variant_inv_policy = "continue"

						variant_weight = product.set_weight(variants[vrnt_idx])
						variant_weight_unit = "lb"

						variant_num = vrnt_idx + 1 # use this number to determine what the option names and values should be for those variants with consistent pattern
						option1_name = product.set_option_name(product_type, variant_num, variant_options)
						option1_value = product.set_option_value(product_type, variant_num, variant_options)

						final_catalog_row = "\"" + product_handle + "\",\"" + product_command + "\",\"" + product_title + "\",\"" + product_description + "\",\"" + product_vendor + "\",\"" + product_type + "\",\"" + product_tags + "\",\"" + product_publish_status + "\",\"" + product_publish_scope + "\",\"" + product_img_src + "\",\"" + variant_sku + "\",\"" + variant_price + "\",\"" + variant_compare_at_price + "\",\"" + variant_cost + "\",\"" + variant_inv_tracker + "\",\"" + variant_inv_policy + "\",\"" + variant_weight + "\",\"" + variant_weight_unit + "\",\"" + option1_name + "\",\"" + option1_value + "\""

						products.append(final_catalog_row)

						print("\nFinal Catalog Row: " + final_catalog_row + "\n")

						print("\n=== Created Catalog Row ===\n")
					else:
						print("\n=== Warning: Duplicate Catalog Row Not Created ===\n")
			else:
				print("Catalog Reader cannot process products of type " + product_type + ".\n")

	print("=== Arranged Catalog ===\n")

	return products

def determine_unique_sku(variant_sku, variant_skus):
	unique_sku = True
	for current_sku in variant_skus:
		if re.search(variant_sku, current_sku):
			unique_sku = False
			break

	return unique_sku

def determine_valid_product_type(p_type):
	valid_type = False

	valid_types = [ "chests", "dressers", "mirrors", "nightstands" ]

	print("Product Type: " + p_type)
	for v_type in valid_types:
		if re.search(v_type, p_type):
			print("Valid Type: " + v_type)
			valid_type = True
			break

	return valid_type

def write_catalog(catalog, catalog_headers, vndr):

	print("=== Write Catalog ===\n")

	catalog_filename = "../Data/" + vndr + "-import.csv"
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	catalog_headers = arrange_headers(catalog_headers)

	catalog_file.write(catalog_headers)
	catalog_file.write("\n")
	#print(collection_headers)

	for row_idx in range(len(catalog)):
		catalog_file.write(catalog[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()

	print("=== Wrote Catalog ===\n")

def arrange_headers(fields):
	headers = ""
	for field in fields:
		headers += "\"" + field + "\""
		#print("field: " + field + ", fields[-1]: " + fields[-1])
		if field != fields[-1]:
			headers += ","

	#print(headers)
	return headers
