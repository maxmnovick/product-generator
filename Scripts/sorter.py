# sorter.py
# sort and isolate and split variables

import generator

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
	all_sorted_items = all_item_info # list of strings in shopify import format

	# isolate products in unsorted import table
	isolated_product_imports = generator.isolate_product_strings(all_item_info, import_type)
	#print("\n===Unsorted Product Imports===\n" + str(isolated_product_imports) + "\n")
	num_product_imports = len(isolated_product_imports)
	#print("Num Unsorted Product Imports: " + str(num_product_imports) + "\n")

	isolated_product_details = generator.isolate_products(all_details)
	#print("\n===Unsorted Product Details===\n" + str(isolated_product_details) + "\n")
	num_product_details = len(isolated_product_details)
	#print("Num Unsorted Product Details: " + str(num_product_details) + "\n")

	if num_product_imports == num_product_details:
		all_sorted_products = []
		all_sorted_items = []

		num_isolated_products = len(isolated_product_details)
		#print("Num Isolated Products: " + str(num_isolated_products))

		for product_idx in range(num_isolated_products):
			product_details = isolated_product_details[product_idx] # list of data
			#print("product_details: " + str(product_details))
			product_imports = isolated_product_imports[product_idx] # string of data
			#print("product_imports: " + str(product_imports))

			sorted_indices = generator.get_sorted_indices(product_details)
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