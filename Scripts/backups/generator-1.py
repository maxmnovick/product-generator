# generator.py
# functions for a generator

import reader, re
import numpy as np

# def extract_data(input, extension):
# 	catalog_filename = "../Data/" + input + "-init-data." + extension
#
# 	lines = []
# 	data = []
# 	all_data = []
#
# 	with open(catalog_filename, encoding="UTF8") as catalog_file:
#
# 		current_line = ""
# 		for catalog_info in catalog_file:
# 			current_line = catalog_info.strip()
# 			lines.append(current_line)
#
# 		catalog_file.close()
#
# 	# skip header line
# 	for line in lines[1:]:
# 		if len(line) > 0:
# 			if extension == "csv":
# 				data = line.split(",")
# 			else:
# 				data = line.split("\t")
# 		all_data.append(data)
#
# 	return all_data

def extract_data(vendor, input, extension):
	catalog_filename = "../Data/" + vendor + "-" + input + "-init-data." + extension

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

def write_data(arranged_data, input):
	catalog_filename = "../Data/" + input + "-final-data.csv"
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	for row_idx in range(len(arranged_data)):
		catalog_file.write(arranged_data[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()
	
def generate_title(item_details):
	handle = title = ''

	if len(item_details) > 0:
		handle = item_details[1].strip().lower()
		#print("Handle: " + handle)

	handle_words = re.split('-',handle)
	#print("Handle Words: " + str(handle_words))

	for word in handle_words:
		word = word.capitalize()
		title += word + ' '
	title = title.rstrip()
	#print(title)
	
	return title
	
def generate_product_type(item_details):
	handle = final_type = ''

	handle_data = []

	output = "type"
	all_keywords = reader.read_keywords(output)

	# look at item handle to determine type
	if len(item_details) > 0:
		handle = item_details[1].strip().lower() # need to know field number in given table

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
		print("Warning: No details for this item!")
		
	return final_type

def generate_options(item_details):
	sku = color = title = ''

	output = "option"
	all_keywords = reader.read_keywords(output)

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

		final_opt_names = []
		final_opt_values = []

		final_opt_string = ''

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

			#print("======Checked for Option Name: " + option_name + "\n")

		#print("===Generated Options for SKU: " + sku + "\n")
	else:
		print("Warning: No details for this item!")

	final_opt_data = [ final_opt_names, final_opt_values ]

	return final_opt_data

def isolate_detail_field(all_details, field_title):
	detail_field_values = []

	handle_idx = 1
	field_idx = 0
	if field_title == "handle":
		field_idx = handle_idx

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		field_value = item_details[field_idx]
		detail_field_values.append(field_value)

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

def generate_colors_fmla(product):

	final_colors_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_colors(product): # if we are NOT given colors we do not include colors in the description
		final_colors_fmla = "\"Colors: \"" # only if at least 1 of the variants has colors
		
		opt_name = 'Color' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		color_options = options[opt_name]
		#print("Color Options: " + str(color_options))

		valid_opt = False
		
		for variant in product:
			
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
				
			option_data = generate_options(variant)
			
			if len(option_data) > 0:
				option_names = option_data[0]
				option_values = option_data[1]

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				if current_opt_name == opt_name:
					valid_opt = True
					break
				opt_idx += 1

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

def generate_dimensions_fmla(product):
	
	dimensions_fmla = "\"\"" # init fmla for this part of the description
	if determine_given_dimensions(product): # if we are NOT given dimensions we do not include dimensions in the description
		dimensions_fmla = "\"Dimensions (in): \"" # only if at least 1 of the variants has dimensions
		
		#sizes = set_option_values(product, 'Size')
		opt_name = 'Size' # choose what option we want to show
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		size_options = options[opt_name]
		
		valid_opt = False

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

			option_data = generate_options(variant)
			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				option_values = option_data[1]

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				if current_opt_name == opt_name:
					valid_opt = True
					break
				opt_idx += 1

			if valid_opt:
				opt_value = option_values[opt_idx]

				opt_fmla = dim_fmla

				size_options[opt_value] = opt_fmla

		#print(opt_name + ": " + str(size_options))

		# now we have populated all size values for this product
		# so create dim fmla by looping through sizes and printing those with valid values
		if valid_opt:
			#print("Dimensions: ")
			for size, dims in size_options.items():
				if dims != '':
					size_fmla = "\"" + size + ": \","
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
		
		if len(variant) > 10:
			handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			features = variant[10].strip()
			#print("Features: " + features)
			
		if features != '' and features != 'n/a':
			features = re.sub('\"','\",CHAR(34),\"', features) # if quotes found in features, such as for dimensions, then fmla will incorrectly interpret that as closing string
			features = re.sub(' •','. •', features) # add periods at end of lines
			if features[-1] != '.':
				#print("Last character: " + features[-1])
				features += '. '
			features = re.sub('•','\",CHAR(10),\"• \",\"', features) # bullet point indicates new line
			features = re.sub('    ','\",CHAR(10),\"• \",\"', features) # 4 spaces indicates new line
			features = re.sub('ï','\",CHAR(10),\"• \",\"', features) # ï character indicates new line (for Coaster)
			features_fmla = "\"" + features + "\""
		#print("Features Formula: " + features_fmla)

	return features_fmla
