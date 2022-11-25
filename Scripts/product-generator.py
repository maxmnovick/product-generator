# product-generator.py
# generate product page in Shopify by setting variables in table format
# for import with Excelify or shopify import tool
# local test for generateml.com

# take all subsidiary generators and bring them together to generate a product
# now we are looping first through all products, getting one field at a time for all products
# b/c we then copy-paste the output into the column in the spreadsheet, which is not in a particular order
# when we have all columns in a standard order or write code to find the column by name,
# we can first loop through all fields for a single product, and then the whole file will be output at once
# still, we could keep the looping the same way it is b/c it is more natural,
# unless it is much more efficient to loop through all fields for the same product
# rather than looping through all products for the same field, like the generator currently does

import re
import copy # to store init deep copy of catalog for processing
import reader # format input field values
import writer
import converter # convert all weights to grams
import generator # generate output
import sorter # sort items by size

from determiner import determine_stocked



# order of detail fields, from init catalog, not needed bc field determined by keywords

# set the seller for different cost to price conversions and other requirements such as if inventory tracking capable
seller = 'HFF' # examples: JF, HFF

vendor = "acme"

# input = "new" # example inputs: details, options, names, new, all, raw
# output = "product"
# extension = "tsv"

# arg = ''

# if arg == 'js':
# 	all_details = []
# elif arg == 'json':
	
# 	#all_items_json = [[{'item#':'sku1','collection':'col1'}]] # raw data field names unknwown so look for keywords in raw key/field name
# 	all_items_json = [[{'Catalog Year': 2022, 'Catalog Page': 1255, ' Item#': '00118', 'D E S C R I P T I O N': 'COMPUTER DESK', '2022\n  EAST PETE PRICE ': 77, '#PC/CTN': 1, 'Ctn GW\n(lbs)': 36, 'Carton CUFT': 3.48, 'Collection Name': 'Vincent'}]]
# 	all_details = generator.generate_catalog_from_json(all_items_json)
# else:
# 	if vendor == 'acme': # acme gives 3 separate sheets so combine to make catalog
# 		all_details = generator.generate_catalog_auto(vendor)
# 	else:
# 		all_details = generator.extract_data(vendor, input, extension)


# print as single string that can then be separated by semicolon delimiter
def display_shopify_variants(seller, vendor, all_details, product_titles, all_costs, all_barcodes, product_handles, product_tags, product_types, product_img_srcs, product_options, product_descrip_dict, all_skus, all_weights, all_weights_in_grams, import_tool = 'shopify', inv_tracker='', all_inv={}): # set import tool when calling to display the variants to be imported with the given import tool, bc they have different import orders although some do not care about order but use the title to determine field value match

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

		#body_html = product_descriptions[item_idx]
		body_html = product_descrip_dict[product_handle]

		# general fields
		sku = all_skus[item_idx]
		item_weight = all_weights[item_idx]

		# we only want to show inv qty if in ny otherwise would be confusing with inventory at other warehouses with different arrival times
		# so leave blank here and set to shopify if we have inventory in ny or no inventory at all
		# first check if we have any inventory or eta, bc simplest calculation
		
		# if it is stocked outside of ny, tracker='',qty=''
		vrnt_inv_tracker = '' # leave blank unless inv track capable. get input from generate all products, based on inventory abilities. for now with payment plan we only get 1 location so shopify is good enough
		vrnt_inv_qty = ''
		# if no stock or eta, then tracker=shopify and qty=0
		if not determine_stocked(sku, all_inv):
			print("Not Stocked")
			vrnt_inv_tracker = inv_tracker
			vrnt_inv_qty = '0'
		else: # we must have stock or eta
			# if we have stock in ny, tracker=shopify and qty=ny_qty
			location = 'ny' # only location currently, but could expand
			vrnt_inv_qty = generator.generate_vrnt_inv_qty(sku, all_inv, location)
			if int(vrnt_inv_qty) > 0:
				vrnt_inv_tracker = inv_tracker
			else:
				# we know it is stocked or eta, but not in ny bc ny has 0
				if vrnt_inv_tracker == '' and vrnt_inv_qty == '0': # we do not want to put 0 inventory bc it is stocked outside ny
					vrnt_inv_qty = ''

		print("vrnt_inv_tracker: " + vrnt_inv_tracker)
		print("vrnt_inv_qty: " + vrnt_inv_qty)

		vrnt_inv_policy = ''
		if import_tool == 'excelify':
			vrnt_inv_policy = 'continue'
		else:
			vrnt_inv_policy = 'deny'
		vrnt_weight_unit = 'lb'
		cmd = 'UPDATE'

		vrnt_price = generator.generate_vrnt_price(item_cost, product_type, seller) # seller tells us desired multiplier
		vrnt_compare_price = generator.generate_vrnt_compare_price(vrnt_price)

		# fields determined by request content/context
		published = 'TRUE'
		published_scope = 'global'

		

		final_item_info = ""
		if import_tool == 'shopify':
			# shopify specific fields
			standard_product_type = ''
			item_weight_in_grams = all_weights_in_grams[item_idx]
			
			vrnt_fulfill_service = 'manual'
			vrnt_req_ship = 'TRUE'
			vrnt_taxable = 'TRUE'
			img_position = ''
			img_alt = ''
			gift_card = 'FALSE'
			vrnt_tax_code = ''
			product_status = 'active'

			#print("product_type: " + product_type)

			vrnt_img = '' # still need to account for multiple img srcs given

			# each image needs a new row, but deal with that after sorted by size bc that function needs to isolate products and sort indices
			

			final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + vrnt_inv_tracker + ";" + vrnt_inv_qty + ";" + vrnt_inv_policy + ";" + vrnt_fulfill_service + ";" + vrnt_price + ";" + vrnt_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
			#print(final_item_info)
			all_final_item_info.append(final_item_info)
		elif import_tool == 'excelify':
			final_item_info = sku + ";" + product_handle + ";" + item_weight + ";" + item_cost + ";" + barcode + ";=" + body_html + ";" + product_option_string + ";" + product_tag_string + ";" + product_img_src + ";" + product_type + ";" + product_title + ";" + published + ";" + published_scope + ";" + vrnt_inv_tracker + ";" + vrnt_inv_policy + ";" + vrnt_weight_unit + ";" + cmd + ";" + vendor + ";" + vrnt_price + ";" + vrnt_compare_price

			#print(final_item_info)
			all_final_item_info.append(final_item_info)

	#print("\n===ALL FINAL ITEM INFO===\n" + str(all_final_item_info))

	#sorted_final_item_info = sort_items_by_size(all_final_item_info, "shopify") # we do not want to remove lines with same handles if they have different images
	sorted_final_item_info = sorter.sort_items_by_size(all_final_item_info, "shopify", all_details) # we do not want to remove lines with same handles if they have different images
	#sorted_final_item_info = all_final_item_info

	# shopify import tool needs imgs on different lines
	if import_tool == 'shopify':
		sorted_final_item_info = sorter.split_variants_by_img(sorted_final_item_info)

	writer.display_shopify_variant_headers()
	for item_info in sorted_final_item_info:
		print(item_info)

	return sorted_final_item_info



#all_final_item_info = display_shopify_variants() # currently uses all global variables. main fcn
#all_final_item_json = converter.convert_all_final_item_info_to_json(all_final_item_info)

#generator.write_data(all_final_item_info, vendor, output, extension)




# input: {}
def generate_all_products(vendor):
	print("\n===Generate All Products===\n")
	all_products = []

	seller = 'HFF'
	vendor = 'acme'
	import_tool = 'shopify' # based on seller. if can afford 3rd party, then likely not using shopify



	# ====== Inventory ======
	# need this inv info to add to description
	inventory_enabled = True # ask seller if separate tracking capable and if so what platform (eg zoho inventory)
	inv_tracker = ''
	product_inv_qtys = {}
	all_inv = {}
	if inventory_enabled:
		print("\n====== Inventory ======\n")
		# bc no standard order, this is dict with keys=location tied to qty
		all_inv = generator.generate_inv_from_data(vendor) # vendor to retrieve file
		
		inv_tracker = 'shopify'
		#product_inv_qtys = generator.generate_all_inv_qtys(all_inv)

	
	# at this point need to go per item in all details, 
	# get the sku and then check inventory
	# then if inventory, proceed to gather data for the item
	# otherwise, would generate much data only to find it is not in stock
	# if dictionary inefficient, consider making list of out of stock items
	# and then removing out of stock items from all details before proceeding
	all_details = generator.generate_catalog_from_data(vendor, all_inv) # catalog here corresponds to all_details in original product generator
	print("catalog: " + str(all_details))
	
	
	

	# generate product
	print("\n===Generate Product===\n")
	


	# store init item details untouched so we can detect measurement type based on input format of dimensions
	init_all_details = copy.deepcopy(all_details)

	# General Info from Details table
	all_skus = reader.format_field_values('sku', all_details)
	all_widths = reader.format_field_values('width', all_details, init_all_details)
	all_depths = reader.format_field_values('depth', all_details, init_all_details)
	all_heights = reader.format_field_values('height', all_details, init_all_details)
	all_weights = reader.format_field_values('weight', all_details, init_all_details)
	init_unit='lb'
	all_weights_in_grams = converter.convert_all_weights_to_grams(all_weights, init_unit) # shopify requires grams
	all_costs = reader.format_field_values('cost', all_details)
	all_barcodes = reader.format_field_values('barcode', all_details)
	all_img_srcs = reader.format_field_values('img', all_details)
	all_vrnt_imgs = reader.format_field_values('vrnt_img', all_details)


	# # ====== Shopify Product Catalog ======
	print("\n====== Shopify Product Catalog ======\n")

	#writer.display_all_item_details(init_all_details)

	# generate handles
	product_handles = generator.generate_all_handles(all_details) # formerly copied directly from catalog table but now made automatically from raw data descrip and collection name (if col name not given by vendor then look in product names table)
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
	#writer.display_field_values(product_img_srcs)

	# generate options
	product_options = generator.generate_all_options(all_details, init_all_details) # we need init details to detect measurement type
	#writer.display_field_values(product_options)
	#writer.display_all_item_details(init_all_details)

	

	# generate descriptions with dictionary
	product_descrip_dict = generator.generate_descrip_dict(all_details, init_all_details, all_inv, vendor)
	writer.display_field_values(product_descrip_dict)

	


	if inv_tracker == 'zoho':
		item_names = generator.generate_all_item_names(all_details, init_all_details) # generate item names
		item_collection_types = generator.generate_all_collection_types(all_details) # generate "inventory" types (formerly "collection" types)
		writer.display_zoho_items(item_names, item_collection_types, all_widths, all_depths, all_heights, all_skus, all_weights, vendor, all_details) # print as single string that can then be separated by comma delimiter




	# if inv 0, set inv tracker to shopify and inv qty to 0
	#all_products = ['handle;title;variant_sku;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30;31;32;33']
	all_products = display_shopify_variants(seller, vendor, all_details, product_titles, all_costs, all_barcodes, product_handles, product_tags, product_types, product_img_srcs, product_options, product_descrip_dict, all_skus, all_weights, all_weights_in_grams, import_tool, inv_tracker, all_inv)
	print("all_products: " + str(all_products))


	

	return all_products

# how do we know which files to include? we could go through all files in folder or go by given keywords
# how do we know file keywords? we know from vendor so use vendor as input
#file_keywords = ["price","spec","img","inv"] # equivalent to files selected on web format

product_import_rows = generate_all_products(vendor)