# sorter.py
# sort and isolate and split variables

import generator, isolator, reader, determiner
import re
import numpy as np

# order of detail fields
sku_idx = 0
collection_idx = handle_idx = 1 # formerly handle_idx = 1 when we were given handle but now we need to make handle from description and collection name
title_idx = 2
intro_idx = 3
color_idx = 4
mat_idx = 5
finish_idx = 6
width_idx = 7
depth_idx = 8
height_idx = 9
weight_idx = 10
features_idx = 11
cost_idx = 12
img_src_idx = 13
barcode_idx = 14

# returns list of all unique variants no longer grouped into products
def isolate_unique_variants(all_sorted_products, import_type):
	unique_variants = []
	for sorted_product in all_sorted_products:
		for variant in sorted_product:
			if generator.determine_unique_variant(variant, sorted_product, import_type):
				unique_variants.append(variant)

	return unique_variants

# sort from small to large so price user sees in grid view is first price shown on product page
def sort_items_by_size(all_item_info, import_type, all_details):
	print("\n=== Sort Items by Size ===\n")
	#print("all_item_info: " + str(all_item_info))
	all_sorted_items = all_item_info # list of strings in shopify import format

	# isolate products in unsorted import table
	# isolated_product_imports = isolator.isolate_product_strings(all_item_info, import_type)
	# print("\n===Unsorted Product Imports===\n" + str(isolated_product_imports) + "\n")
	# num_product_imports = len(isolated_product_imports)
	sorted_product_imports = sort_product_imports(all_item_info, import_type)
	#print("\n===Sorted Product Imports by Handle===\n" + str(sorted_product_imports) + "\n")
	num_product_imports = len(sorted_product_imports)
	#print("Num Unsorted Product Imports: " + str(num_product_imports) + "\n")

	# isolated_product_details = isolator.isolate_products(all_details)
	# print("\n===Unsorted Product Details===\n" + str(isolated_product_details) + "\n")
	# num_product_details = len(isolated_product_details)
	sorted_products = sort_products(all_details)
	#print("\n===Sorted Products by Handle===\n" + str(sorted_products) + "\n")
	num_product_details = len(sorted_products)
	#print("Num Unsorted Product Details: " + str(num_product_details) + "\n")

	if num_product_imports == num_product_details:
		all_sorted_products = []
		all_sorted_items = []

		#num_isolated_products = len(isolated_product_details)
		num_isolated_products = len(sorted_products)
		#print("Num Isolated Products: " + str(num_isolated_products))

		for product_idx in range(num_isolated_products):
			#product_details = isolated_product_details[product_idx] # list of data
			product_details = sorted_products[product_idx] # list of data
			#print("product_details: " + str(product_details))
			#product_imports = isolated_product_imports[product_idx] # string of data
			product_imports = sorted_product_imports[product_idx] # string of data
			
			#print("product_imports: " + str(product_imports))

			sorted_indices = get_sorted_indices(product_details)
			num_sorted_indices = sorted_indices.size
			#print("Num Sorted Indices = Num Widths: " + str(num_sorted_indices))

			num_variants = len(product_details)
			#print("Num Variants: " + str(num_variants))

			sorted_variants = product_details # init as unsorted variants
			# only sort variants if we have valid values for sorting
			if num_variants == num_sorted_indices:
				#print('num_variants == num_sorted_indices')
				sorted_variants = [] # How can we be sure there are valid dimensions given?
				for idx in range(num_variants):
					#print("Index: " + str(idx))
					sorted_idx = sorted_indices[idx]
					#print("Sorted Index: " + str(sorted_idx))
					sorted_variant = product_imports[sorted_idx]
					sorted_variants.append(sorted_variant)
			else:
				print("Warning: Num Variants != Num Sorted Indices while sorting items!")

			#print("sorted_variants: " + str(sorted_variants))

			all_sorted_products.append(sorted_variants)
			#print("all_sorted_products: " + str(all_sorted_products))

		all_sorted_items = isolate_unique_variants(all_sorted_products, import_type)
		#print("all_sorted_items: " + str(all_sorted_items))
	else:
		print("Warning: Num Product Imports != Num Product Details (" + str(num_product_imports) + " != " + str(num_product_details) + ") while sorting items!\n")

	return all_sorted_items

# shopify needs images on separate lines
def split_variants_by_img(all_import_strings):
	print("\n===Split Variants by Image===\n")

	#print("all_import_strings: " + str(all_import_strings))
	all_split_variants_by_img = []

	all_import_data = []
	for item in all_import_strings:
		#print("item: " + str(item))
		# split by semicolon
		item_data = item.split(';')
		all_import_data.append(item_data)
	#print("all_import_data: " + str(all_import_data))

	for item_import_data in all_import_data:
		#print("item_import_data: " + str(item_import_data))
		import_img_src_idx = 25
		images_string = item_import_data[import_img_src_idx]
		#print("images_string: " + str(images_string))
		images_list = images_string.split(',')
		#print("images_list: " + str(images_list))
		items_with_single_img = []
		for img_idx in range(len(images_list)):
			img = images_list[img_idx]
			#print("img: " + str(img))
			# if not first img then we only want handle and image in row, blanking out all others so it does not cause conflict during import
			if img_idx != 0:
				for value_idx in range(len(item_import_data)):
					value = item_import_data[value_idx]
					if value_idx != 0: # keep handle
						value = ''
						item_import_data[value_idx] = value
			item_import_data[import_img_src_idx] = img

			#convert to string with semicolon delimiter
			value_string = ''
			for value_idx in range(len(item_import_data)):
				value = item_import_data[value_idx]
				if value_idx == 0:
					value_string = value
				else:
					value_string += ';' + value
			all_split_variants_by_img.append(value_string)
		#print("all_split_variants_by_img: " + str(all_split_variants_by_img))

	return all_split_variants_by_img


def get_sorted_indices(product):

	#print("\n=== Get Variant Indices by Size ===\n")

	areas = []
	widths = []

	for variant in product:
		width = depth = height = ''

		handle = ''

		if len(variant) > width_idx:
			#handle = variant[1].strip().lower()
			handle = generator.generate_handle(variant)
			#print("Handle: " + handle)
			width = variant[width_idx].strip()

			if len(variant) > depth_idx:
				depth = variant[depth_idx].strip()

				if len(variant) > height_idx:
					height = variant[height_idx].strip()

		blank_width = blank_depth = blank_height = True
		if width != '' and width != 'n/a':
			blank_width = False
		if depth != '' and depth != 'n/a':
			blank_depth = False
		if height != '' and height != 'n/a':
			blank_height = False

		meas_type = ''
		if not blank_width:
			meas_type = determiner.determine_measurement_type(width, handle)

		if not blank_width and not blank_depth:
			width = reader.format_dimension(width, handle)
			depth = reader.format_dimension(depth, handle)

			width_float = float(width)
			width_int = round(width_float,0)

			depth_float = float(depth)
			depth_int = round(depth_float,0)

			area = width_int * depth_int
			areas.append(area)
			widths.append(width_int)

		elif blank_width:
			widths.append(0) # we need 0 returned for width if empty

		elif blank_depth:
			# if width contains multiple ft symbols and depth is blank, take digits before first foot symbol as width and digits after as depth
			if re.search('\'\\s*\\d+\'',width):
				dims = width.split('\'')
				width = dims[0].rstrip('\'')
				depth = dims[1].rstrip('\'')

				width = reader.format_dimension(width, handle)
				depth = reader.format_dimension(depth, handle)

				width_float = float(width)
				width_int = round(width_float,0)
				widths.append(width_int)

			if meas_type == 'round' or meas_type == 'square':
				width = reader.format_dimension(width, handle)
				depth = width

				width_float = float(width)
				width_int = round(width_float,0)

				depth_float = float(depth)
				depth_int = round(depth_float,0)

				area = width_int * depth_int
				areas.append(area)
				widths.append(width_int)
		else:
			widths.append(0) # we need 0 returned for width if empty

	#print("Areas: " + str(areas))
	#print("Widths: " + str(widths))

	#areas_array = np.array(areas)
	widths_array = np.array(widths)

	sorted_indices = np.argsort(widths_array)
	#sorted_indices = np.flip(sorted_indices) removed flip b/c thought better to have larger first for upsell but actually better to have smaller first b/c then customer is willing to explore options (otherwise high price is deterrent to even looking)
	#print("Sorted Indices: " + str(sorted_indices))

	#print("\n=== Got Variant Indices by Size ===\n")

	return sorted_indices

def sort_variants_by_size(product):

	variant1 = product[0]
	handle = generator.generate_handle(variant1)
	#print("=== Sort Variants by Size: " + handle + " ===")

	sorted_indices = get_sorted_indices(product) # numpy array
	num_widths = sorted_indices.size
	#print("Num Widths: " + str(num_widths))

	sorted_variants = product
	num_variants = len(product)
	#print("Num Variants: " + str(num_variants))

	# only sort variants if we have valid values for sorting
	if num_variants == num_widths:
		sorted_variants = []
		for idx in range(num_variants):
			#print("Index: " + str(idx))
			sorted_idx = sorted_indices[idx]
			#print("Sorted Index: " + str(sorted_idx))
			sorted_variant = product[sorted_idx]
			sorted_variants.append(sorted_variant)
	else:
		print("Warning for " + handle + ": Num Variants != Num Widths (" + str(num_variants) + " != " + str(num_widths) + ") while sorting variants!")

	#for variant in sorted_variants:
		#print("Sorted Variant: " + str(variant))
	return sorted_variants

# before isolating products, they must be sorted by handle
def sort_products(unsorted_product_details, sort_feature=''):
	print("\n===Sort Products===\n")
	#print("unsorted_product_details: " + str(unsorted_product_details))
	sorted_products = []
	if sort_feature == '':
		# default by handle
		# for product in unsorted_product_details:
		# 	handle = generator.generate_handle(product)

		# separate/isolate products by handle
		# group lists by handle element to get isolated products from final item info
		# for efficiency, we could assume items already sorted by handle at this point bc we are passed sorted final item info, but we could leave this in case the first sorting fcn fails
		products = {}
		product_handle_idx = 0 # change to beginning and then remove before adding to final list
		for item_data in unsorted_product_details:
			#print("item_data: " + str(item_data))
			handle = generator.generate_handle(item_data)
			
			#item_data.append(handle)
			item_data.insert(0,handle)
			#print("item_data with handle: " + str(item_data))
			item_handle = item_data[product_handle_idx]
			# print("item_handle: " + item_handle)
			item_data.pop(0)
			products.setdefault(item_handle, []).append(item_data)
		#print("products: " + str(products))

		sorted_products = list(products.values()) # products separated by handle
		
	
	#print("sorted_products: " + str(sorted_products))
	return sorted_products

# before isolating products, they must be sorted by handle
def sort_product_imports(unsorted_product_imports, import_type, sort_feature=''):
	print("\n===Sort Product Imports===\n")
	#print("unsorted_product_imports: " + str(unsorted_product_imports))
	sorted_product_imports = []
	# print("sort_feature: " + sort_feature)
	if sort_feature == '':
		# default by handle
		# for product in unsorted_product_details:
		# 	handle = generator.generate_handle(product)

		# separate/isolate products by handle
		# group lists by handle element to get isolated products from final item info
		# for efficiency, we could assume items already sorted by handle at this point bc we are passed sorted final item info, but we could leave this in case the first sorting fcn fails
		products = {}
		product_handle_idx = 0 # change to beginning and then remove before adding to final list
		for item_import in unsorted_product_imports:
			#print("item_import: " + str(item_import))
			item_data = item_import.split(';')
			item_handle = item_data[product_handle_idx]
			#print("item_handle: " + item_handle)
			products.setdefault(item_handle, []).append(item_import)
		#print("products: " + str(products))

		sorted_product_imports = list(products.values()) # products separated by handle
		
		# reconstruct strings
		# sorted_product_import = ""
		# for product in sorted_products:
		# 	for feature in product:
		# 		sorted_product_import += feature + ";"

		
		# 	sorted_product_imports.append(sorted_product_import)


	#print("sorted_product_imports: " + str(sorted_product_imports))
	return sorted_product_imports