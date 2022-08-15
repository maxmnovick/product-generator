# generator.py
# functions for a generator

import reader, re, datetime, math
import numpy as np

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

# get data from a file and format into a list
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
	catalog_filename = "../Data/" + vendor + "-" + output + "-import." + extension
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	for row_idx in range(len(arranged_data)):
		catalog_file.write(arranged_data[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()

# title is based on handle
def generate_title(item_details):
	handle = title = ''

	if len(item_details) > 0:
		handle = item_details[1].strip().lower()
		#print("Handle: " + handle)

		if handle != '':
			handle_words = re.split('-',handle)
			#print("Handle Words: " + str(handle_words))

			for word in handle_words:
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
def generate_all_titles(all_details):
	all_titles = []

	for item_details in all_details:
		title = generate_title(item_details)
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
			color_tags += "color-" + color + ", "
	color_tags = color_tags.rstrip(', ')
	#print("Color Tags: " + color_tags)
	for material in material_data:
		material = material.strip()
		material = material.rstrip(' -') # for Global but maybe also for others
		material = material.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if material != '':
			material_tags += "material-" + material + ", "
	material_tags = material_tags.rstrip(', ')
	#print("Material Tags: " + material_tags)
	for finish in finish_data:
		finish = finish.strip()
		finish = finish.rstrip(' -') # for Global but maybe also for others
		finish = finish.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if finish != '':
			finish_tags += "finish-" + finish + ", "
	finish_tags = finish_tags.rstrip(', ')
	#print("Finish Tags: " + finish_tags)

	tags = vendor + publication_year

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
		handle = item_details[1].strip().lower() # need to know field number in given table

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

	return final_type

def generate_all_product_types(all_details):
	all_product_types = []

	for item_details in all_details:
		types = generate_product_type(item_details)
		all_product_types.append(types)

	return all_product_types

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

def generate_description(product, init_product):
	descrip_instances = []

	intro_fmla = generate_intro_fmla(product)

	colors_fmla = generate_colors_fmla(product,init_product)

	materials_fmla = generate_materials_fmla(product)

	finishes_fmla = generate_finishes_fmla(product)

	dimensions_fmla = generate_dimensions_fmla(product,init_product)

	features_fmla = generate_features_fmla(product)

	#arrival_fmla = generate_arrival_fmla(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

	descrip_fmla = "=CONCATENATE(" + intro_fmla  + ",CHAR(10)," + colors_fmla  + ",CHAR(10)," + materials_fmla  + ",CHAR(10)," + finishes_fmla  + ",CHAR(10)," + dimensions_fmla + ",CHAR(10)," + features_fmla + ")"

	# all variants of the product get the same description
	# the variants must be ordered by options, based on knowledge of desired option order and available options
	for variant in product:
		descrip_instances.append(descrip_fmla)

	return descrip_instances

def generate_all_descriptions(all_details, init_all_details):
	all_descriptions = []

	init_products = isolate_products(init_all_details)
	products = isolate_products(all_details)

	for product_idx in range(len(products)):
		product = products[product_idx]
		init_product = init_products[product_idx]
		descrip_instances = generate_description(product, init_product)
		for descrip_instance in descrip_instances:
			all_descriptions.append(descrip_instance)

	return all_descriptions

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
	for vrnt_idx in range(len(sorted_product)):
		variant = sorted_product[vrnt_idx]
		vrnt_data = variant.split(';')

		#print("Variant Data: " + str(vrnt_data[6:12]))
		#print("Question Variant Data: " + str(q_vrnt_data[6:12]))
		#print()

		relevant_vrnt_data = vrnt_data[6:12]
		relevant_q_vrnt_data = q_vrnt_data[6:12]
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

	handles = np.array(isolate_detail_field(all_details, field_title))

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
			break;

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
			break;

	#print("Products: " + str(products) + "\n")
	return products

def capitalize_sentences(intro):
	final_intro = ''

	intro_sentences = intro.split('.')
	#print("intro_sentences: " + str(intro_sentences))
	for sentence in intro_sentences:
		if sentence != '':
			#print("sentence: " + sentence)
			sentence = sentence.strip().capitalize() + '. '
			final_intro += sentence

	return final_intro

def generate_intro_fmla(product):
	intro_fmla = "\"\""

	for variant in product:

		intro = ''

		if len(variant) > 3:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			intro = variant[3].strip().lower()
			#print("Intro: " + intro)

		if intro != '' and intro != 'n/a':
			intro = capitalize_sentences(intro)
			intro = re.sub('\"','\",CHAR(34),\"', intro) # if quotes found in intro, such as for dimensions, then fmla will incorrectly interpret that as closing string
			intro_fmla = "\"" + intro + "\""
		#print("Intro Formula: " + intro_fmla)

	return intro_fmla

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

				opt_fmla = colors_fmla

				color_options[opt_value] = opt_fmla

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
			if re.search('\'\s*\d+\'',width):
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
			if re.search('\'\s*\d+\'',width):
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

def generate_features_fmla(product):
	features_fmla = "\"\""

	for variant in product:

		features = ''

		if len(variant) > 11:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			features = variant[11].strip()
			#print("Features: " + features)

		if features != '' and features != 'n/a':
			# need better way to check if there are no proper nouns that should stay capitalized, b/c too blunt to lowercase everything
			features = features.lower()
			features = capitalize_sentences(features).strip()

			features = re.sub('\"','\",CHAR(34),\"', features) # if quotes found in features, such as for dimensions, then fmla will incorrectly interpret that as closing string
			features = re.sub(' •','. •', features) # add periods at end of lines
			if features[-1] != '.':
				#print("Last character: " + features[-1])
				features += '. '
			features = re.sub('•','\",CHAR(10),\"• \",\"', features) # bullet point indicates new line
			features = re.sub('    ','\",CHAR(10),\"• \",\"', features) # 4 spaces indicates new line
			features = re.sub('ï|Ï','\",CHAR(10),\"• \",\"', features) # ï character indicates new line (for Coaster)
			features_fmla = "\"" + features + "\""
		#print("Features Formula: " + features_fmla)

	return features_fmla

# helper functions
def roundup(x):
	 return int(math.ceil(x / 100.0)) * 100

def rounddown(x):
	 return int(math.floor(x / 100.0)) * 100
