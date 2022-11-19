# generator.py
# functions for a generator

import reader, writer, determiner # custom
import re, datetime, math, random, pandas
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

# order of shopify import fields
import_sku_idx = 0
import_handle_idx = 1
import_opt1_name_idx = 6
import_opt1_val_idx = 7
import_opt2_name_idx = 8
import_opt2_val_idx = 9
import_opt3_name_idx = 10
import_opt3_val_idx = 11

# order of zoho import fields
item_name_idx = 1

# get data from a file and format into a list, for specific vendors with different formats (same as reader version of this fcn but more specific)
def extract_data(vendor, input, extension):
	catalog_filename = ''
	if input == "name":
		catalog_filename = "../Data/product-names - " + vendor + "." + extension
	elif input == "options" or input == "descrips":
		catalog_filename = "../Data/" + vendor + "-product-import - " + input.capitalize() + "." + extension
	else:
		vendor = re.sub(' ','-',vendor)
		catalog_filename = catalog_filename = "../Data/" + vendor + "-catalog - " + input.capitalize() + "." + extension

	lines = []
	data = []
	all_data = []

	with open(catalog_filename, encoding="UTF8") as catalog_file:

		current_line = ""
		for catalog_info in catalog_file:
			current_line = catalog_info.strip()
			lines.append(current_line)

		catalog_file.close()

	# skip header line
	for line in lines[1:]:
		if len(line) > 0:
			if extension == "csv":
				data = line.split(",")
			else:
				data = line.split("\t")
		all_data.append(data)

	return all_data

# write data from a list into a file
def write_data(arranged_data, vendor, output, extension):
	output = re.sub(' ','-',output)
	vendor = re.sub(' ','-',vendor)
	catalog_filename = "../Data/" + vendor + "-" + output + "-import." + extension
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	for row_idx in range(len(arranged_data)):
		catalog_file.write(arranged_data[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()

# generate handles based on descriptions or titles (see handle-generator.py)
def generate_handle(item_details):
	#print("\n===Generate Handle===\n")
	item_sku = item_details[sku_idx]

	# descrip of what type of furniture needed to make title
	descrip = final_title_suffix = final_handle_suffix = final_handle = ''

	output = "title"
	all_keywords = reader.read_keywords(output)

	if len(item_details) > 0:
		# need to know field number in given table (in this case catalog table but could also use product names table)
		sku = item_details[sku_idx]
		descrip = item_details[title_idx]
		collection_name = item_details[collection_idx]

		# get features to check if a table is round bc not always differentiated bt round and rect tables in same collection
		features = item_details[features_idx]

		# keywords in form without dashes so remove excess from descrip to compare to keywords
		plain_descrip = descrip.lower().strip()
		plain_features = features.lower().strip()

		for title_suffix, title_keywords in all_keywords.items():
			#print("Title Suffix: " + title_suffix)
			#print("Title Keywords: " + str(title_keywords))
			for keyword in title_keywords:
				#print("Keyword: " + keyword + "\n")
				if re.search(keyword,plain_descrip):
					final_title_suffix = title_suffix
					break

			if final_title_suffix != '':
				break

		# replace "table" with "round table" if "round" mentioned in features of table but not in title/type/descrip (3 different names for the same field is confusing!)
		if re.search("table", final_title_suffix) and not re.search("round", final_title_suffix):
			#print("\n\nfound table in title but not round, so check if it is round!!!\n\n")
			#print("final_title_suffix before: " + final_title_suffix)
			if re.search("round", plain_features):
				final_title_suffix = re.sub(r"(.*\s)table", r"round \1table", final_title_suffix)
		#print("final_title_suffix after: " + final_title_suffix)

		# warn user if no matching keyword
		if final_title_suffix == '':
			print("WARNING: No matching keyword for product when generating handle " + item_sku)

		# go from title format to handle format by adding dashes b/t words, b/c already lowercase
		final_handle_suffix = re.sub(' ','-',final_title_suffix)
		#print("Final Handle Suffix: " + final_handle_suffix)
		collection_name = re.sub(' ','-',collection_name)

		final_handle = collection_name.lower() + "-" + final_handle_suffix
	else:
		print("Warning: No details for this item!")

	return final_handle

# generate all handles for a set of products
def generate_all_handles(all_details):
	all_handles = []

	for item_details in all_details:
		handle = generate_handle(item_details)
		all_handles.append(handle)

	return all_handles

# title is based on handle
# so do we need to add generate handle fcn here or just pass it the handle as a param?
# it simplifies the params if only given item details and it is more robust only if it was reading the title of the column/field whereas right now it is given a set column coordinate
def generate_title(item_details, handle=''):
	handle = title = ''

	if len(item_details) > 0:
		if handle == '':
			handle = generate_handle(item_details)

		#print("Handle: " + handle)

		if handle != '':
			handle_words = re.split('-',handle)
			#print("Handle Words: " + str(handle_words))

			for word in handle_words:
				roman_numerals = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
				if word.upper() in roman_numerals:
					word = word.upper()
				else:
					word = word.capitalize()
				title += word + ' '
			title = title.rstrip()
			#print(title)
		else:
			print("Warning: Blank handle while generating title, so the title was set to an empty string (title = '')!")
	else:
		print("Warning: No Details found for this item while generating title!")

	return title

# generate all titles for a set of products
def generate_all_titles(all_details, all_handles=[]):
	all_titles = []

	handle = ''
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		if len(all_handles) == len(all_details):
			handle = all_handles[item_idx]
		title = generate_title(item_details, handle)
		all_titles.append(title)

	return all_titles

# tags based on vendor, publication year, color, material, and finish
def generate_tags(item_details, vendor):
	now = datetime.datetime.now()
	publication_year = str(now.year) # get current year

	sku = handle = colors = materials = finishes = ''

	color_data = []
	material_data = []
	finish_data = []

	tags = color_tags = material_tags = finish_tags = ''

	if len(item_details) > 0:
		sku = item_details[0].strip().lower()
		handle = item_details[1].strip().lower()
		colors = item_details[4].strip().lower()
		#print("Colors: " + colors)
		materials = item_details[5].strip().lower()
		materials = re.sub('full ','',materials)
		materials = re.sub(' front','',materials)
		materials = re.sub(' back','',materials)
		#print("Materials: " + materials)
		finishes = item_details[6].strip().lower()
		#print("Finishes: " + finishes)

	if colors != "n/a":
		color_data = re.split(',|/|&|\\band|\\bwith',colors)
	#print("Color Data: " + str(color_data))
	if materials != "n/a":
		material_data = re.split(',|/|&|\\band|\\bwith',materials)
	#print("Material Data: " + str(material_data))
	if finishes != "n/a":
		finish_data = re.split(',|/|&|\\band|\\bwith',finishes)
	#print("Finish Data: " + str(finish_data))

	for color in color_data:
		color = color.strip()
		color = color.rstrip(' -') # for Global but maybe also for others
		color = color.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if color != '':
			color_tags += "Color: " + color.title() + ", "
	color_tags = color_tags.rstrip(', ')
	#print("Color Tags: " + color_tags)
	for material in material_data:
		material = material.strip()
		material = material.rstrip(' -') # for Global but maybe also for others
		material = material.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if material != '':
			material_tags += "Material: " + material.title() + ", "
	material_tags = material_tags.rstrip(', ')
	#print("Material Tags: " + material_tags)
	for finish in finish_data:
		finish = finish.strip()
		finish = finish.rstrip(' -') # for Global but maybe also for others
		finish = finish.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if finish != '':
			finish_tags += "Finish: " + finish.title() + ", "
	finish_tags = finish_tags.rstrip(', ')
	#print("Finish Tags: " + finish_tags)

	
	tags = vendor.title() + " " + publication_year # desired space bt vendor and pub yr in case vendor name has multiple parts

	if colors != "n/a":
		tags += ", " + color_tags

	if materials != "n/a":
		tags += ", " + material_tags

	if finishes != "n/a":
		tags += ", " + finish_tags

	return tags

def generate_all_tags(all_details, vendor):
	all_tags = []

	for item_details in all_details:
		tags = generate_tags(item_details, vendor)
		all_tags.append(tags)

	return all_tags

def generate_product_type(item_details):
	handle = final_type = ''

	handle_data = []

	output = "type"
	all_keywords = reader.read_keywords(output)

	# look at item handle to determine type
	if len(item_details) > 0:
		handle = generate_handle(item_details) #item_details[1].strip().lower() # need to know field number in given table

		if handle != '':
			# keywords in form without dashes so remove dashes from handle to compare to keywords
			dashless_handle = re.sub('-', ' ', handle)

			for type, type_keywords in all_keywords.items():
				#print("Type: " + type)
				#print("Type Keywords: " + str(type_keywords))
				for keyword in type_keywords:
					#print("Keyword: " + keyword)
					if re.search(keyword,dashless_handle):
						final_type = type
						break

				if final_type != '':
					break
		else:
			print("Warning: Blank handle while generating type, so the type was set to an empty string (type = '')!")
	else:
		print("Warning: No details for this item!")

	return final_type.title()

def generate_all_product_types(all_details):
	all_product_types = []

	for item_details in all_details:
		types = generate_product_type(item_details)
		all_product_types.append(types)

	return all_product_types

def generate_product_img_src(item_details):

	img_src = item_details[img_src_idx]

	if re.search('drive.google.com',img_src):
		# extract ID
		img_id = re.sub("https://drive.google.com/file/d/|/view\?usp=sharing","",img_src)
		#img_id = re.sub("/view\?usp=sharing","",img_id)
		print("img_id: " + img_id)

		img_src = "https://drive.google.com/uc?export=view&id=" + img_id

	return img_src

def generate_all_product_img_srcs(all_details):
	all_product_img_srcs = []

	for item_details in all_details:
		img_srcs = generate_product_img_src(item_details)
		all_product_img_srcs.append(img_srcs)

	return all_product_img_srcs

def generate_options(item_details, init_item_details):

	#print("\n=== Generate Options ===\n")

	init_width = init_item_details[width_idx].strip().lower()
	#print("Init Width: " + init_width)
	handle = item_details[handle_idx]
	meas_type = reader.determine_measurement_type(init_width, handle)

	sku = color = title = ''

	output = "option"
	all_keywords = reader.read_keywords(output)

	final_opt_names = []
	final_opt_values = []

	# look at item sku to determine options
	# if nothing apparent from sku, then check other fields like color and material
	# do not rely entirely on sku b/c could be ambiguous codes that may appear as part of other words not meant to indicate options
	# example: W is code for wenge brown for vendor=Global, but W is likely to mean something else for other vendors
	if len(item_details) > 0:
		sku = item_details[0].strip().lower()
		#print("===Generate Options for SKU: " + sku)
		title = item_details[2].strip().lower()
		color = item_details[4].strip().lower()
		#print("Color: " + color)

		# option codes must only be considered valid when they are the entire word in the sku, so must remove dashes to separate words and isolate codes
		dashless_sku = re.sub('-',' ',sku)

		final_opt_string = ''

		type = generate_product_type(item_details)
		if type == 'rugs':
			option_name = 'Size' # width-depth combos are options for rugs
			# see if dims given
			width = item_details[width_idx].strip()
			depth = item_details[depth_idx].strip()
			if width != 'n/a' and depth != 'n/a':
				dim_string = width + "\" x " + depth + "\""
				if meas_type == 'round':
					dim_string = width + "\" Diameter"
				final_opt_values.append(dim_string)
				final_opt_names.append(option_name)

		# loop for each type of option, b/c need to fill in value for each possible option (eg loop for size and then loop for color in case item has both size and color options)
		for option_name, option_dict in all_keywords.items():
			#print("======Check for Option Name: " + option_name)
			#print("Option Dict: " + str(option_dict))

			final_opt_value = ''

			for option_value, option_keywords in option_dict.items():
				#print("Option Value: " + option_value)
				#print("Option Keywords: " + str(option_keywords))

				for keyword in option_keywords:
					#print("Keyword: " + keyword)
					#print("Plain SKU: " + dashless_sku)
					if re.search(keyword,dashless_sku):
						final_opt_value = option_value
						final_opt_values.append(final_opt_value)

						final_opt_names.append(option_name)

						final_opt_string += option_name + "," + final_opt_value + ","
						break

					# if no codes found in sku, check other fields for this item such as title field
					if re.search(keyword,title):
						final_opt_value = option_value
						final_opt_values.append(final_opt_value)

						final_opt_names.append(option_name)

						final_opt_string += option_name + "," + final_opt_value + ","
						break

					# if no codes found in sku, check other fields for this item such as color field
					if re.search(keyword,color):
						final_opt_value = option_value
						final_opt_values.append(final_opt_value)

						final_opt_names.append(option_name)

						final_opt_string += option_name + "," + final_opt_value + ","
						break

				if final_opt_value != '':
					#print("Final Option Name: " + option_name)
					#print("Final Option Value: " + final_opt_value)
					#print("Option String: " + final_opt_string + "\n")
					break

			#print("======Checked for Option Name: " + option_name + "\n")\



		#print("===Generated Options for SKU: " + sku + "\n")
	else:
		print("Warning: No details for this item!")

	final_opt_data = [ final_opt_names, final_opt_values ]

	#print("=== Generated Options ===\n")

	return final_opt_data

def generate_all_options(all_details, init_all_details):
	all_options = []

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		init_item_details = init_all_details[item_idx]

		options = generate_options(item_details, init_item_details) # we need init details to detect measurement type
		option_names = options[0]
		option_values = options[1]
		#print("Options: " + str(options))
		option_string = ''
		for opt_idx in range(len(option_names)):
			option_name = option_names[opt_idx]
			option_value = option_values[opt_idx]
			if opt_idx == 0:
				option_string += option_name + "," + option_value
			else:
				option_string += "," + option_name + "," + option_value
		all_options.append(option_string)

	return all_options

def generate_description_instances(product, init_product):
	print("\n===Generate Description Instances===\n")

	descrip_instances = []

	body_html = ""

	html_descrip = True # user input based on spreadsheet tool. we want to use html bc we need to make a table format for data. 
	
	if html_descrip == True:
		
		intro_html = generate_intro_html(product)

		colors_html = generate_colors_html(product,init_product)

		materials_html = generate_materials_html(product)

		finishes_html = generate_finishes_html(product)

		dimensions_html = generate_dimensions_html(product,init_product)

		features_html = generate_features_html(product)

		#arrival_html = generate_arrival_html(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

		descrip_html = intro_html + colors_html + materials_html + finishes_html + dimensions_html + features_html
		body_html = descrip_html

	elif html_descrip == False:

		intro_fmla = generate_intro_fmla(product)

		colors_fmla = generate_colors_fmla(product,init_product)

		materials_fmla = generate_materials_fmla(product)

		finishes_fmla = generate_finishes_fmla(product)

		dimensions_fmla = generate_dimensions_fmla(product,init_product)

		features_fmla = generate_features_fmla(product)

		#arrival_fmla = generate_arrival_fmla(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

		descrip_fmla = "=CONCATENATE(" + intro_fmla  + ",CHAR(10)," + colors_fmla  + ",CHAR(10)," + materials_fmla  + ",CHAR(10)," + finishes_fmla  + ",CHAR(10)," + dimensions_fmla + ",CHAR(10)," + features_fmla + ")"
		body_html = descrip_fmla

	# all variants of the product get the same description
	# the variants must be ordered by options, based on knowledge of desired option order and available options
	for variant in product:
		descrip_instances.append(body_html)

	# instead of saving description instances and relying on them to align with product variants, 
	# make dictionary matching description to product handle
	# and then when setting the description, use the product handle as the key
	#descrip_dict[handle] = body_html
	# see generate_descrip_dict()

	return descrip_instances

def generate_all_descriptions(all_details, init_all_details):
	print("\n===Generate All Descriptions===\n")
	all_descriptions = []

	init_products = isolate_products(init_all_details)
	products = isolate_products(all_details) # why isolate products and not go line by line in all details?

	for product_idx in range(len(products)):
		product = products[product_idx]
		init_product = init_products[product_idx]
		descrip_instances = generate_description_instances(product, init_product)
		for descrip_instance in descrip_instances:
			all_descriptions.append(descrip_instance)

	return all_descriptions

# instead of saving description instances and relying on them to align with product variants, 
# make dictionary matching description to product handle
# and then when setting the description, use the product handle as the key
def generate_description(product, init_product):
	print("\n===Generate Description===\n")

	descrip_instances = []

	body_html = ""

	html_descrip = True # user input based on spreadsheet tool. we want to use html bc we need to make a table format for data. 
	
	if html_descrip == True:
		
		intro_html = generate_intro_html(product)

		colors_html = generate_colors_html(product,init_product)

		materials_html = generate_materials_html(product)

		finishes_html = generate_finishes_html(product)

		dimensions_html = generate_dimensions_html(product,init_product)

		features_html = generate_features_html(product)

		#arrival_html = generate_arrival_html(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

		descrip_html = intro_html + colors_html + materials_html + finishes_html + dimensions_html + features_html
		body_html = descrip_html

	elif html_descrip == False:

		intro_fmla = generate_intro_fmla(product)

		colors_fmla = generate_colors_fmla(product,init_product)

		materials_fmla = generate_materials_fmla(product)

		finishes_fmla = generate_finishes_fmla(product)

		dimensions_fmla = generate_dimensions_fmla(product,init_product)

		features_fmla = generate_features_fmla(product)

		#arrival_fmla = generate_arrival_fmla(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

		descrip_fmla = "=CONCATENATE(" + intro_fmla  + ",CHAR(10)," + colors_fmla  + ",CHAR(10)," + materials_fmla  + ",CHAR(10)," + finishes_fmla  + ",CHAR(10)," + dimensions_fmla + ",CHAR(10)," + features_fmla + ")"
		body_html = descrip_fmla

	

	return body_html

# products = { "<sku>": { "handle":"<handle>", "description":"<description>"  } }
# dict = { <handle>:<description> }
def generate_descrip_dict(all_details, init_all_details):
	print("\n===Generate Description Dictionary===\n")
	# instead of saving description instances and relying on them to align with product variants, 
	# make dictionary matching description to product handle
	# and then when setting the description, use the product handle as the key
	descrip_dict = {}
	

	init_products = isolate_products(init_all_details)
	products = isolate_products(all_details) # why isolate products and not go line by line in all details?

	for product_idx in range(len(products)):
		product = products[product_idx]
		item_details = product[0]
		handle = generate_handle(item_details)
		print("handle: " + handle)
		init_product = init_products[product_idx]
		descrip = generate_description(product, init_product)

		descrip_dict[handle] = descrip

	print("descrip_dict: " + str(descrip_dict))
	return descrip_dict

def generate_item_name(item_details, init_item_details):
	final_name = ''

	# look at item handle to determine title, and other details to determine options
	if len(item_details) > 0:

		product_title = generate_title(item_details)
		#print("Product Title: " + product_title)
		final_name += product_title

		option_data = generate_options(item_details, init_item_details)
		option_values = []
		if len(option_data) > 0:
			option_values = option_data[1]
			#print("Option Values: " + str(option_values))

		for value in option_values:
			final_name += "/" + value

	else:
		print("Warning: No details for this item!")

	#print("Final Name: " + final_name + "\n")
	return final_name

def generate_all_item_names(all_details, init_all_details):
	all_item_names = []

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		init_item_details = init_all_details[item_idx]

		item_name = generate_item_name(item_details, init_item_details)
		all_item_names.append(item_name)

	return all_item_names

def generate_collection_type(item_details):
	final_collection_type = ''

	output = "collection type"
	all_keywords = reader.read_keywords(output)

	# look at item handle to determine type
	if len(item_details) > 0:
		product_type = generate_product_type(item_details)

		for type, type_keywords in all_keywords.items():
			#print("Type: " + type)
			#print("Type Keywords: " + str(type_keywords))
			for keyword in type_keywords:
				#print("Keyword: " + keyword)
				if re.search(keyword,product_type):
					final_collection_type = type
					break

			if final_collection_type != '':
				break
	else:
		print("Warning: No details for this item!")

	#print(product_type + ", " + final_collection_type)
	return final_collection_type

def generate_all_collection_types(all_details):
	all_collection_types = []

	for item_details in all_details:
		collection_type = generate_collection_type(item_details)
		all_collection_types.append(collection_type)

	return all_collection_types

# extract options from product string and format as string
def generate_option_string(raw_product_string):

	option_string = ''

	max_options =  3

	raw_product_data = raw_product_string.split(';')

	init_opt_idx = import_opt1_name_idx
	for opt_idx in range(max_options):
		opt_name_idx = init_opt_idx + opt_idx * 2
		opt_val_idx = init_opt_idx + 1 + opt_idx * 2
		opt_name = raw_product_data[opt_name_idx]
		opt_val = raw_product_data[opt_val_idx]

		if opt_idx == 0:
			option_string += opt_name + ";" + opt_val
		else:
			option_string += ";" + opt_name + ";" + opt_val

	return option_string

# isolate unique variants by comparing option lists such as "["Size","10'x10'"]"
# def isolate_unique_variants(raw_product_vrnt_strings):
# 	print("\n=== Isolate Unique Variants ===\n")
#
# 	option_string = generate_option_string(raw_product_string)
#
#
#
# 	print("\n=== Isolated Unique Variants ===\n")

def get_unique_vrnt_idx(question_variant, sorted_product):
	unique_vrnt_idx = 0

	for vrnt_idx in range(len(sorted_product)):
		variant = sorted_product[vrnt_idx]
		if variant == question_variant:
			unique_vrnt_idx = vrnt_idx
			break

	#print("Unique Variant Index: " + str(unique_vrnt_idx))

	return unique_vrnt_idx

# def count_max_product_options(sorted_product, import_type):
# 	max_product_options = num_product_options = 0
#
# 	all_num_product_opts = []
#
# 	for vrnt_idx in range(len(sorted_product)):
# 		num_product_options = 0
#
# 		variant = sorted_product[vrnt_idx]
# 		vrnt_data = variant.split(';')
#
# 		relevant_vrnt_data = vrnt_data[6:12]
# 		if import_type == 'zoho':
# 			item_name = vrnt_data[item_name_idx]
#
# 			relevant_vrnt_data = item_name.split("/")
# 			relevant_vrnt_data = relevant_vrnt_data[1:]
#
# 		print("Variant Data: " + str(relevant_vrnt_data))
#
# 		for opt_idx in range(len(relevant_vrnt_data)):
# 			opt_name_or_value = relevant_vrnt_data[opt_idx]
# 			if import_type == 'zoho':
# 				if opt_name_or_value != '':
# 					num_product_options += 1
# 			else:
# 				# if even number idx then check if empty
# 				if opt_idx % 2 == 0:
# 					if opt_name_or_value != '':
# 						num_product_options += 1
#
# 		all_num_product_opts.append(num_product_options)
#
# 	max_product_options = max(all_num_product_opts)
#
# 	print("Max Product Options: " + str(max_product_options))
# 	return max_product_options
#
#
# def count_variant_options(question_variant, import_type):
# 	num_vrnt_opts = 0
#
# 	vrnt_data = question_variant.split(';')
#
# 	#print("Variant Data: " + str(vrnt_data[6:12]))
# 	#print("Question Variant Data: " + str(q_vrnt_data[6:12]))
# 	#print()
#
# 	relevant_vrnt_data = vrnt_data[6:12]
# 	if import_type == 'zoho':
# 		item_name = vrnt_data[item_name_idx]
#
# 		relevant_vrnt_data = item_name.split("/")
# 		relevant_vrnt_data = relevant_vrnt_data[1:]
#
# 	for opt_idx in range(len(relevant_vrnt_data)):
# 		opt_name_or_value = relevant_vrnt_data[opt_idx]
# 		if import_type == 'zoho':
# 			if opt_name_or_value != '':
# 				num_vrnt_opts += 1
# 		else:
# 			# if even number idx then check if empty
# 			if opt_idx % 2 == 0:
# 				if opt_name_or_value != '':
# 					num_vrnt_opts += 1
#
# 	print("Num Variant Options: " + str(num_vrnt_opts))
# 	return num_vrnt_opts

def determine_unique_variant(question_variant, sorted_product, import_type):

	unique_vrnt = True

	# max_product_options = count_max_product_options(sorted_product, import_type)
	# num_variant_options = count_variant_options(question_variant, import_type)
	# print()

	#print("Question Variant: " + question_variant)

	q_vrnt_data = question_variant.split(';')
	#print("Question Variant Data: " + str(q_vrnt_data))
	#print()

	unique_vrnt_idx = get_unique_vrnt_idx(question_variant, sorted_product)

	# we know that sku might actually be different (idx=0) but if the rest of the line is the same then it is a duplicate variant
	# really we just need the option data but the whole string should be the same
	# actually the option data may be the same but the image may be different bc we need one row per image
	for vrnt_idx in range(len(sorted_product)):
		variant = sorted_product[vrnt_idx]
		vrnt_data = variant.split(';')

		#print("Variant Data: " + str(vrnt_data[6:12]))
		#print("Question Variant Data: " + str(q_vrnt_data[6:12]))
		#print()

		# should the whole line match or just the options? we need at least options and image to match to know it is duplicate but more robust would be whole line
		relevant_vrnt_data = vrnt_data #vrnt_data[6:12]
		relevant_q_vrnt_data = q_vrnt_data #q_vrnt_data[6:12]
		if import_type == 'zoho':
			item_name = vrnt_data[item_name_idx]
			q_item_name = q_vrnt_data[item_name_idx]

			relevant_vrnt_data = item_name.split("/")
			relevant_q_vrnt_data = q_item_name.split("/")

		if relevant_vrnt_data == relevant_q_vrnt_data: # remember last item is not included in range
			#print("Variant Data = Question Variant Data so could be duplicate variant.")
			if vrnt_idx != unique_vrnt_idx and vrnt_idx < unique_vrnt_idx:
				#print("New Variant matches an Earlier Variant (" + str(vrnt_idx) + " != " + str(unique_vrnt_idx) + "), so duplicate variant!")
				unique_vrnt = False
				break

	#print("Unique Variant? " + str(unique_vrnt) + "\n")

	return unique_vrnt

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

def isolate_product_from_details(all_details, start_idx, stop_idx):
	product_rows = []

	for variant_idx in range(start_idx, stop_idx):
		product_rows.append(all_details[variant_idx])

	return product_rows

def isolate_products(all_details):
	products = []

	field_title = "handle" # we know that all variants of the same product have the same handle

	#handles = np.array(isolate_detail_field(all_details, field_title))
	handles = np.array(generate_all_handles(all_details))

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

# originally based on capitalizing sentences for an intro paragraph
def capitalize_sentences(intro):

	#===\n")

	final_sentences = ''

	intro_sentences = intro.split('.')
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

def generate_intro(item_details):
	intro = ''

	# intro variables based on item details
	product_type = generate_product_type(item_details)

	room_type = 'room'
	product_name = str.capitalize(item_details[collection_idx]) #'this product'
	room_activity = 'living'

	# parts of speech change based on product type
	pronoun = 'your'

	# make map matching product type to room type
	if product_type == 'sofas':
		room_type = 'living room'

	if room_type == 'room':
		pronoun = 'its'

	product_type = product_type.lower() # make lowercase unless start of sentence bc source uses uppercase as it is a grouping by Type
	product_type_singular = product_type
	if product_type == '':
		product_type = product_type_singular = 'pieces'

	elif product_type[-1] == 's':
		product_type_singular = product_type[:-1]


	intro1 = 'This exceptional ' + product_type_singular + ' will make ' + pronoun + ' ' + room_type + ' the most delightful room in your home'

	intro2 = str.capitalize(product_name) + ' is here to help with your design problem. Available in our most popular materials for speedier delivery, this distinguished ' + product_type_singular + ' is elegant, traditional, and crafted by hand, just the way you would expect our preeminent ' + product_type + ' to be'

	intro3 = 'Elegant ' + room_activity + ' is ' + product_name + '\'s speciality—so much so that you\'ll want to keep it forever. From all sides, you see a graceful shape that is perfectly balanced and sturdy, while being exceptionally refined'

	intro_templates = [intro1, intro2, intro3]

	intro = random.choice(intro_templates)

	#print(intro)

	return intro

def generate_intro_fmla(product):
	intro_fmla = "\"\""

	for variant in product:

		intro = ''

		if len(variant) > 3:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			intro = variant[3].strip().lower()
			print("Intro: " + intro)
			# if no intro given then generate one
			if intro == '' or intro == 'intro':
				intro = generate_intro(variant)

		if intro != '' and intro != 'n/a':
			intro = capitalize_sentences(intro)
			intro = re.sub('\"','\",CHAR(34),\"', intro) # if quotes found in intro, such as for dimensions, then fmla will incorrectly interpret that as closing string
			intro_fmla = "\"" + intro + "\""
		#print("Intro Formula: " + intro_fmla)

	return intro_fmla

def generate_intro_html(product):
	print("\n===Generate Intro HTML===\n")
	intro_html = ''

	for variant in product:

		intro = ''

		if len(variant) > 3: # if variant contains intro data. todo: make it check for intro keyord instead of index.
			handle = generate_handle(variant) #variant[1].strip().lower()
			#print("Handle: " + handle)
			#print("Handle: " + handle)
			intro = variant[3].strip().lower()
			#print("Initial Intro: " + intro)
			# if no intro given then generate one
			# if only word given, assume error bc intro cannot be one word
			# for example some of Acme intros are '<span>' for unknown reason
			if intro == '' or intro == 'intro' or intro == 'n/a' or not re.search('\\s',intro):
				intro = generate_intro(variant)

		# check if intro blank
		if intro != '' and intro != 'n/a':
			intro = capitalize_sentences(intro)
			#intro = re.sub('\"','\",CHAR(34),\"', intro) # if quotes found in intro, such as for dimensions, then fmla will incorrectly interpret that as closing string
			intro_html = "<p>" + intro + "</p>"
			break # once we make an intro for the product we dont need to loop thru any more variants because they all get the same intro
		#print("Intro HTML: " + intro_html)

	return intro_html

def determine_given_colors(product_details):
	given_colors = True

	for variant_details in product_details:
		colors = ''

		if len(variant_details) > 4:
			colors = variant_details[4].strip()

			if colors == '' or colors.lower() == 'n/a':
				# no colors given
				given_colors = False

		else:
			given_colors = False

	return given_colors

def generate_colors_fmla(product, init_product):

	final_colors_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_colors(product): # if we are NOT given colors we do not include colors in the description
		final_colors_fmla = "\"Colors: \"" # only if at least 1 of the variants has colors

		opt_name = 'Color' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		color_options = options[opt_name]
		#print("Color Options: " + str(color_options))

		valid_opt = False

		colors_fmla = ''

		for vrnt_idx in range(len(product)):
			variant = product[vrnt_idx]
			init_variant = init_product[vrnt_idx]

			valid_opt = False

			colors = ''

			if len(variant) > 4:
				handle = variant[1].strip().lower()
				#print("Handle: " + handle)
				colors = variant[4].strip().lower()
				#print("Colors: " + colors)

			colors_fmla = '\"\"' # init option fmla so if no value given it is empty quotes
			if colors != '' and colors != 'n/a':
				colors = re.sub('\"','\",CHAR(34),\"', colors) # if something like "red" brown is given as colors, then fmla will incorrectly interpret that as closing string
				colors_fmla = "\"" + colors + "\""
			#print("Colors Formula: " + colors_fmla)

			option_data = generate_options(variant, init_variant)

			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				#print("Option Names: " + str(option_names))
				option_values = option_data[1]
				#print("Option Values: " + str(option_values))

			# get the value of the size option, if there is one
			opt_idx = 0
			if len(option_names) > 0:
				for current_opt_name in option_names:
					if current_opt_name == opt_name:
						#print("Valid Opt: " + opt_name)
						valid_opt = True
						break
					opt_idx += 1
			else:
				print("WARNING: No option names given!")


			#print("Opt Idx: " + str(opt_idx))
			if valid_opt:
				opt_value = ''
				if len(option_values) > opt_idx:
					opt_value = option_values[opt_idx]
				#print("Option Value: " + opt_value)

				opt_fmla = colors_fmla
				if opt_value in color_options.keys():
					color_options[opt_value] = opt_fmla
				else:
					print("WARNING: Option Value not in Color Options Keys!")

		#print("Populated Option Values: " + opt_name + ": " + str(color_options))

		# now we have populated all color values for this product
		# so create color fmla by looping through colors and printing those with valid values
		if valid_opt:
			#print("Colors: ")
			opt_idx = 0
			for color_name, color_value in color_options.items():
				if color_value != '':
					variant_color_fmla = color_value
					#print(variant_color_fmla)
					if opt_idx == 0:
						final_colors_fmla += "," + variant_color_fmla
					else:
						final_colors_fmla += ",\", or \"," + variant_color_fmla
					opt_idx += 1
			#print()
			final_colors_fmla += ",\". \""
		else:
			final_colors_fmla += "," + colors_fmla + ",\". \""

	#print("Colors Formula: " + final_colors_fmla + "\n")

	return final_colors_fmla

def generate_colors_html(product, init_product):

	final_colors_html = "" # init fmla for this part of the description
	if determine_given_colors(product): # if we are NOT given colors we do not include colors in the description
		final_colors_html = "<table><tr><td>Colors: " # only if at least 1 of the variants has colors

		opt_name = 'Color' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		color_options = options[opt_name]
		#print("Color Options: " + str(color_options))

		valid_opt = False

		colors_html = ''

		for vrnt_idx in range(len(product)):
			variant = product[vrnt_idx]
			init_variant = init_product[vrnt_idx]

			valid_opt = False

			colors = ''

			if len(variant) > 4:
				handle = variant[1].strip().lower()
				#print("Handle: " + handle)
				colors = variant[4].strip().lower()
				#print("Colors: " + colors)

			colors_html = '' # init option fmla so if no value given it is empty quotes
			if colors != '' and colors != 'n/a':
				#colors = re.sub('\"','\",CHAR(34),\"', colors) # if something like "red" brown is given as colors, then fmla will incorrectly interpret that as closing string
				colors_html = "</td><td>" + colors.title()
			#print("Colors Formula: " + colors_fmla)

			option_data = generate_options(variant, init_variant)

			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				#print("Option Names: " + str(option_names))
				option_values = option_data[1]
				#print("Option Values: " + str(option_values))

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				if current_opt_name == opt_name:
					#print("Valid Opt: " + opt_name)
					valid_opt = True
					break
				opt_idx += 1


			#print("Opt Idx: " + str(opt_idx))
			if valid_opt:
				opt_value = option_values[opt_idx]
				#print("Option Value: " + opt_value)

				opt_html = colors_html

				color_options[opt_value] = opt_html

		#print("Populated Option Values: " + opt_name + ": " + str(color_options))

		# now we have populated all color values for this product
		# so create color fmla by looping through colors and printing those with valid values
		if valid_opt:
			#print("Colors: ")
			opt_idx = 0
			for color_name, color_value in color_options.items():
				if color_value != '':
					variant_color_html = color_value
					#print(variant_color_html)
					if opt_idx == 0:
						final_colors_html += variant_color_html
					else:
						final_colors_html += ", or " + variant_color_html
					opt_idx += 1
			#print()
			final_colors_html += ". </td></tr>"
		else:
			final_colors_html += colors_html + ". </td></tr>"

	#print("Colors HTML: " + final_colors_html + "\n")

	return final_colors_html

def determine_given_materials(product_details):
	given_materials = True

	for variant_details in product_details:
		materials = ''

		if len(variant_details) > 5:
			materials = variant_details[5].strip()

			if materials == '' or materials.lower() == 'n/a':
				# no colors given
				given_materials = False

		else:
			given_materials = False

	return given_materials

def generate_materials_fmla(product):

	final_materials_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_materials(product): # if we are NOT given materials we do not include materials in the description
		final_materials_fmla = "\"Materials: \"" # only if at least 1 of the variants has materials

		# for now, only handle cases where all variants have same material
		variant1 = product[0]

		materials = ''

		if len(variant1) > 5:
			handle = variant1[1].strip().lower()
			materials = variant1[5].strip().lower()

		materials_fmla = '\"\"' # init option fmla so if no value given it is empty quotes
		if materials != '' and materials != 'n/a':
			# format materials string by correcting typos and replacing invalid characters
			materials = re.sub('\"','\'', materials) # if something like "s" spring is given as material, then fmla will incorrectly interpret that as closing string

			materials_fmla = "\"" + materials + "\""

		final_materials_fmla += "," + materials_fmla + ",\". \""

	return final_materials_fmla

def generate_materials_html(product):

	final_materials_html = "<tr>" # init fmla for this part of the description
	if determine_given_materials(product): # if we are NOT given materials we do not include materials in the description
		#print("\n===GIVEN MATERIALS===\n")
		final_materials_html = "<tr><td>Materials: </td>" # only if at least 1 of the variants has materials
		#print("final_materials_html: " + final_materials_html)
		# for now, only handle cases where all variants have same material
		variant1 = product[0]

		materials = ''

		if len(variant1) > 5:
			handle = variant1[1].strip().lower()
			materials = variant1[5].strip().lower()

		materials_html = '' # init option fmla so if no value given it is empty quotes
		if materials != '' and materials != 'n/a':
			# format materials string by correcting typos and replacing invalid characters
			#materials = re.sub('\"','\'', materials) # if something like "s" spring is given as material, then fmla will incorrectly interpret that as closing string

			materials_html = "<td>" + materials.title() + ". </td></tr>"

		final_materials_html += materials_html

	return final_materials_html

def determine_given_finishes(product_details):
	given_finishes = True

	for variant_details in product_details:
		finishes = ''

		if len(variant_details) > 6:
			finishes = variant_details[6].strip()

			if finishes == '' or finishes.lower() == 'n/a':
				# no finishes given
				given_finishes = False

		else:
			given_finishes = False

	return given_finishes

def generate_finishes_fmla(product):

	final_finishes_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_finishes(product): # if we are NOT given finishes we do not include finishes in the description
		final_finishes_fmla = "\"Finishes: \"" # only if at least 1 of the variants has finishes

		# for now, only handle cases where all variants have same material
		variant1 = product[0]

		finishes = ''

		if len(variant1) > 6:
			handle = variant1[1].strip().lower()
			finishes = variant1[6].strip().lower()

		finishes_fmla = '\"\"' # init option fmla so if no value given it is empty quotes
		if finishes != '' and finishes != 'n/a':
			finishes_fmla = "\"" + finishes + "\""

		final_finishes_fmla += "," + finishes_fmla + ",\". \""

	return final_finishes_fmla

def generate_finishes_html(product):

	final_finishes_html = "" # init fmla for this part of the description
	if determine_given_finishes(product): # if we are NOT given finishes we do not include finishes in the description
		final_finishes_html = "<tr><td>Finishes: </td>" # only if at least 1 of the variants has finishes

		# for now, only handle cases where all variants have same material
		variant1 = product[0]

		finishes = ''

		if len(variant1) > 6:
			handle = variant1[1].strip().lower()
			finishes = variant1[6].strip().lower()

		finishes_html = '' # init option fmla so if no value given it is empty quotes
		if finishes != '' and finishes != 'n/a':
			finishes_html = "<td>" + finishes.title() + ". </td></tr>"

		final_finishes_html += finishes_html + "</table>"
	else:
		# close the description data table
		final_finishes_html = "</table>"

	return final_finishes_html

def determine_given_dimensions(product_details):
	given_dims = True

	for variant_details in product_details:
		width = depth = height = ''

		if len(variant_details) > 7:
			width = variant_details[7].strip()

			if len(variant_details) > 8:
				depth = variant_details[8].strip()

				if len(variant_details) > 9:
					height = variant_details[9].strip()
		else:
			given_dims = False

		if width == '' or width.lower() == 'n/a':
			# no width given but maybe other dims given
			if depth == '' or depth.lower() == 'n/a':
				# no width or depth given but maybe height given
				if height == '' or height.lower() == 'n/a':
					given_dims = False

	return given_dims

# product input includes all variants of product
# def set_option_values(product, opt_name):
#
# 	standard_type = opt_name.lower() + "s"
#
# 	options = reader.read_standards(standard_type)
#
# 	valid_opt = False
#
# 	for variant in product:
#
# 		dim_fmla = ''
#
# 		if opt_name == 'Size':
# 			width = depth = height = ''
#
# 			if len(variant) > 5:
# 				handle = variant[1].strip()
# 				#print("Handle: " + handle)
# 				width = variant[5].strip()
#
# 				if len(item_details) > 6:
# 					depth = variant[6].strip()
#
# 					if len(item_details) > 7:
# 						height = variant[7].strip()
#
# 			width_fmla = depth_fmla = height_fmla = '\"\"'
# 			if width != '' and width != 'n/a':
# 				width_fmla = "\"" + width + "\",CHAR(34),\" W \""
# 			if depth != '' and depth != 'n/a':
# 				depth_fmla = "\"" + depth + "\",CHAR(34),\" D \""
# 			if height != '' and height != 'n/a':
# 				height_fmla = "\"" + height + "\",CHAR(34),\" H\""
#
# 			dim_fmla = width_fmla + ",\"x \"," + depth_fmla + ",\"x \"," + height_fmla + ",\". \""
#
# 		option_data = generate_options(variant)
# 		option_names = []
# 		option_values = []
# 		if len(option_data) > 0:
# 			option_names = option_data[0]
# 			option_values = option_data[1]
#
# 		# get the value of the size option, if there is one
# 		opt_idx = 0
# 		for current_opt_name in option_names:
# 			if current_opt_name == opt_name:
# 				valid_opt = True
# 				break
# 			opt_idx += 1
#
# 		if valid_opt:
# 			opt_value = option_values[opt_idx]
#
# 			opt_fmla = ''
# 			if opt_name == 'Size':
# 				opt_fmla = dim_fmla
# 			elif opt_name == 'Color':
# 				opt_fmla = color_fmla
#
# 			options[opt_value] = opt_fmla
#
# 	print(opt_name + ": " + str(options))
#
# 	return options

def determine_valid_option(option_values):
	valid_opt = False
	for dims in option_values.values():
		if dims != '':
			valid_opt = True

	return valid_opt

def get_variant_indices_by_size(product_details):
	#print("\n=== Get Variant Indices by Size ===\n")

	areas = []
	widths = []

	for variant in product_details:
		width = depth = height = ''

		if len(variant) > 7:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			width = variant[7].strip()

			if len(variant) > 8:
				depth = variant[8].strip()

				if len(variant) > 9:
					height = variant[9].strip()

		blank_width = blank_depth = blank_height = True
		if width != '' and width != 'n/a':
			blank_width = False
		if depth != '' and depth != 'n/a':
			blank_depth = False
		if height != '' and height != 'n/a':
			blank_height = False

		if not blank_width and not blank_depth:
			area = int(width) * int(depth)
			areas.append(area)
			widths.append(int(width))

		elif blank_width:
			widths.append(0) # we need 0 returned for width if empty

		elif blank_depth:
			# if width contains multiple ft symbols and depth is blank, take digits before first foot symbol as width and digits after as depth
			if re.search('\'\\s*\\d+\'',width):
				print("Format Notice: Measurement contains improper sequence of two separate feet measurements!")
				dims = width.split('\'')
				width = dims[0].rstrip('\'')
				depth = dims[2].rstrip('\'')
				widths.append(int(width))
		else:
			widths.append(0) # we need 0 returned for width if empty

	#print("Areas: " + str(areas))

	#areas_array = np.array(areas)
	#print("Widths: " + str(widths))
	num_widths = len(widths)
	#print("Num Widths: " + str(num_widths))

	widths_array = np.array(widths)

	sorted_indices = np.argsort(widths_array)
	sorted_indices = np.flip(sorted_indices)
	#print("Sorted Indices: " + str(sorted_indices))

	#print("\n=== Got Variant Indices by Size ===\n")

	return sorted_indices

def get_sorted_indices(product):

	#print("\n=== Get Variant Indices by Size ===\n")

	areas = []
	widths = []

	for variant in product:
		width = depth = height = ''

		handle = ''

		if len(variant) > 7:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			width = variant[7].strip()

			if len(variant) > 8:
				depth = variant[8].strip()

				if len(variant) > 9:
					height = variant[9].strip()

		blank_width = blank_depth = blank_height = True
		if width != '' and width != 'n/a':
			blank_width = False
		if depth != '' and depth != 'n/a':
			blank_depth = False
		if height != '' and height != 'n/a':
			blank_height = False

		meas_type = ''
		if not blank_width:
			meas_type = reader.determine_measurement_type(width, handle)

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
	handle = variant1[handle_idx]
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

def generate_dimensions_fmla(product, init_product):

	dimensions_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_dimensions(product): # if we are NOT given dimensions we do not include dimensions in the description
		dimensions_fmla = "\"Dimensions (in): \"" # only if at least 1 of the variants has dimensions

		#sizes = set_option_values(product, 'Size')
		opt_name = 'Size' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		size_options = options[opt_name]
		#print("Size Options: " + str(size_options))

		valid_opt = False

		# sort variants
		#print("Sort Init Variants")
		init_sorted_variants = sort_variants_by_size(init_product)
		#print("Sort Variants")
		sorted_variants = sort_variants_by_size(product)

		type = ''

		dim_fmla = ''

		for vrnt_idx in range(len(sorted_variants)):
			variant = sorted_variants[vrnt_idx]
			init_variant = init_sorted_variants[vrnt_idx]

			valid_opt = False

			type = generate_product_type(variant)

			width = depth = height = ''

			if len(variant) > 7:
				handle = variant[1].strip().lower()
				#print("Handle: " + handle)
				width = variant[7].strip()

				if len(variant) > 8:
					depth = variant[8].strip()

					if len(variant) > 9:
						height = variant[9].strip()

			blank_width = blank_depth = blank_height = True
			if width != '' and width != 'n/a':
				blank_width = False
			if depth != '' and depth != 'n/a':
				blank_depth = False
			if height != '' and height != 'n/a':
				blank_height = False

			dim_fmla = ''
			width_fmla = depth_fmla = height_fmla = '\"\"' # init option fmla so if no value given it is empty quotes
			if not blank_width:
				width_fmla = "\"" + width + "\",CHAR(34),\" W\""
				dim_fmla = width_fmla
			if not blank_depth:
				depth_fmla = "\"" + depth + "\",CHAR(34),\" D\""
				if blank_width:
					dim_fmla = depth_fmla
				else:
					dim_fmla += ",\" x \"," + depth_fmla
			if not blank_height:
				height_fmla = "\"" + height + "\",CHAR(34),\" H\""
				if blank_width and blank_height:
					dim_fmla = height_fmla
				else:
					dim_fmla += ",\" x \"," + height_fmla

			dim_fmla += ",\". \""

			option_data = generate_options(variant, init_variant)
			#print("Option Data: " + str(option_data))
			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				option_values = option_data[1]

			# order option values from large to small, and correspond with dim_fmla

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				if current_opt_name == opt_name:
					valid_opt = True
					break
				opt_idx += 1

			if valid_opt:
				opt_value = option_values[opt_idx] # option value is dictionary key

				opt_fmla = dim_fmla

				# before assigning to options dict, could sort dims but could also sort after by checking if custom dims and storing in separate array to sort
				size_options[opt_value] = opt_fmla

		#print(opt_name + ": " + str(size_options))

		# now we have populated all size values for this product
		# so create dim fmla by looping through sizes and printing those with valid values
		if valid_opt:
			#print("Dimensions: ")

			# reorder custom dims from large to small

			for size, dims in size_options.items():
				if dims != '':
					#print("Dims: " + dims)
					if type == 'rugs':
						variant_dim_fmla = dims # do not add quote-comma to dims b/c already there
						#print("variant_dim_fmla: " + variant_dim_fmla)
						dimensions_fmla += ",CHAR(10)," + variant_dim_fmla
					else:
						size_fmla = "\"" + size + ": \","
						#print("size_fmla: " + size_fmla)
						variant_dim_fmla = size_fmla + dims
						#print(variant_dim_fmla)
						dimensions_fmla += ",CHAR(10)," + variant_dim_fmla

			#print()
		else:
			dimensions_fmla += "," + dim_fmla

	#print("Dimensions Formula: " + dimensions_fmla + "\n")

	return dimensions_fmla

def generate_dimensions_html(product, init_product):

	dimensions_html = "" # init fmla for this part of the description
	if determine_given_dimensions(product): # if we are NOT given dimensions we do not include dimensions in the description
		dimensions_html = "<table><tr><td>Dimensions (in.): </td><td>" # only if at least 1 of the variants has dimensions

		#sizes = set_option_values(product, 'Size')
		opt_name = 'Size' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		size_options = options[opt_name]
		#print("Size Options: " + str(size_options))

		valid_opt = False

		# sort variants
		#print("Sort Init Variants")
		init_sorted_variants = sort_variants_by_size(init_product)
		#print("Sort Variants")
		sorted_variants = sort_variants_by_size(product)

		type = ''

		dim_html = ''

		for vrnt_idx in range(len(sorted_variants)):
			variant = sorted_variants[vrnt_idx]
			init_variant = init_sorted_variants[vrnt_idx]

			valid_opt = False

			type = generate_product_type(variant)

			width = depth = height = ''

			if len(variant) > 7:
				handle = variant[1].strip().lower()
				#print("Handle: " + handle)
				width = variant[7].strip()

				if len(variant) > 8:
					depth = variant[8].strip()

					if len(variant) > 9:
						height = variant[9].strip()

			blank_width = blank_depth = blank_height = True
			if width != '' and width != 'n/a':
				blank_width = False
			if depth != '' and depth != 'n/a':
				blank_depth = False
			if height != '' and height != 'n/a':
				blank_height = False

			dim_html = ''
			width_html = depth_html = height_html = '' # init option fmla so if no value given it is empty quotes
			if not blank_width:
				width_html = width + "\" W"
				dim_html = width_html
			if not blank_depth:
				depth_html = depth + "\" D"
				if blank_width:
					dim_html = depth_html
				else:
					dim_html += " x " + depth_html
			if not blank_height:
				height_html = height + "\" H"
				if blank_width and blank_height:
					dim_html = height_html
				else:
					dim_html += " x " + height_html

			dim_html += ". </td></tr>"

			option_data = generate_options(variant, init_variant)
			#print("Option Data: " + str(option_data))
			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				option_values = option_data[1]

			# order option values from large to small, and correspond with dim_fmla

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				if current_opt_name == opt_name:
					valid_opt = True
					break
				opt_idx += 1

			if valid_opt:
				opt_value = option_values[opt_idx] # option value is dictionary key

				opt_fmla = dim_html

				# before assigning to options dict, could sort dims but could also sort after by checking if custom dims and storing in separate array to sort
				size_options[opt_value] = opt_fmla

		#print(opt_name + ": " + str(size_options))

		# now we have populated all size values for this product
		# so create dim fmla by looping through sizes and printing those with valid values
		if valid_opt:
			#print("Dimensions: ")

			# reorder custom dims from large to small

			for size, dims in size_options.items():
				if dims != '':
					#print("Dims: " + dims)
					if type == 'rugs':
						variant_dim_html = dims # do not add quote-comma to dims b/c already there
						#print("variant_dim_fmla: " + variant_dim_fmla)
						dimensions_html += variant_dim_html
					else:
						size_html = size + ": "
						#print("size_html: " + size_html)
						variant_dim_html = size_html + dims
						#print(variant_dim_fmla)
						dimensions_html += variant_dim_html

			#print()
		else:
			dimensions_html += dim_html + "</table>"

	#print("Dimensions HTML: " + dimensions_html + "\n")

	return dimensions_html

def generate_features(item_details):
	print("\n===Generate Features===\n")
	
	# bullet point indicates new line in features fmla so use bullet point for new line
	features = '• Perfectly balanced and sturdy • Lightweight and easy to carry for convenience. • Durable construction, built to last. '

	#print("Features: " + features)
	return features


def generate_features_fmla(product):
	features_fmla = "\"\""

	for variant in product:

		features = ''

		if len(variant) > 11:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			features = variant[11].strip()
			print("Features: " + features)
			# if no intro given then generate one
			if features == '' or str.lower(features) == 'features':
				features = generate_features(variant)

		if features != '' and features != 'n/a':
			# need better way to check if there are no proper nouns that should stay capitalized, b/c too blunt to lowercase everything
			features = features.lower()

			# add periods before bullets
			# make sure no extra periods added so no double periods if sentence already has period at end
			features = re.sub(r"([^\.])\s•",r"\1. •", features) 
			if features[-1] != '.':
				#print("Last character: " + features[-1])
				features += '. '

			features = capitalize_sentences(features).strip()

			features = re.sub('\"','\",CHAR(34),\"', features) # if quotes found in features, such as for dimensions, then fmla will incorrectly interpret that as closing string
			
			

			features = re.sub('•','\",CHAR(10),\"• \",\"', features) # bullet point indicates new line
			features = re.sub('    ','\",CHAR(10),\"• \",\"', features) # 4 spaces indicates new line
			features = re.sub('ï|Ï','\",CHAR(10),\"• \",\"', features) # ï character indicates new line (for Coaster)
			features_fmla = "\"" + features + "\""

			

		#print("Features Formula: " + features_fmla)

	return features_fmla

def generate_features_html(product):
	features_html = "\"\""

	for variant in product:

		features = ''

		if len(variant) > 11:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			features = variant[11].strip()
			print("Features: " + features)
			# if no intro given then generate one
			if features == '' or str.lower(features) == 'features':
				features = generate_features(variant)

		if features != '' and features != 'n/a':
			# need better way to check if there are no proper nouns that should stay capitalized, b/c too blunt to lowercase everything
			features = features.lower()

			# add periods before bullets
			# make sure no extra periods added so no double periods if sentence already has period at end
			features = re.sub(r"([^\.])\s•",r"\1. •", features) 
			if features[-1] != '.':
				#print("Last character: " + features[-1])
				features += '. '

			features = capitalize_sentences(features).strip()

			#features = re.sub('\"','\",CHAR(34),\"', features) # if quotes found in features, such as for dimensions, then fmla will incorrectly interpret that as closing string
			
			if re.search('•',features) or re.search('    ',features) or re.search('ï|Ï',features):
				features_list = "<ul>"
				print("\nFEATURES: " + features)

				features_list += re.sub(r'•([^\.]+)\.',r'<li>\1. </li>', features) # bullet point indicates new line
				features_list = re.sub(r'    ([^\.]+)\.',r'<li>\1. </li>', features_list) # 4 spaces indicates new line
				features_list = re.sub(r'ï|Ï([^\.]+)\.',r'<li>\1. </li>', features_list) # ï character indicates new line (for Coaster)
				
				features_list += "</ul>"

				features_html = features_list
			else:
				features_html = features

			break # for now, once we make features list for variant skip the rest of the variants for now bc it is more complex to organize all variant features in descrip

		#print("Features HTML: " + features_html)

	return features_html

# given list of separate data sources/tables
# with unknown data fields
# use known desired data fields and keywords to isolate fields in data tables
def generate_catalog_from_tables(list_of_tables):
	# desired fields to look for in sheets
	sku_key = sku_field_name = "sku" # init default
	desired_fields = [sku_field_name]
	sku_keywords = ["sku", "item#"] # maintain list when new vendors use different keywords
	keywords = {"sku":sku_keywords}
	for table in list_of_tables:
		for header in table:
			print("header: " + header)
			for field in desired_fields:
				for keyword in keywords[field]:
					if re.search(keyword, header):
						# found header matching keyword
						sku_key = header

# convert from all_items_json = [[{'sku':'sku1','collection':'col1'}]]
# to [{'sku':['sku1'],'collection':['col1']}]
def convert_list_of_items_to_fields(all_items_json):

	list_of_fields = []
	all_fields_dict = {}
	
	for sheet in all_items_json:
		print("sheet: " + str(sheet))
		# all_skus = []
		# all_collections = []
		# all_values = []
		for item_json in sheet:
			print("item_json: " + str(item_json))
			# all_skus.append(item_json['sku'])
			# all_collections.append(item_json['collection'])
			for key in item_json:
				standard_key = determiner.determine_standard_key(key)
				formatted_input = reader.format_vendor_product_data(item_json[key], standard_key) # passing in a single value corresponding to key. also need key to determine format.
				if standard_key != '' and formatted_input != '':
					if key in all_fields_dict.keys():
						print("add to existing key")
						all_fields_dict[standard_key].append(formatted_input)
					else:
						print("add new key")
						all_fields_dict[standard_key] = [formatted_input]
		# all_fields_dict['sku'] = all_skus
		# all_fields_dict['collection'] = all_collections
		print("all_fields_dict: " + str(all_fields_dict))
			
		list_of_fields.append(all_fields_dict)

	print("all_fields_dict: " + str(all_fields_dict))
	return list_of_fields


def generate_catalog_from_json(all_items_json):
	print("\n===Auto Generate Catalog Given JSON===\n")
	print("all_items_json: " + str(all_items_json))

	catalog = []

	ext = 'tsv'

	# header names given by vendor, rather than determining index

	#catalog_dict = {} # store lists based on desired field name key
	desired_field_names = ['sku', 'collection', 'type', 'intro', 'color', 'material', 'finish', 'width', 'depth', 'height', 'weight', 'features', 'cost', 'images', 'barcode'] #corresponding to keys in dict. determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	crucial_field_names = ['sku', 'cost', 'images'] # , cost, images]
	current_sheet_field_name = '' # loop thru each sheet and each field in each sheet

	# for unknown no. sheets with unknown contents
	# for user input, we have their list of files to loop thru

	all_sheet_all_field_values = convert_list_of_items_to_fields(all_items_json)
	# format keys and values before sending to display
	# all_sheet_all_field_values = determiner.determine_standard_keys(all_sheet_all_field_values)
	# all_sheet_all_field_values = format

	print("\n === Display Catalog Info === \n")

	catalog = []

	# take first sheet and loop thru following sheets to see if matching sku entry
	sheet1 = all_sheet_all_field_values[0]
	print("sheet1: " + str(sheet1))
	# all keys
	# sku_key = 'sku'
	# # all fields/values
	# all_sheet1_skus = []
	# if sku_key in sheet1.keys():
	# 	all_sheet1_skus = sheet1[sku_key]
	# print("all_sheet1_skus init: " + str(all_sheet1_skus))
	# all_sheet1_collections = []
	#all_sheet1_prices = sheet1['prices']
	all_sheet1_values = {}
	for key in desired_field_names:
		if key in sheet1.keys():
		#if sheet1[key] != '':
			all_sheet1_values[key] = sheet1[key]
	print("all_sheet1_values init: " + str(all_sheet1_values))

	# see if all fields given by seeing if left blank or key exists?
	all_fields_given = True
	print("sheet1.keys(): " + str(sheet1.keys()))
	for key in desired_field_names:
		
		if key not in sheet1.keys():
		#if sheet1[key] == '':
			all_fields_given = False
			break
	print("all_fields_given in first sheet? " + str(all_fields_given)) # since we assume all sheets rely on each other for full info this does not happen until we upgrade to allowing sheets with full and partial info

	all_sheet1_skus = all_sheet1_values['sku']
	for product_idx in range(len(all_sheet1_skus)):
		sheet1_all_field_values = {}
		for key in all_sheet1_values:
			print("key in all_sheet1_values: " + str(key))
			sheet1_value = all_sheet1_values[key][product_idx]
			print("sheet1_value: " + str(sheet1_value))
			sheet1_all_field_values[key] = sheet1_value
		sheet1_sku = all_sheet1_skus[product_idx]
		# sheet1_collection = ''
		# if len(all_sheet1_collections) > 0:
		# 	sheet1_collection = all_sheet1_collections[product_idx]
		# #sheet1_cost = all_sheet1_prices[product_idx]
		# sheet_all_field_values = [sheet1_sku] # corresponding to desired field names
		print("sheet1_all_field_values: " + str(sheet1_all_field_values))

		# init blank and then we will check if spots blank to see if we should transfer data
		product_catalog_dict = {
			'sku':'n/a',
			'collection':'n/a',
			'type':'n/a',
			'intro':'n/a',
			'color':'n/a',
			'material':'n/a',
			'finish':'n/a',
			'width':'n/a',
			'depth':'n/a',
			'height':'n/a',
			'weight':'n/a',
			'features':'n/a',
			'cost':'n/a',
			'images':'n/a',
			'barcode':'n/a'
		}

		for key in desired_field_names:
			if key in sheet1.keys():
			#if sheet1[key] != '':
				current_sheet_value = sheet1[key][product_idx]
				print("current_sheet_" + key + ": " + str(current_sheet_value))
				if current_sheet_value != '' and current_sheet_value != 'n/a':
					product_catalog_dict[key] = current_sheet_value
		print("product_catalog_dict after sheet1: " + str(product_catalog_dict))

		if all_fields_given:
			for field_idx in range(len(desired_field_names)):
				desired_field_name = desired_field_names[field_idx]
				sheet_field_value = sheet1_all_field_values[desired_field_name]
				if sheet_field_value != '' and sheet_field_value != 'n/a':
					product_catalog_dict[desired_field_name] = sheet_field_value
			


		# compare all subsequent sheets to first sheet
		elif len(all_sheet_all_field_values) > 1 and not all_fields_given: # if we have more than 1 sheet and we need more fields. 
			for current_sheet_idx in range(1,len(all_sheet_all_field_values)):
				
				current_sheet = all_sheet_all_field_values[current_sheet_idx] # current sheet
				print("current_sheet: " + str(current_sheet))
				# current_sheet_dict = {}
				# for key in desired_field_names:
				# 	if key in current_sheet_all_field_values.keys():
				# 		all_current_sheet_current_field_values = current_sheet_all_field_values[key]
				# 		current_sheet_dict[key] = all_current_sheet_current_field_values
				
				#for key in desired_field_names:
					#if key in current_sheet_all_field_values.keys():
				all_current_sheet_skus = current_sheet['sku']
				
				#all_current_sheet_collections = current_sheet_all_field_values['collections']
				#all_current_sheet_prices = current_sheet_all_field_values['price']
		

				#match_in_sheet = False
				for current_sheet_item_idx in range(len(all_current_sheet_skus)):
					
					sheet1_sku = sheet1_all_field_values['sku']
					current_sheet_sku = all_current_sheet_skus[current_sheet_item_idx]
					#current_sheet_collection = all_current_sheet_collections[current_sheet_item_idx]
					
					if sheet1_sku == current_sheet_sku:
						print("sheet1_sku matches current_sheet_sku: " + sheet1_sku + ", " + current_sheet_sku)
						#match_in_sheet = True

						for key in desired_field_names:
							if key in current_sheet.keys():
							#if current_sheet[key] != '':
								current_sheet_value = current_sheet[key][current_sheet_item_idx]
								print("current_sheet_" + key + ": " + str(current_sheet_value))
								if current_sheet_value != '' and current_sheet_value != 'n/a':
									product_catalog_dict[key] = current_sheet_value
						# product_catalog_dict['sku'] = sheet1_sku
						# product_catalog_dict['collection'] = current_sheet_collection
						# product_catalog_dict['type'] = current_sheet_type

						#all_current_sheet_images = []
						# key = 'images'
						# if key in current_sheet_all_field_values.keys():
						# 	all_current_sheet_images = current_sheet_all_field_values[key]
						# 	current_sheet_values = all_current_sheet_images[current_sheet_item_idx]
						# 	if current_sheet_values != '' and current_sheet_values != 'n/a':
						# 		product_catalog_dict[key] = current_sheet_values

						break

		print("product_catalog_dict: " + str(product_catalog_dict))


		# see if crucial fields given by seeing if left blank or key exists?
		crucial_fields_given = True
		for crucial_field in crucial_field_names:
			#print("product_catalog_dict.keys(): " + str(product_catalog_dict.keys()))
			#if crucial_field not in product_catalog_dict.keys():
			if product_catalog_dict[crucial_field] == '':
				crucial_fields_given = False
				break

		if crucial_fields_given: 
			catalog_info = list(product_catalog_dict.values()) #[sheet1_sku] #, coll_name, product_type, intro, color, material, finish, length, width, height, weight, features, sheet1_cost, img_links, barcode]
			print("catalog_info: " + str(catalog_info))
			catalog.append(catalog_info)
		else:
			print("Warning: Missing fields for SKU " + sheet1_sku + ", so product not uploaded!")


	return catalog

def generate_catalog_auto(vendor):
	print("\n===Auto Generate Catalog Given Vendor " + vendor.title() + " ===\n")

	catalog = []

	ext = 'tsv'

	# header names given by vendor, rather than determining index

	#catalog_dict = {} # store lists based on desired field name key
	desired_field_names = ['sku', 'collection', 'type', 'intro', 'color', 'material', 'finish', 'width', 'depth', 'height', 'weight', 'features', 'cost', 'images', 'barcode'] #corresponding to keys in dict. determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	crucial_field_names = ['sku', 'cost', 'images'] # , cost, images]
	current_sheet_field_name = '' # loop thru each sheet and each field in each sheet

	if vendor == 'acme':
		# for unknown no. sheets with unknown contents
		# for user input, we have their list of files to loop thru

		data_files = ['price sheet test', 'spec sheet test', 'image sheet test'] # for acme, price sheet, spec sheet, and img sheet separate
		all_sheet_all_field_values = reader.read_raw_vendor_product_data(vendor, data_files)
		
		print("\n === Display Catalog Info === \n")

		catalog = []

		# take first sheet and loop thru following sheets to see if matching sku entry
		sheet1 = all_sheet_all_field_values[0]
		#print("sheet1: " + str(sheet1))
		# all keys
		# sku_key = 'sku'
		# # all fields/values
		# all_sheet1_skus = []
		# if sku_key in sheet1.keys():
		# 	all_sheet1_skus = sheet1[sku_key]
		# print("all_sheet1_skus init: " + str(all_sheet1_skus))
		# all_sheet1_collections = []
		#all_sheet1_prices = sheet1['prices']
		all_sheet1_values = {}
		for key in desired_field_names:
			if key in sheet1.keys():
			#if sheet1[key] != '':
				all_sheet1_values[key] = sheet1[key]
		#print("all_sheet1_values init: " + str(all_sheet1_values))

		# see if all fields given by seeing if left blank or key exists?
		all_fields_given = True
		#print("sheet1.keys(): " + str(sheet1.keys()))
		for key in desired_field_names:
			
			if key not in sheet1.keys():
			#if sheet1[key] == '':
				all_fields_given = False
				break
		#print("all_fields_given in first sheet? " + str(all_fields_given)) # since we assume all sheets rely on each other for full info this does not happen until we upgrade to allowing sheets with full and partial info

		all_sheet1_skus = all_sheet1_values['sku']
		for product_idx in range(len(all_sheet1_skus)):
			sheet1_all_field_values = {}
			for key in all_sheet1_values:
				#print("key in all_sheet1_values: " + str(key))
				sheet1_value = all_sheet1_values[key][product_idx]
				#print("sheet1_value: " + str(sheet1_value))
				sheet1_all_field_values[key] = sheet1_value
			# sheet1_sku = all_sheet1_skus[product_idx]
			# sheet1_collection = ''
			# if len(all_sheet1_collections) > 0:
			# 	sheet1_collection = all_sheet1_collections[product_idx]
			# #sheet1_cost = all_sheet1_prices[product_idx]
			# sheet_all_field_values = [sheet1_sku] # corresponding to desired field names
			#print("sheet1_all_field_values: " + str(sheet1_all_field_values))

			# init blank and then we will check if spots blank to see if we should transfer data
			product_catalog_dict = {
				'sku':'',
				'collection':'',
				'type':'',
				'intro':'',
				'color':'',
				'material':'',
				'finish':'',
				'width':'',
				'depth':'',
				'height':'',
				'weight':'',
				'features':'',
				'cost':'',
				'images':'',
				'barcode':''
			}

			for key in desired_field_names:
				if key in sheet1.keys():
				#if sheet1[key] != '':
					current_sheet_value = sheet1[key][product_idx]
					#print("current_sheet_" + key + ": " + str(current_sheet_value))
					if current_sheet_value != '' and current_sheet_value != 'n/a':
						product_catalog_dict[key] = current_sheet_value
			#print("product_catalog_dict after sheet1: " + str(product_catalog_dict))

			sheet1_sku = ''

			if all_fields_given:
				for field_idx in range(len(desired_field_names)):
					desired_field_name = desired_field_names[field_idx]
					sheet_field_value = sheet1_all_field_values[desired_field_name]
					if sheet_field_value != '' and sheet_field_value != 'n/a':
						product_catalog_dict[desired_field_name] = sheet_field_value
				
	

			# compare all subsequent sheets to first sheet
			elif len(all_sheet_all_field_values) > 1 and not all_fields_given: # if we have more than 1 sheet and we need more fields. 
				for current_sheet_idx in range(1,len(all_sheet_all_field_values)):
					
					current_sheet = all_sheet_all_field_values[current_sheet_idx] # current sheet
					#print("current_sheet: " + str(current_sheet))
					# current_sheet_dict = {}
					# for key in desired_field_names:
					# 	if key in current_sheet_all_field_values.keys():
					# 		all_current_sheet_current_field_values = current_sheet_all_field_values[key]
					# 		current_sheet_dict[key] = all_current_sheet_current_field_values
					
					#for key in desired_field_names:
						#if key in current_sheet_all_field_values.keys():
					all_current_sheet_skus = current_sheet['sku']
					
					#all_current_sheet_collections = current_sheet_all_field_values['collections']
					#all_current_sheet_prices = current_sheet_all_field_values['price']
			

					#match_in_sheet = False
					for current_sheet_item_idx in range(len(all_current_sheet_skus)):
						
						sheet1_sku = sheet1_all_field_values['sku']
						current_sheet_sku = all_current_sheet_skus[current_sheet_item_idx]
						#current_sheet_collection = all_current_sheet_collections[current_sheet_item_idx]
						
						if sheet1_sku == current_sheet_sku:
							#print("sheet1_sku matches current_sheet_sku: " + sheet1_sku + ", " + current_sheet_sku)
							#match_in_sheet = True

							for key in desired_field_names:
								if key in current_sheet.keys():
								#if current_sheet[key] != '':
									current_sheet_value = current_sheet[key][current_sheet_item_idx]
									#print("current_sheet_" + key + ": " + str(current_sheet_value))
									if current_sheet_value != '' and current_sheet_value != 'n/a':
										product_catalog_dict[key] = current_sheet_value
							# product_catalog_dict['sku'] = sheet1_sku
							# product_catalog_dict['collection'] = current_sheet_collection
							# product_catalog_dict['type'] = current_sheet_type

							#all_current_sheet_images = []
							# key = 'images'
							# if key in current_sheet_all_field_values.keys():
							# 	all_current_sheet_images = current_sheet_all_field_values[key]
							# 	current_sheet_values = all_current_sheet_images[current_sheet_item_idx]
							# 	if current_sheet_values != '' and current_sheet_values != 'n/a':
							# 		product_catalog_dict[key] = current_sheet_values

							break

			#print("product_catalog_dict: " + str(product_catalog_dict))


			# see if crucial fields given by seeing if left blank or key exists?
			crucial_fields_given = True
			for crucial_field in crucial_field_names:
				#print("product_catalog_dict.keys(): " + str(product_catalog_dict.keys()))
				#if crucial_field not in product_catalog_dict.keys():
				if product_catalog_dict[crucial_field] == '':
					crucial_fields_given = False
					break

			if crucial_fields_given: 
				catalog_info = list(product_catalog_dict.values()) #[sheet1_sku] #, coll_name, product_type, intro, color, material, finish, length, width, height, weight, features, sheet1_cost, img_links, barcode]
				#print("catalog_info: " + str(catalog_info))
				catalog.append(catalog_info)
			else:
				print("Warning: Missing fields for SKU " + sheet1_sku + ", so product not uploaded!")




		

	return catalog


def generate_catalog(vendor):
	print("\n===Generate Catalog Given Vendor " + vendor + " ===\n")

	catalog = []

	ext = 'tsv'

	# header names given by vendor, rather than determining index
	# these below headers are for acme but should be generalized for all vendors
	price_sheet_sku_name = "sku"
	price_sheet_price_name = "price"
	spec_sheet_title_name = "title"
	spec_sheet_sku_name = "sku"
	spec_sheet_weight_name = 'weight'
	spec_sheet_length_name = 'length'
	spec_sheet_width_name = 'width'
	spec_sheet_height_name = 'height'
	spec_sheet_coll_name = 'collection name'
	spec_sheet_type_name = 'type'
	spec_sheet_features_name = 'features'
	spec_sheet_descrip_name = 'description'
	spec_sheet_finish_name = 'finish'
	spec_sheet_material_name = 'material'
	img_sheet_sku_name = "sku"
	img_sheet_links_name = "image links"

	#catalog_dict = {} # store lists based on desired field name key
	desired_field_names = ['sku'] # determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	current_sheet_field_name = '' # loop thru each sheet and each field in each sheet

	if vendor == 'acme':
		# for unknown no. sheets with unknown contents
		# for user input, we have their list of files to loop thru

		# data_files = ['price sheet test', 'spec sheet test', 'image sheet test'] # for acme, price sheet, spec sheet, and img sheet separate
		# all_sheet_all_field_values = [] # only relevant fields?
		# for data_type in data_files:
		# 	current_sheet_all_field_values = []
		# 	print("\n====== Read Sheet: " + data_type + " ======\n")
		# 	# remove leading zeros from sku in price list to match sku in spec sheet
		# 	filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext

		# 	current_sheet_df = pandas.read_table(filepath).fillna('n/a')
		# 	current_sheet_df.columns = current_sheet_df.columns.str.strip() # remove excess spaces
		# 	current_sheet_headers = current_sheet_df.columns.values
		# 	print("current_sheet_headers: " + str(current_sheet_headers))
		# 	# first check if any desired fields
		# 	for desired_field_name in desired_field_names:

		# 		current_sheet_field_name = determiner.determine_field_name(desired_field_name, current_sheet_df)
		# 		if current_sheet_field_name != '':
		# 			all_current_sheet_field_values = []
		# 			if re.search('price', current_sheet_field_name.lower()):
		# 				all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.replace("$","").str.replace(",","").str.strip().tolist()
		# 			else:
		# 				all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().str.lstrip("0").tolist()
		# 			print("all_current_sheet_field_values: " + desired_field_name + " " + str(all_current_sheet_field_values))
		# 			current_sheet_all_field_values.append(all_current_sheet_field_values)
		# 		# for header in current_sheet_headers:
		# 		# 	if determiner.determine_matching_field(field_name, header):
		# 		# 		print("field_name matches header: " + field_name + ", " + header)

		# 	#all_current_sheet_field_values = current_sheet_df[current_sheet_field_name]
		# 	all_sheet_all_field_values.append(current_sheet_all_field_values)

		print("\n====== Read Price Sheet ======\n")
		data_type = 'price sheet test'

		# remove leading zeros from sku in price list to match sku in spec sheet
		filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
		#print("filepath: " + filepath)
		price_sheet_df = pandas.read_table(filepath).fillna('n/a')
		#print("price_sheet_df:\n" + str(price_sheet_df))
		price_sheet_df.columns = price_sheet_df.columns.str.strip() # remove excess spaces
		#print(price_sheet_df.columns.values)

		desired_field = 'sku'
		price_sheet_sku_name = determiner.determine_field_name(desired_field, price_sheet_df) #'Item#'
		all_price_sheet_skus = price_sheet_df[price_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
		#print("all_price_sheet_skus: " + str(all_price_sheet_skus))
		
		price_sheet_price_name = '2022   EAST PETE PRICE'
		all_price_sheet_prices = price_sheet_df[price_sheet_price_name].astype('string').str.replace("$","").str.replace(",","").str.strip().tolist()
		#print("all_price_sheet_prices: " + str(all_price_sheet_prices))


		# look for file in Data folder called acme-spec-sheet.tsv
		print("\n====== Read Spec Sheet ======\n")
		data_type = "spec sheet test"
		filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
		#print("filepath: " + filepath)
		spec_sheet_df = pandas.read_table(filepath).fillna('n/a')
		#print("spec_sheet_df:\n" + str(spec_sheet_df))
		spec_sheet_df.columns = spec_sheet_df.columns.str.strip() # remove excess spaces
		#print(spec_sheet_df.columns.values)

		spec_sheet_title_name = 'acme.name'
		spec_sheet_sku_name = 'acme.sku'
		spec_sheet_weight_name = 'acme.product_weight'
		spec_sheet_length_name = 'acme.product_length'
		spec_sheet_width_name = 'acme.product_width'
		spec_sheet_height_name = 'acme.product_height'
		spec_sheet_coll_name = 'acme.collection_name'
		spec_sheet_type_name = 'acme.product_type'
		spec_sheet_features_name = 'acme.description'
		spec_sheet_descrip_name = 'acme.short_description'
		spec_sheet_finish_name = 'acme.catalog_finish'
		spec_sheet_material_name = 'acme.material_detail'

		all_spec_sheet_titles = spec_sheet_df[spec_sheet_title_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_titles: " + str(all_spec_sheet_titles))
		all_spec_sheet_skus = spec_sheet_df[spec_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
		#print("all_spec_sheet_skus: " + str(all_spec_sheet_skus))
		all_spec_sheet_weights = spec_sheet_df[spec_sheet_weight_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_weights: " + str(all_spec_sheet_weights))
		all_spec_sheet_lengths = spec_sheet_df[spec_sheet_length_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_lengths: " + str(all_spec_sheet_lengths))
		all_spec_sheet_widths = spec_sheet_df[spec_sheet_width_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_widths: " + str(all_spec_sheet_widths))
		all_spec_sheet_heights = spec_sheet_df[spec_sheet_height_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_heights: " + str(all_spec_sheet_heights))
		all_spec_sheet_coll_names = spec_sheet_df[spec_sheet_coll_name].astype('string').str.strip().tolist()
		#print("all_spec_sheet_coll_names: " + str(all_spec_sheet_coll_names))
		all_spec_sheet_types = spec_sheet_df[spec_sheet_type_name].astype('string').str.strip().str.replace(";","-").tolist()
		#print("all_spec_sheet_types: " + str(all_spec_sheet_types))
		all_spec_sheet_features = spec_sheet_df[spec_sheet_features_name].astype('string').str.strip().str.replace(";","-").tolist()
		#print("all_spec_sheet_features: " + str(all_spec_sheet_features))
		all_spec_sheet_descrips = spec_sheet_df[spec_sheet_descrip_name].astype('string').str.strip().str.replace(";","-").tolist()
		#print("all_spec_sheet_descrips: " + str(all_spec_sheet_descrips))
		all_spec_sheet_finishes = spec_sheet_df[spec_sheet_finish_name].astype('string').str.strip().str.replace(";","-").tolist()
		#print("all_spec_sheet_finishes: " + str(all_spec_sheet_finishes))
		all_spec_sheet_materials = spec_sheet_df[spec_sheet_material_name].astype('string').str.strip().str.replace(";","-").tolist()
		#print("all_spec_sheet_materials: " + str(all_spec_sheet_materials))

		# look for file in Data folder called acme-image-links.tsv
		print("\n====== Read Image Sheet ======\n")
		data_type = "image sheet test"
		filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
		#print("filepath: " + filepath)
		img_sheet_df = pandas.read_table(filepath).fillna('n/a')
		#print("img_sheet_df:\n" + str(img_sheet_df))
		img_sheet_df.columns = img_sheet_df.columns.str.strip() # remove excess spaces
		#print(img_sheet_df.columns.values)

		img_sheet_sku_name = 'acme.sku'
		img_sheet_links_name = 'Image Array'

		all_img_sheet_skus = img_sheet_df[img_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
		#print("all_img_sheet_skus: " + str(all_img_sheet_skus))
		all_img_sheet_links = img_sheet_df[img_sheet_links_name].astype('string').str.strip().str.lstrip("[").str.rstrip("]").tolist()
		#print("all_img_sheet_links: " + str(all_img_sheet_links))

		print("\n === Display Catalog Info === \n")

		catalog = []

		for product_idx in range(len(all_price_sheet_skus)):

			price_sheet_sku = all_price_sheet_skus[product_idx] # use this to match with spec and image sheets
			cost = all_price_sheet_prices[product_idx]

			# init vars from spec sheet 
			coll_name = ""
			product_type = ""
			intro = ""
			color = ""
			material = ""
			finish = "" 
			length = ""
			width = ""
			height = ""
			weight = ""
			features = ""
			barcode = ""
			# and img sheet
			img_links = ""

			specs_given = False
			for spec_sheet_item_idx in range(len(all_spec_sheet_skus)):
				spec_sheet_sku = all_spec_sheet_skus[spec_sheet_item_idx]
				#print("spec_sheet_sku: " + spec_sheet_sku)

				if price_sheet_sku == spec_sheet_sku:
					specs_given = True
					# get specs for this product
					coll_name = all_spec_sheet_coll_names[spec_sheet_item_idx]
					#print("coll_name: " + coll_name)
					product_type = all_spec_sheet_types[spec_sheet_item_idx]
					if product_type == '' or product_type == 'n/a':
						print("Product Type is Blank for " + spec_sheet_sku)
						# use spec sheet name/title
						product_type = all_spec_sheet_titles[spec_sheet_item_idx].replace(coll_name,'').strip()
					#print("product_type: " + product_type)
					intro = all_spec_sheet_descrips[spec_sheet_item_idx]
					#print("intro: " + intro)
					color = all_spec_sheet_finishes[spec_sheet_item_idx] 
					#print("color: " + color)
					material = all_spec_sheet_materials[spec_sheet_item_idx] 
					#print("material: " + material)
					finish = "" # todo: acme gives finish and color together so separate them
					length = all_spec_sheet_lengths[spec_sheet_item_idx] 
					#print("length: " + length)
					width = all_spec_sheet_widths[spec_sheet_item_idx]
					#print("width: " + width)
					height = all_spec_sheet_heights[spec_sheet_item_idx]
					#print("height: " + height)
					weight = all_spec_sheet_weights[spec_sheet_item_idx]
					#print("weight: " + weight)
					features = all_spec_sheet_features[spec_sheet_item_idx] 
					#print("features: " + features)
					barcode = ""

					break

			if specs_given: # only proceed to img if specs given
				image_given = False
				for img_sheet_item_idx in range(len(all_img_sheet_skus)):
					img_sheet_sku = all_img_sheet_skus[img_sheet_item_idx]

					if price_sheet_sku == img_sheet_sku:
						# get imgs for this product
						img_links = all_img_sheet_links[img_sheet_item_idx]
						#print("img_links: " + img_links)
						if img_links != '' and img_links.lower() != 'n/a':
							image_given = True
						break

				# only add product with image
				if image_given:

					# when copied to spreadsheet, separate by semicolons
					#catalog_info = price_sheet_sku + ";" + coll_name + ";" + product_type + ";" + intro + ";" + color + ";" + material + ";" + finish + ";" + length + ";" + width + ";" + height + ";" + weight + ";" + features + ";" + cost + ";" + img_links + ";" + barcode
					# when used for input to product generator, use list
					catalog_info = [price_sheet_sku, coll_name, product_type, intro, color, material, finish, length, width, height, weight, features, cost, img_links, barcode]

					catalog.append(catalog_info)

				else:
					print("Warning: No image given for SKU " + price_sheet_sku + ", so product not uploaded!")
			else:
				print("Warning: No specs given for SKU " + price_sheet_sku + ", so product not uploaded!")

	return catalog

def generate_vrnt_price(cost, type, seller):

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
			common_multiplier = 1.5 #ideally > 1.8
			online_only_rate = 1.1
			# need a separate var to compute price with deliv, 
			# or just set it at the end before output
			common_deliv_rate = 1.0 #1.2 # calculate this to display in descrip, and incorporate into price as shipping rate
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
		rounded_price = roundup(vrnt_price)
		rounded_price = float(rounded_price)
		#print("Rounded Price Up To Nearest 100: " + str(rounded_price))

		remainder = rounded_price % vrnt_price
		#print("Remainder: " + str(remainder))

		if type == 'rugs':
			# if the remainder is below 30, round up; if 30 or above, round down
			if remainder >= 30:
				vrnt_price = rounddown(vrnt_price) - 0.01
			else:
				vrnt_price = rounded_price - 0.01
		else:
			# if the remainder is below 50, round up; if 50 or above, round down
			if remainder >= 50:
				vrnt_price = rounddown(vrnt_price) - 0.01
			else:
				vrnt_price = rounded_price - 0.01

		vrnt_price_string = str(vrnt_price)

		#print("Final Variant Price: " + vrnt_price_string)

	return vrnt_price_string

def generate_vrnt_compare_price(price):

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

# helper functions
def roundup(x):
	 return int(math.ceil(x / 100.0)) * 100

def rounddown(x):
	 return int(math.floor(x / 100.0)) * 100

def round_price(price):
	rounded_price = roundup(price)
	rounded_price = float(rounded_price)

	return rounded_price - 0.01
