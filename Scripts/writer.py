# writer.py
# functions for a writer

import re

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
	if import_tool == 'shopify':
		product_variable_names = ["Handle", "Title", "Body (HTML)", "Vendor", "Standardized Product Type", "Custom Product Type", "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name","Option3 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Variant Image", "Variant Weight Unit", "Variant Tax Code", "Cost per item", "Status"]
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

def display_all_item_details(all_dtls):
	print("\n=== Item Details ===\n")
	for item_details in all_dtls:
		handle = item_details[handle_idx].strip().lower()

		print(handle + ": " + str(item_details))
	print()
