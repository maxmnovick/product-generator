# writer.py
# functions for a writer

import re
import sorter

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

def display_field_values(values):
	print("=== Display Field Values ===")
	for value in values:
		print(value)
	print()

def display_shopify_variant_headers(import_tool='shopify'):
	print("\n=== Shopify Variants == \n")
	product_variable_names = []
	if import_tool == 'shopify':
		# product category and type used to be standard product type and custom product type
		product_variable_names = ["Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name","Option3 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Variant Image", "Variant Weight Unit", "Variant Tax Code", "Cost per item", "Status"]
	elif import_tool == 'excelify':
		product_variable_names = ["Variant SKU","Handle","Variant Weight","Variant Cost","Variant Barcode","Body HTML","Option1 Name","Option1 Value","Option2 Name","Option2 Value","Option3 Name","Option3 Value","Tags","Image Src","Type","Title","Published","Published Scope","Variant Inventory Tracker","Variant Inventory Policy","Variant Weight Unit","Command","Vendor","Variant Price","Variant Compare At Price"]
	
	product_headers = ''
	for name_idx in range(len(product_variable_names)):
		name = product_variable_names[name_idx]
		if name_idx == 0:
			product_headers += name
		else:
			product_headers += ";" + name
	print(product_headers)

def display_zoho_item_headers():
	product_variable_names = ["SKU","Item Name","Package Width","Package Depth","Package Height","Package Weight","Type","Reference Number","Account","Reason","Vendor","Date","Warehouse Name","Description","Quantity Adjusted"]
	product_headers = ''
	for name_idx in range(len(product_variable_names)):
		name = product_variable_names[name_idx]
		if name_idx == 0:
			product_headers += name
		else:
			product_headers += ";" + name
	print(product_headers)

def display_catalog_headers():

	product_variable_names = ["SKU", "Collection", "Type", "Intro", "Colors", "Materials", "Finish", "Width", "Depth", "Height", "Weight (lb)", "Features", "Cost", "Image Link", "Barcode"]
	
	product_headers = ''
	for name_idx in range(len(product_variable_names)):
		name = product_variable_names[name_idx]
		if name_idx == 0:
			product_headers += name
		else:
			product_headers += ";" + name
	print(product_headers)

# replace commas with semicolons for shopify import and add commas if needed to allow space for 3 options
def format_option_string(init_option_string):
	option_string = ''

	option_string = re.sub(',',';',init_option_string)
	product_option_data = option_string.split(";")
	# make sure always 3 option spaces, even if less than 3 options
	max_options = 3 # limited by shopify
	num_option_fields = 2 * max_options # name and value for each option
	# if we already have maximum number of options, do nothing
	num_defined_option_fields = len(product_option_data) # number of fields filled in with either name or value
	if num_defined_option_fields != num_option_fields:
		# add spaces for options, so count defined options so we know difference
		num_blank_option_fields = num_option_fields - num_defined_option_fields
		for blank_option in range(num_blank_option_fields):
			option_string += ';' # original maybe "size;king" so final would be "size;king;;;;"

	return option_string

# separate data with semicolons for shopify import and add commas if needed to allow space for 3 options
def format_option_string_from_data(option_data): # [[names],[vals]]
	print("\n===Format Option String from Data===\n")
	print("option_data: " + str(option_data))
	option_string = ''
	opt_names = option_data[0]
	opt_vals = option_data[1]

	#init_opt_string = ''
	for opt_idx in range(len(opt_names)):
		if opt_idx == 0:
			option_string += opt_names[opt_idx] + ";" + opt_vals[opt_idx]
		else:
			option_string += ";" + opt_names[opt_idx] + ";" + opt_vals[opt_idx]

	option_string = format_option_string(option_string)

	# max_opts = 3 # limited by shopify
	# num_blank_opts = max_opts - len(opt_names)
	# for opt_idx in range(len(opt_names)):
	# 	if opt_idx == 0:
	# 		option_string += opt_names[opt_idx] + ";" + opt_vals[opt_idx]
	# 	else:
	# 		option_string += ";" + opt_names[opt_idx] + ";" + opt_vals[opt_idx]
	# for opt_idx in range(num_blank_opts):
	# 	if opt_idx == 0:
	# 		option_string += ";;"
	# 	else:
	# 		option_string += ";;"

	print("option_string: " + option_string)
	return option_string

def display_all_item_details(all_dtls):
	print("\n=== Item Details ===\n")
	for item_details in all_dtls:
		handle = item_details[handle_idx].strip().lower()

		print(handle + ": " + str(item_details))
	print()

# originally based on capitalizing sentences for an intro paragraph
def capitalize_sentences(intro):

	#===\n")

	final_sentences = ''

	intro_sentences = re.split("\\.|!",intro) #intro.split('.')
	#print("intro_sentences: " + str(intro_sentences))
	for sentence in intro_sentences:
		#print("sentence: " + sentence)
		if len(sentence) > 1: # if space after last sentence then there will be a blank last element which should not be taken
			
			sentence = sentence.strip()
			#print("sentence: \'" + sentence + '\'')

			# if sentence starts with numerals or special characters, get idx of first letter
			first_letter_idx = 0

			first_letter = re.search('\\w', sentence)
			if first_letter is not None:
				first_letter_idx = first_letter.start()
			#print("first_letter_idx: " + str(first_letter_idx))
			if first_letter_idx == 0:
				sentence = sentence[first_letter_idx].upper() + sentence[first_letter_idx+1:] + '. '
			else:
				sentence = sentence[:first_letter_idx] + sentence[first_letter_idx].upper() + sentence[first_letter_idx+1:] + '. ' #sentence = sentence.strip().capitalize() + '. '
			final_sentences += sentence

	#print("final_sentences: " + final_sentences)
	return final_sentences


# print as single string that can then be separated by comma delimiter
def display_zoho_items(item_names, item_collection_types, all_widths, all_depths, all_heights, all_skus, all_weights, vendor, all_details):

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
	sorted_final_item_info = sorter.sort_items_by_size(all_final_item_info, import_type, all_details)
	#sorted_final_item_info = all_final_item_info

	display_zoho_item_headers()
	for item_info in sorted_final_item_info:
		print(item_info)

# fill in blank options bc always need same number limited by product import tool or ecom platform
# opt_data = [[names],[vals]]
def format_option_data(opt_data):
	print("\n===Format Option Data===\n")
	final_opt_data = []
	opt_names = opt_data[0]
	opt_vals = opt_data[1]
	num_options = 3
	for opt_idx in range(num_options):
		if len(opt_names) <= opt_idx:
			opt_names.append('')
			opt_vals.append('')

	final_opt_data = [opt_names, opt_vals]

	print("final_opt_data: " + str(final_opt_data))
	return final_opt_data
