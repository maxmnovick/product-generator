# product-generator.py
# generate product page in Shopify by setting variables in table format
# for import with Excelify

# take all subsidiary generators and bring them together to generate a product
# now we are looping first through all products, getting one field at a time for all products
# b/c we then copy-paste the output into the column in the spreadsheet, which is not in a particular order
# when we have all columns in a standard order or write code to find the column by name,
# we can first loop through all fields for a single product, and then the whole file will be output at once
# still, we could keep the looping the same way it is b/c it is more natural,
# unless it is much more efficient to loop through all fields for the same product
# rather than looping through all products for the same field, like the generator currently does

import generator, reader, writer, copy, re

# order of detail fields
sku_idx = 0
handle_idx = 1
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

# set the seller for different cost to price conversions and other requirements such as if inventory tracking capable
seller = 'HFF' # examples: JF, HFF

vendor = "Furniture World"
input = "new" # example inputs: details, options, names, new, all, raw
output = "product"
extension = "tsv"

all_details = generator.extract_data(vendor, input, extension)
# store init item details untouched so we can detect measurement type based on input format of dimensions
init_all_details = copy.deepcopy(all_details)
#writer.display_all_item_details(init_all_details)

# General Info from Details table
all_skus = []
for item_details in all_details:
	sku = item_details[sku_idx]
	all_skus.append(sku)


default_meas_type = "rectangular"

measurements = []

# use dims from details table for shopify description and zoho inventory
#print("=== Get Widths ===")
all_widths = []
for item_idx in range(len(all_details)):
	item_details = all_details[item_idx]
	init_item_details = init_all_details[item_idx]

	handle = item_details[handle_idx]
	#print("Item: " + handle)

	#width = item_details[width_idx]
	#print("Width: " + width)
	#init_width = init_item_details[width_idx]
	#print("Init Width: " + init_width)

	meas_type = reader.determine_measurement_type(item_details[width_idx], handle) # we need to know if the measurement is of a round or rectangular object so we can format output

	#print("Width: " + width)
	#init_width = init_item_details[width_idx]
	#print("Init Width: " + init_width)

	width = reader.format_dimension(item_details[width_idx], handle)

	#print("Width: " + width)
	#init_width = init_item_details[width_idx]
	#print("Init Width: " + init_width)

	#m = reader.Measurement(width,meas_type)
	if meas_type == 'rectangular':
		item_details[width_idx] = width
	else: #if meas_type == 'round' or meas_type == 'square' or meas_type == 'invalid':
		item_details[width_idx] = width
		item_details[depth_idx] = width
		# add dim to init_item_details so not really init item details anymore but needed for sorting later, now that we know dims
		init_item_details[depth_idx] = width

	all_widths.append(width)
	#measurements.append(m)

	#print("=== Got Widths ===")
	#print("Width: " + width)
	#init_width = init_item_details[width_idx]
	#print("Init Width: " + init_width)

#writer.display_all_item_details(init_all_details)

all_depths = []
for item_idx in range(len(all_details)):
	item_details = all_details[item_idx]
	handle = item_details[handle_idx]
	depth = reader.format_dimension(item_details[depth_idx], handle)
	item_details[depth_idx] = depth
	all_depths.append(depth)

all_heights = []
for item_details in all_details:
	handle = item_details[handle_idx]
	height = reader.format_dimension(item_details[height_idx], handle)
	item_details[height_idx] = height
	all_heights.append(height)

all_weights = []
for item_details in all_details:
	handle = item_details[handle_idx]
	weight = reader.format_dimension(item_details[weight_idx], handle)
	item_details[weight_idx] = weight
	all_weights.append(weight)

all_weights_in_grams = [] # shopify requires grams
for item_weight in all_weights:
	#print("item_weight: " + item_weight)
	weight_in_grams = int(item_weight) * 453.59237
	all_weights_in_grams.append(str(weight_in_grams))

# use from details table for shopify import
all_handles = []
for item_details in all_details:
	handle = item_details[handle_idx]
	all_handles.append(handle)
	
all_costs = []
for item_details in all_details:
	cost = ''
	if len(item_details) > cost_idx:
		cost = item_details[cost_idx]
	if cost.lower() == 'n/a':
		all_costs.append('')
	else:
		all_costs.append(cost)
all_barcodes = []
for item_details in all_details:
	barcode = ''
	if len(item_details) > barcode_idx:
		barcode = item_details[barcode_idx]
	if barcode.lower() == 'n/a':
		all_barcodes.append('')
	else:
		all_barcodes.append(barcode)

all_img_srcs = []
for item_details in all_details:
	img_src = ''
	if len(item_details) > img_src_idx:
		img_src = item_details[img_src_idx]
		img_src = re.sub(";",",",img_src)
	if img_src.lower() == 'n/a':
		all_img_srcs.append('')
	else:
		all_img_srcs.append(img_src)
all_vrnt_imgs = []
for item_idx in range(len(all_details)):
	item_details = all_details[item_idx]
	vrnt_img = ''
	if len(item_details) > img_src_idx:
		img_src = item_details[img_src_idx]
		if not re.search(",",img_src):
			vrnt_img = img_src
	all_vrnt_imgs.append(vrnt_img)

# ====== Shopify Product Catalog ======
print("\n====== Shopify Product Catalog ======\n")

#writer.display_all_item_details(init_all_details)

# generate handles
product_handles = generator.generate_all_handles(all_details)
#writer.display_field_values(product_handles)

# generate titles, based on handles
product_titles = generator.generate_all_titles(all_details, product_handles)
#writer.display_field_values(product_titles)

# generate tags
product_tags = generator.generate_all_tags(all_details, vendor)
#writer.display_field_values(product_tags)

# generate product types
product_types = generator.generate_all_product_types(all_details)
#writer.display_field_values(product_types)

# generate product img srcs
product_img_srcs = generator.generate_all_product_img_srcs(all_details)
writer.display_field_values(product_img_srcs)

# generate options
product_options = generator.generate_all_options(all_details, init_all_details) # we need init details to detect measurement type
#writer.display_field_values(product_options)
#writer.display_all_item_details(init_all_details)

# generate descriptions
product_descriptions = generator.generate_all_descriptions(all_details, init_all_details)
#writer.display_field_values(product_descriptions)

def compute_vrnt_price(cost, type):

	#print("Cost: " + cost)

	vrnt_price_string = ''

	if cost != '':
		cost_value = float(cost) # make float for math operations
		#print("Cost Value: " + str(cost_value))

		vrnt_price = 0.0
		vrnt_price_string = ''
		rug_deliv_price = 70
		mattress_multiplier = 3
		common_deliv_rate = 1.15
		online_only_rate = 1
		if seller == 'JF':
			common_multiplier = 2.4
		elif seller == 'HFF':
			common_multiplier = 1.8
			online_only_rate = 1.1
			common_deliv_rate = 1.2
		else:
			common_multiplier = 2.0

		if type == 'rugs':
			vrnt_price = cost_value * online_only_rate * common_multiplier + rug_deliv_price
			#print("vrnt_price = " + str(cost_value) + " * " + str(common_multiplier) + " + " + str(rug_deliv_price) + " = " + str(vrnt_price))
		elif type == 'mattresses' or type == 'box springs':
			vrnt_price = cost_value * online_only_rate * mattress_multiplier
		else:
			vrnt_price = cost_value * online_only_rate * common_deliv_rate * common_multiplier
		#print("Variant Price Before Rounding: " + str(vrnt_price))

		# round price
		rounded_price = generator.roundup(vrnt_price)
		rounded_price = float(rounded_price)
		#print("Rounded Price Up To Nearest 100: " + str(rounded_price))

		remainder = rounded_price % vrnt_price
		#print("Remainder: " + str(remainder))

		if type == 'rugs':
			# if the remainder is below 30, round up; if 30 or above, round down
			if remainder >= 30:
				vrnt_price = generator.rounddown(vrnt_price) - 0.01
			else:
				vrnt_price = rounded_price - 0.01
		else:
			# if the remainder is below 50, round up; if 50 or above, round down
			if remainder >= 50:
				vrnt_price = generator.rounddown(vrnt_price) - 0.01
			else:
				vrnt_price = rounded_price - 0.01

		vrnt_price_string = str(vrnt_price)

		#print("Final Variant Price: " + vrnt_price_string)

	return vrnt_price_string

def round_price(price):
	rounded_price = generator.roundup(price)
	rounded_price = float(rounded_price)

	return rounded_price - 0.01

def compute_vrnt_compare_price(price):

	#print("Price: " + price)

	compare_price_string = ''

	if price != '':

		price_value = float(price)

		compare_price = 0.0
		compare_price_string = ''
		discount = True
		discount_multiplier = 1.2
		if discount:
			compare_price = round_price(price_value * discount_multiplier)
			compare_price_string = str(compare_price)
			#print("Compare Price: " + compare_price_string)

	return compare_price_string

# returns list of all unique variants no longer grouped into products
def isolate_unique_variants(all_sorted_products, import_type):
	unique_variants = []
	for sorted_product in all_sorted_products:
		for variant in sorted_product:
			if generator.determine_unique_variant(variant, sorted_product, import_type):
				unique_variants.append(variant)

	return unique_variants

# sort from small to large so price user sees in grid view is first price shown on product page
def sort_items_by_size(all_item_info, import_type):
	#print("\n=== Sort Items by Size ===\n")
	all_sorted_items = all_item_info # list of strings in shopify import format

	# isolate products in unsorted import table
	isolated_product_imports = generator.isolate_product_strings(all_item_info, import_type)
	#print("Unsorted Product Imports: " + str(isolated_product_imports) + "\n")
	num_product_imports = len(isolated_product_imports)
	#print("Num Unsorted Product Imports: " + str(num_product_imports) + "\n")

	isolated_product_details = generator.isolate_products(all_details)
	#print("Unsorted Product Details: " + str(isolated_product_details) + "\n")
	num_product_details = len(isolated_product_details)
	#print("Num Unsorted Product Details: " + str(num_product_details) + "\n")

	if num_product_imports == num_product_details:
		all_sorted_products = []
		all_sorted_items = []

		num_isolated_products = len(isolated_product_details)
		#print("Num Isolated Products: " + str(num_isolated_products))

		for product_idx in range(num_isolated_products):
			product_details = isolated_product_details[product_idx] # list of data
			product_imports = isolated_product_imports[product_idx] # string of data

			sorted_indices = generator.get_sorted_indices(product_details)
			num_sorted_indices = sorted_indices.size
			#print("Num Sorted Indices = Num Widths: " + str(num_sorted_indices))

			num_variants = len(product_details)
			#print("Num Variants: " + str(num_variants))

			sorted_variants = product_details # init as unsorted variants
			# only sort variants if we have valid values for sorting
			if num_variants == num_sorted_indices:
				sorted_variants = [] # How can we be sure there are valid dimensions given?
				for idx in range(num_variants):
					#print("Index: " + str(idx))
					sorted_idx = sorted_indices[idx]
					#print("Sorted Index: " + str(sorted_idx))
					sorted_variant = product_imports[sorted_idx]
					sorted_variants.append(sorted_variant)
			else:
				print("Warning: Num Variants != Num Sorted Indices while sorting items!")

			all_sorted_products.append(sorted_variants)

		all_sorted_items = isolate_unique_variants(all_sorted_products, import_type)

	else:
		print("Warning: Num Product Imports != Num Product Details (" + str(num_product_imports) + " != " + str(num_product_details) + ") while sorting items!\n")

# 	all_sorted_products = []
#
# 	isolated_product_details = generator.isolate_products(all_details)
# 	#print("Isolated Product Details: " + str(isolated_product_details))
# 	isolated_product_imports = generator.isolate_products(all_item_info)
# 	#print("Isolated Product Imports: " + str(isolated_product_imports))
#
# 	num_product_details = len(product_details)
# 			num_product_imports = len(product_imports)
#
# 	if num_product_details == num_product_imports:
# 		for item_idx in range(len(isolated_product_details)):
# 			product = isolated_product_details[0]
# 			variant = product[0]
# 			handle = variant[1]
# 			print("Item: " + handle)
# 			product_details = isolated_product_details[item_idx]
# 			product_import = isolated_product_imports[item_idx]
#
#
#
# 			sorted_variants = product_imports
#
#
# 				sorted_indices = generator.get_vrnt_idx_by_size(product_details)
# 				num_widths = sorted_indices.size
# 				print("Num Widths: " + str(num_widths))
# 				num_variants = len(product_details)
# 				print("Num Variants: " + str(num_variants))
# 				if num_variants == num_widths:
# 					sorted_variants = []
# 					for variant_idx in range(num_variants):
# 						sorted_idx = sorted_indices[variant_idx]
# 						print("Sorted Idx: " + str(sorted_idx))
# 						sorted_variant = product_import[sorted_idx]
# 						sorted_variants.append(sorted_variant)
# 				else:
# 					print("Warning: Num Variants != Num Widths!")
# 			else:
# 				print("Warning: Num Product Details != Num Product Imports!")
#
# 			all_sorted_products.append(sorted_variants)
#
# 	for product in all_sorted_products:
# 		for variant in product:
# 			all_sorted_items.append(variant)
#

	#print("\n=== Sorted Items by Size ===\n")

	return all_sorted_items

# print as single string that can then be separated by semicolon delimiter
def display_shopify_variants(import_tool = 'shopify'): # set import tool when calling to display the variants to be imported with the given import tool, bc they have different import orders although some do not care about order but use the title to determine field value match

	print("\n === Display Shopify Variants === \n")

	all_final_item_info = []

	for item_idx in range(len(product_titles)):

		# fields copied from details to shopify import
		#handle = all_handles[item_idx] formerly copied directly from catalog table but now made automatically from raw data descrip and collection name (if col name not given by vendor then look in product names table)
		item_cost = all_costs[item_idx]
		barcode = all_barcodes[item_idx]
		#img_src = all_img_srcs[item_idx] # formerly copied from catalog but img src may need to be reformatted as with google drive

		# fields generated specifically for shopify import
		product_handle = product_handles[item_idx] # added new way to make product handle 8/21/22
		product_title = product_titles[item_idx]
		product_tag_string = product_tags[item_idx]
		product_type = product_types[item_idx]
		product_img_src = product_img_srcs[item_idx]

		product_option_string = writer.format_option_string(product_options[item_idx])

		body_html = product_descriptions[item_idx]
		vrnt_inv_tracker = '' # leave blank unless inv track capable
		vrnt_inv_policy = ''
		if import_tool == 'excelify':
			vrnt_inv_policy = 'continue'
		else:
			vrnt_inv_policy = 'deny'
		vrnt_weight_unit = 'lb'
		cmd = 'UPDATE'
		vrnt_price = compute_vrnt_price(item_cost, product_type)
		vrnt_compare_price = compute_vrnt_compare_price(vrnt_price)

		# fields determined by request content/context
		published = 'TRUE'
		published_scope = 'global'

		# general fields
		sku = all_skus[item_idx]
		item_weight = all_weights[item_idx]

		final_item_info = ""
		if import_tool == 'shopify':
			# shopify specific fields
			standard_product_type = ''
			item_weight_in_grams = all_weights_in_grams[item_idx]
			vrnt_inv_qty = ''
			vrnt_fulfill_service = 'manual'
			vrnt_req_ship = 'TRUE'
			vrnt_taxable = 'TRUE'
			img_position = ''
			img_alt = ''
			gift_card = 'FALSE'
			vrnt_tax_code = ''
			product_status = 'active'

			print("product_type: " + product_type)

			vrnt_img = product_img_src # still need to account for multiple img srcs given

			final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + vrnt_inv_tracker + ";" + vrnt_inv_qty + ";" + vrnt_inv_policy + ";" + vrnt_fulfill_service + ";" + vrnt_price + ";" + vrnt_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
		elif import_tool == 'excelify':
			final_item_info = sku + ";" + product_handle + ";" + item_weight + ";" + item_cost + ";" + barcode + ";=" + body_html + ";" + product_option_string + ";" + product_tag_string + ";" + product_img_src + ";" + product_type + ";" + product_title + ";" + published + ";" + published_scope + ";" + vrnt_inv_tracker + ";" + vrnt_inv_policy + ";" + vrnt_weight_unit + ";" + cmd + ";" + vendor + ";" + vrnt_price + ";" + vrnt_compare_price

		#print(final_item_info)
		all_final_item_info.append(final_item_info)

	sorted_final_item_info = sort_items_by_size(all_final_item_info, "shopify")
	#sorted_final_item_info = all_final_item_info

	writer.display_shopify_variant_headers()
	for item_info in sorted_final_item_info:
		print(item_info)

	return sorted_final_item_info

all_final_item_info = display_shopify_variants() # currently uses all global variables

generator.write_data(all_final_item_info, vendor, output, extension)

# ====== Zoho Inventory ======

inventory_enabled = False # ask seller if separate tracking capable and if so what platform (eg zoho inventory)

if inventory_enabled:

	print("\n====== Zoho Inventory ======\n")

	# generate item names
	item_names = generator.generate_all_item_names(all_details, init_all_details)
	#writer.display_field_values(item_names)

	# generate "inventory" types (formerly "collection" types)
	item_collection_types = generator.generate_all_collection_types(all_details)
	#writer.display_field_values(item_collection_types)

	# print as single string that can then be separated by comma delimiter
	def display_zoho_items():

		all_final_item_info = []

		for item_idx in range(len(item_names)):

			# fields generated specifically for zoho import
			item_name = item_names[item_idx]
			item_collection_type = item_collection_types[item_idx]

			ref_num = item_idx + 1
			account = 'Cost of Goods Sold'
			reason = 'Update Inventory'

			# fields determined by request content/context
			adj_date = ''
			warehouse = ''
			qty_adj = ''
			adj_descrip = ''

			# fields copied from details to zoho import
			item_width = all_widths[item_idx]
			item_depth = all_depths[item_idx]
			item_height = all_heights[item_idx]

			# general fields
			sku = all_skus[item_idx]
			item_weight = all_weights[item_idx]

			final_item_info = sku + ";" + item_name + ";" + item_width + ";" + item_depth + ";" + item_height + ";" + item_weight + ";" + item_collection_type + ";" + str(ref_num) + ";" + account + ";" + reason + ";" + vendor + ";" + adj_date + ";" + warehouse + ";" + adj_descrip + ";" + qty_adj

			#print(final_item_info)
			all_final_item_info.append(final_item_info)

		import_type = 'zoho'
		sorted_final_item_info = sort_items_by_size(all_final_item_info, import_type)
		#sorted_final_item_info = all_final_item_info

		writer.display_zoho_item_headers()
		for item_info in sorted_final_item_info:
			print(item_info)

	display_zoho_items()
