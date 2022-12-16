# generator.py
# functions for a generator

import reader, writer, determiner
import isolator # for isolating products in list of all products
import re, math, random, pandas # random number for random sale item to set compare price
import numpy as np
import sorter # sort variants by size
import converter # convert list of items to fields (like transpose matrix), for generating catalog from info

from datetime import date # get today's date to display when availability updated in product descrip
from datetime import datetime # get current date and convert given eta date to datetime for difference

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
		intro = item_details[intro_idx]

		# get features to check if a table is round bc not always differentiated bt round and rect tables in same collection
		features = item_details[features_idx]

		# keywords in form without dashes so remove excess from descrip to compare to keywords
		plain_descrip = descrip.lower().strip()
		#print("plain_descrip: " + plain_descrip)
		plain_features = features.lower().strip()
		#print("plain_features: " + plain_features)
		plain_intro = intro.lower().strip()
		#print("plain_intro: " + plain_intro)

		for title_suffix, title_keywords in all_keywords.items():
			#print("Title Suffix: " + title_suffix)
			#print("Title Keywords: " + str(title_keywords))
			for keyword in title_keywords:
				#print("Keyword: " + keyword + "\n")
				if re.search(keyword,plain_descrip):
					final_title_suffix = title_suffix
					if final_title_suffix == 'bed':
						if re.search('loft bed',plain_intro):
							final_title_suffix = 'loft bed'
					elif final_title_suffix == 'dining table':
						if re.search('single pedestal',plain_intro):
							final_title_suffix = 'single pedestal dining table'
						elif re.search('double pedestal',plain_intro):
							final_title_suffix = 'double pedestal dining table'
						elif re.search('trestle',plain_intro):
							final_title_suffix = 'trestle dining table'
					elif final_title_suffix == 'chair':
						if re.search('dining',plain_intro):
							final_title_suffix = 'dining chair'
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
			print("item_details: " + str(item_details))

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
				abbrevs = ['TV']
				roman_numerals = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
				if word.upper() in roman_numerals or word.upper() in abbrevs:
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
def generate_tags(item_details, vendor, item_inv={}):
	print("\n===Generate Item Tags===\n")
	now = datetime.now()
	publication_year = str(now.year) # get current year

	sku = handle = colors = materials = finishes = ''

	color_data = []
	material_data = []
	finish_data = []

	tags = color_tags = material_tags = finish_tags = ''

	if len(item_details) > 0:
		sku = item_details[0].strip().lower()
		handle = item_details[1].strip().lower()
		colors = item_details[color_idx].strip().lower()
		#print("Colors: " + colors)
		materials = item_details[mat_idx].strip().lower()
		materials = re.sub('full ','',materials)
		materials = re.sub(' front','',materials)
		materials = re.sub(' back','',materials)
		#print("Materials: " + materials)
		finishes = item_details[finish_idx].strip().lower()
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

	# we need to condense raw colors into standard colors so tags can be used as a limited selection of color filters
	standard_colors = [] # need to avoid duplicates
	for color in color_data:
		# given raw color, does it fit into standard color? 1 to many relation. purpose of standards/color.json
		color = color.strip()
		color = color.rstrip(' -') # for Global but maybe also for others
		color = color.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		if color != '':

			standard_color = determiner.determine_standard(color,"colors")
			if standard_color != '' and standard_color not in standard_colors: # need to avoid duplicates
				standard_colors.append(standard_color)
				color_tags += "Color: " + standard_color.title() + ", "
	color_tags = color_tags.rstrip(', ')
	#print("Color Tags: " + color_tags)

	standard_materials = [] # need to avoid duplicates
	for material in material_data:

		material = material.strip()
		material = material.rstrip(' -') # for Global but maybe also for others
		material = material.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling

		if material != '':
			#print("material: " + material)
			standard_material = determiner.determine_standard(material,"materials")
			if standard_material != '' and standard_material not in standard_materials: # need to avoid duplicates
				standard_materials.append(standard_material)
				material_tags += "Material: " + standard_material.title() + ", "
	material_tags = material_tags.rstrip(', ')
	#print("Material Tags: " + material_tags)

	for finish in finish_data:
		
		finish = finish.strip()
		finish = finish.rstrip(' -') # for Global but maybe also for others
		finish = finish.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
		
		if finish != '':
			#print("finish: " + finish)
			standard_finish = determiner.determine_standard(finish,'colors')
			if standard_finish != '' and standard_finish not in standard_colors: # need to avoid duplicates
				standard_colors.append(standard_finish)
				finish_tags += "Color: " + standard_finish.title() + ", " # use color tag although finish type bc then combines where other instances use color
	finish_tags = finish_tags.rstrip(', ')
	#print("Finish Tags: " + finish_tags)

	
	tags = "Catalog " + publication_year # desired space bt vendor and pub yr in case vendor name has multiple parts

	if colors != "n/a":
		tags += ", " + color_tags

	if materials != "n/a":
		tags += ", " + material_tags

	if finishes != "n/a":
		tags += ", " + finish_tags

	# add location tag based on inventory
	# if inv>0 at location, add tag for location
	#print("item_inv: " + str(item_inv))
	for key, val in item_inv.items():
		if re.search("qty",key):
			loc = re.sub("locations\\.|_qty","",key)
			if round(float(val)) > 0:
				loc_tag = "Location: " + loc.upper()
				#print("loc_tag: " + loc_tag)

				tags += ", " + loc_tag

	return tags

def generate_all_tags(all_details, vendor, all_inv=[]):
	print("\n===Generate All Tags===\n")
	all_tags = []

	for item_details in all_details:
		item_sku = item_details[sku_idx]
		item_inv = {}
		for inv in all_inv:
			if item_sku == inv['sku']:
				item_inv = inv
				break
		
		tags = generate_tags(item_details, vendor, item_inv)
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
						final_type = ''
						#print("Found type: \'" + type + '\'')
						type_words = type.split()
						#print("type_words: " + str(type_words))
						abbrevs = ['TV']
						for word_idx in range(len(type_words)):
							word = type_words[word_idx]
							

							if word.upper() in abbrevs:
								word = word.upper()
							else:
								word = word.capitalize()

							if word_idx == 0:
								final_type += word # or =word
							else:
								final_type += " " + word
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

def generate_product_img_src(item_details):

	img_src = item_details[img_src_idx]

	if img_src == 'n/a':
		img_src = ''

	elif re.search('drive.google.com',img_src):
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

# products = { "<sku>": { "handle":"<handle>", "description":"<description>"  } }
# dict = { <sku>:<option string> }
def generate_options_dict(all_details, init_all_details):
	print("\n===Generate Options Dictionary===\n")
	# instead of saving options instances and relying on them to align with product variants, 
	# make dictionary matching options data to product sku
	# and then when setting the options, use the product sku as the key
	options_dict = {}
	

	init_products = isolator.isolate_products(init_all_details)
	products = isolator.isolate_products(all_details) # why isolate products and not go line by line in all details?

	for product_idx in range(len(products)):
		product = products[product_idx]
		item_details = product[0]
		# handle = generate_handle(item_details)
		# print("handle: " + handle)
		init_product = init_products[product_idx]
		options = generate_product_options_dict(product, init_product)

		# we need the whole product created to set bundle sku
		# but at this point we need to set options to determine bundle sku
		# so do we set by single sku here and then use options to correct sku later
		# or do we pass in single skus and then pass out bundle skus if needed immediately
		#options_dict[sku] = options

	#print("options_dict: " + str(options_dict))
	return options_dict

# all_products = [[]] from catalog all details
# input catalog with some formatting but also init to detect types before formatting
def generate_product_options_dict(product, init_product):
	print("\n===Generate Product Options Dict===\n")
	product_options = {}

	product_options = generate_product_options(product, init_product)
	for vrnt_idx in range(len(product)):
		vrnt = product[vrnt_idx]
		sku = vrnt[sku_idx]
		vrnt_options = product_options[vrnt_idx]
		product_options[sku] = vrnt_options

	print("product_options: " + str(product_options))
	return product_options

def generate_vrnt_options(product, init_product, sku):
	vrnt_options = []

	product_options = generate_product_options_dict(product, init_product)

	vrnt_options = product_options[sku]

	return vrnt_options
	

# def generate_product_options_dict(product, init_product):
# 	print("\n=== Generate Product Options ===\n")
# 	product_options = []

# 	for vrnt_idx in product:
# 		vrnt = product[vrnt_idx]
# 		init_vrnt = init_product[vrnt_idx]

# 		vrnt_handle = generate_handle(vrnt)
# 		if re.search("loft-bed",vrnt_handle):
# 			# if twin loft bed, option will be loft bed only
# 			# if optional queen for loft, option will be loft + queen
# 			vrnt_type = vrnt[title_idx]
# 			opt_name = 'Components'
# 			if re.search('twin\\sloft\\sbed',vrnt_type.lower()):
# 				opt_value = 'Loft Bed Only'
# 			elif re.search('queen\\sbed', vrnt_type.lower()):
# 				opt_value = 'Loft Bed + Queen Bed'


# 		vrnt_options = generate_vrnt_options(vrnt, init_vrnt)
# 		product_options.append(vrnt_options)
# 	return product_options

# if coffee table where one says no storage and other says storage, make options no storage and storage
# def generate_all_product_options(all_details, init_all_details):
# 	print("\n=== Generate All Product Options ===\n")
# 	# if loft bed with optional queen bed, only consider component options, nothing else
# 	# later we can incorporate other options but for now only components needed bc only 1 color, size, etc
# 	all_products = isolator.isolate_products(all_details)
# 	init_all_products = isolator.isolate_products(init_all_details)

# 	all_product_options = []
# 	for product_idx in range(len(all_products)):
# 		product = all_products[product_idx]
# 		init_product = init_all_products[product_idx]

# 		vrnt_options = []
# 		for vrnt_idx in range(len(product)):
# 			vrnt = product[vrnt_idx]
# 			init_vrnt = init_product[vrnt_idx]

# 			options = generate_options(vrnt, init_vrnt) # we need init details to detect measurement type
# 			option_names = options[0]
# 			option_values = options[1]
# 			#print("Options: " + str(options))
# 			option_string = ''
# 			for opt_idx in range(len(option_names)):
# 				option_name = option_names[opt_idx]
# 				option_value = option_values[opt_idx]
# 				if opt_idx == 0:
# 					option_string += option_name + "," + option_value
# 				else:
# 					option_string += "," + option_name + "," + option_value
# 			vrnt_options.append(option_string)

# 		all_product_options.append(vrnt_options)


# 	return all_product_options

# this fcn should return a complete list of options but should those only be options that have multiple different values or all features that could potentially be an option? both
def generate_options(item_details, init_item_details):

	final_opt_names = []
	final_opt_values = []

	# look at item sku to determine options
	# if nothing apparent from sku, then check other fields like color and material
	# do not rely entirely on sku b/c could be ambiguous codes that may appear as part of other words not meant to indicate options
	# example: W is code for wenge brown for vendor=Global, but W is likely to mean something else for other vendors
	if len(item_details) > 0:

		sku = item_details[sku_idx].strip().lower()
		#print("===Generate Options for SKU: " + sku)

		init_width = init_item_details[width_idx].strip().lower()
		#print("Init Width: " + init_width)
		handle = generate_handle(item_details)
		meas_type = reader.determine_measurement_type(init_width, handle)

		sku = color = title = ''

		output = "option"
		all_keywords = reader.read_keywords(output)



		
		title = item_details[title_idx].strip().lower()
		item_color = item_details[color_idx].strip().lower()
		#print("Color: " + color)
		if item_color == '' or item_color == 'n/a':
			item_color = item_details[finish_idx].strip().lower()
		#print("item_color: " + item_color)

		colors = re.split("\\s*&\\s*|\\s*,\\s*|\\s*and\\s*",item_color)
		#print("colors: " + str(colors))

		# option codes must only be considered valid when they are the entire word in the sku, so must remove dashes to separate words and isolate codes
		dashless_sku = re.sub('-',' ',sku)

		final_opt_string = ''

		# need length/depth to determine if twin or full size bed bc both in type
		# and rugs
		#generate_size_options(item_details)
		depth = item_details[depth_idx].strip()
		
		type = generate_product_type(item_details)
		if type == 'rugs':
			option_name = 'Size' # width-depth combos are options for rugs
			# see if dims given
			width = item_details[width_idx].strip()
			
			if width != 'n/a' and depth != 'n/a':
				dim_string = width + "\" x " + depth + "\""
				if meas_type == 'round':
					dim_string = width + "\" Diameter"
				final_opt_values.append(dim_string)
				final_opt_names.append(option_name)

		# if loft bed with optional queen bed for loft bed, need to look for component options
		# see if colors given, one for twin and one for queen
		# or both twin and queen have multiple colors. if twin and queen have multiple colors, separate color options within same product so they would be Loft Color and Queen Color

		color_values = [] # hold standard color option values based on raw colors
		# loop for each type of option, b/c need to fill in value for each possible option (eg loop for size and then loop for color in case item has both size and color options)
		final_opt_value = ''
		for option_name, option_dict in all_keywords.items():
			#print("======Check for Option Name: " + option_name)
			#print("Option Dict: " + str(option_dict))

			# for material option, only look in color or finish field, not materials field, bc if multiple materials found in materials field that does not mean they are options but that they are all materials used together

			

			
			# options with single values like size
			for option_value, option_keywords in option_dict.items():
				#print("Option Value: " + option_value)
				#print("Option Keywords: " + str(option_keywords))

				for keyword in option_keywords:
					#print("Keyword: " + keyword)
					#print("Plain SKU: " + dashless_sku)
					if option_name.lower() != 'material': # material indicates option only if found in color field/finish field
						# search sku first
						# need to have different keywords when searching sku bc sku uses abbrevs that will be found in other fields with different meanings
						if re.search(keyword,dashless_sku):
							final_opt_value = option_value
							final_opt_values.append(final_opt_value)

							final_opt_names.append(option_name)

							final_opt_string += option_name + "," + final_opt_value + ","
							break

						# if no codes found in sku, check other fields for this item such as title field
						if re.search(keyword,title):
							if re.search("twin.*full",title):
								if float(depth) < 80.0: #inches
									final_opt_value = "Twin"
								else:
									final_opt_value = "Full"
							else:
								final_opt_value = option_value

							final_opt_values.append(final_opt_value)

							final_opt_names.append(option_name)

							final_opt_string += option_name + "," + final_opt_value + ","

							break

					# if no codes found in sku, check other fields for this item such as color field
					# if re.search(keyword,color):
					# 	#print("Found color option: " + keyword + ", " + color)
					# 	final_opt_value = option_value # commented out bc we need to go to next color even though we already found 1 color bc there could be multiple colors
					# 	final_opt_values.append(final_opt_value)

					# 	final_opt_names.append(option_name)

					# 	# final_opt_string += option_name + "," + final_opt_value + ","
						
					# 	break # we break here bc we found matching keyword in color so go to next opt val to see if any more option value keywords in color
					
					
					
					# for color in colors:
					# 	if re.search(keyword,color):
					# 		color_values.append(option_value) # store first match
							
					# 		#print("Found color option: " + keyword + ", " + color)
					# 		#final_opt_value = option_value # commented out bc we need to go to next color even though we already found 1 color bc there could be multiple colors
					# 		# final_opt_values.append(final_opt_value)

					# 		# final_opt_names.append(option_name)

					# 		# final_opt_string += option_name + "," + final_opt_value + ","
							
					# 		break # we break here bc we found matching keyword in color so go to next opt val to see if any more option value keywords in color
					


				# we do not want to break here bc we need to see all matching opt vals
				# problem is some matches rely on breaking otherwise will find multiples such as finding "red" in "weathered white". 
				# to avoid this need to break by comma, & or other separator and then eval each item
				# OR make better regex requiring "r" to be the first letter in the string for "red" and so on but that is case by case whereas separating by delimiter is more reliable. eg we wont see black red as often as black & red unless typo
				if final_opt_value != '':
					#print("Final Option Name: " + option_name)
					#print("Final Option Value: " + final_opt_value)
					#print("Option String: " + final_opt_string + "\n")


					# see if valid options, given known loft bed from handle
					break

		# check color field for materials bc sometimes placed there to differentiate
		option_name = 'Material'
		materials_dict = all_keywords[option_name]
		#print("materials_dict: " + str(materials_dict))
		opt_val = ''
		duplicate_keywords = ["poplar","eucalyptus","oak","maho?ga?ny","larch","pine","linen"] # keywords that apply to both color and material so are misleading like oak
		for option_value, option_keywords in materials_dict.items():
			#print("Option Value: " + option_value)
			#print("Option Keywords: " + str(option_keywords))

			for keyword in option_keywords:
				if re.search(keyword,item_color) and keyword not in duplicate_keywords:
					opt_val = option_value 
					final_opt_values.append(opt_val)

					final_opt_names.append(option_name)
					break

			if opt_val != '':
				break


		# options with multiple values like color
		color_dict = all_keywords['Color']
		#print("color_dict: " + str(color_dict))
		for color in colors:
			opt_val = ''
			for option_value, option_keywords in color_dict.items():
				#print("Option Value: " + option_value)
				#print("Option Keywords: " + str(option_keywords))

				for keyword in option_keywords:
					if re.search(keyword,color):
						color_values.append(option_value) # store first key match
						opt_val = option_value
						break

				if opt_val != '':
					break

		# once we see all opt vals we can create string, and data
		if len(color_values) > 0:
			#print("color_values: " + str(color_values))
			opt_val = '' # hold option val string as we build it with multiple vals
			option_name = "Color"
			final_opt_names.append(option_name)
			for c_idx in range(len(color_values)):
				c = color_values[c_idx] # color val is the standard option value as opposed to the raw value 
				if c_idx == 0:
					opt_val += c
				else:
					opt_val += " & " + c
			final_opt_values.append(opt_val)

			#print("======Checked for Option Name: " + option_name + "\n")\



		#print("===Generated Options for SKU: " + sku + "\n")
	else:
		print("Warning: No details for this item!")

	final_opt_data = [ final_opt_names, final_opt_values ]

	# fill in blank options bc always need same number limited by product import tool or ecom platform
	final_opt_data = writer.format_option_data(final_opt_data)

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

# we need this fcn to generate opts for all vrnts in product
# need all vrnts opts to generate description, arrival, intro, features, etc
# product = [] from catalog all details
# do we need init product bc values get altered while formatting measurements?
def generate_product_options(product, init_product):
	handle = generate_handle(product[0])
	print("\n===Generate Product Options for " + handle + "===\n")
	product_options = [] # post process
	init_product_opt_data = [] # pre process
	product_opt_data = [] # for processing

	# init options only accounting for single vrnt
	# may change to account for whole product initially
	for vrnt_idx in range(len(product)):
		vrnt = product[vrnt_idx]
		init_vrnt = init_product[vrnt_idx]

		vrnt_opts = generate_options(vrnt, init_vrnt) # [[names],[vals]]
		init_product_opt_data.append(vrnt_opts)

	product_opt_data = determiner.determine_duplicate_product_opts(init_product_opt_data) # [[[names],[values]]]
	if len(product_opt_data) > 0: # we know duplicate opts so create new opt data
		weights =[]
		widths = []
		depths = []
		heights = []
		for vrnt in product:
			weights.append(vrnt[weight_idx])
			widths.append(vrnt[width_idx])
			depths.append(vrnt[depth_idx])
			heights.append(vrnt[height_idx])
		print("weights: " + str(weights))
		print("widths: " + str(widths))
		print("depths: " + str(depths))
		print("heights: " + str(heights))

		# or use differing dim in option val
		dims = [widths, depths, heights]
		differ_dim_idx = 0
		all_differ = True
		for dim_idx in range(len(dims)):
			dim = dims[dim_idx]
			# if all dim vals same, cant use to differ
			# if any 2 dim vals are same we cannot use to differ
			
			for val in dim:
				if dim.count(val) > 1: # if the multiple that are the same also have the same options
					all_differ = False
					break

			# if it did not find 2 same in dim then use this dim to differ
			if all_differ:
				differ_dim_idx = dim_idx
				break

		# if all dims same, see if all weights differ
		# if weight is greatest add opt size large
		# get idx of max element in weights

		# if no differing factors, then mark for exclusion and warn user
		# by returning empty list could imply no differing factors
		if all_differ:
			for vrnt_idx in range(len(product_opt_data)):
				vrnt_opt_data = product_opt_data[vrnt_idx]
				print("init vrnt_opt_data: " + str(vrnt_opt_data)) # [[names],[vals]]
				differ_dim = dims[differ_dim_idx]
				dim_types = ['width','depth','height']
				differ_dim_type = dim_types[differ_dim_idx]
				opt_names = vrnt_opt_data[0]
				opt_vals = vrnt_opt_data[1]
				for opt_idx in range(len(opt_names)):
					# opt_name = opt_names[opt_idx]
					# opt_val = opt_vals[opt_idx]
					if opt_names[opt_idx] == '':
						opt_names[opt_idx] = differ_dim_type.title()
						opt_vals[opt_idx] = differ_dim[vrnt_idx]
						break

				print("final vrnt_opt_data: " + str(vrnt_opt_data)) # [[names],[vals]]
				product_options.append(vrnt_opt_data)


		if len(product_options) == 0:
			print("Warning: invalid options for " + handle)

	else:
		product_options = init_product_opt_data

	#print("product_options: " + str(product_options)) [[[names],[vals]]]
	return product_options

# all_products = [[]] from catalog all details
# input catalog with some formatting but also init to detect types before formatting
def generate_all_product_options(catalog, init_catalog):
	print("\n===Generate All Product Options===\n")
	all_product_options = {}

	all_products = isolator.isolate_products(catalog)
	all_init_products = isolator.isolate_products(init_catalog)

	for product_idx in range(len(all_products)):
		product = all_products[product_idx]
		init_product = all_init_products[product_idx]

		product_options = generate_product_options(product, init_product)
		for vrnt_idx in range(len(product)):
			vrnt = product[vrnt_idx]
			sku = vrnt[sku_idx]
			vrnt_options = product_options[vrnt_idx]
			all_product_options[sku] = vrnt_options

	print("all_product_options: " + str(all_product_options))
	return all_product_options

def generate_inv_locations(all_inv):
	print("\n===Generate Inventory Locations===\n")
	#print("all_inv: " + str(all_inv))
	locations = []
	headers = all_inv[0].keys()
	#print("headers: " + str(headers))
	for header in headers:
		if re.search("qty", header):
			location = re.sub("locations\\.|_qty", "", header)
			location = location.lower()
			# if len(location) > 3:
			# 	location = location.title()
			# else:
			# 	location = location.upper()
			#print("location: " + location)
			locations.append(location)

	#print("locations: " + str(locations))
	return locations

# if no vendor given, we can only tell if available immediately
# bc vendor tells us duration of moving bt warehouses
def generate_arrival_html(product, init_product, all_inv, vendor=''):
	#print("\n===Generate Arrival HTML===\n")
	#print("product: " + str(product))
	#print("init_product: " + str(init_product))
	#print("all_inv: " + str(all_inv))


	updated_date = date.today().strftime("%d-%b-%Y") # %d-%m-%y
	updated_date_html = '<p class=\'updated_date\'>Updated: ' + str(updated_date) + '</p>'

	nj_to_ny = 2 # weeks
	ca_to_ny = 4 # weeks, ca is both la and sf
	valid_locations = ['ny', 'nj', 'la', 'sf']


	# if all inv given but any of the vrnts in product are not in it, 
	# then need to decide if any vrnts are available in inv
	# if no vrnts in product are given, show inv tracking not available
	inv_tracking = False
	if len(all_inv) > 0:
		# if any vrnt given inv, we know at least one inv tracked
		for vrnt in product:
			for item_inv in all_inv:
				vrnt_sku = vrnt[sku_idx]
				item_sku = item_inv['sku']
				if vrnt_sku == item_sku:
					inv_tracking = True
					break
			if inv_tracking == True:
				break
		# if some but not all vrnts are given inv, include after table like 
		# no inv tracking, call to ask for inventory
		# option, call <phone>

	available_title_html = ''
	all_locations_html = ''
	if inv_tracking == False:
		print("No inv tracking for this product " + str(product[0][title_idx]))
		available_title_html = '<h2>Available, Call for Arrival Time</h2>'
	else:
		available_title_html = '<h2>Available After Order</h2>'
		all_locations_html = ''
		locations = generate_inv_locations(all_inv)
		# create a section for each location
		for location in locations:
			#print("location: " + location)
			available_location = 'ny' # consider making items available at the cities they are stocked only because could arrange delivery from there
			if location.lower() ==  available_location.lower():
				# format location title
				location_title_html = '<h3>' # class='product_location_title'
				if len(location) > 3:
					location_title_html += location.title()
				else:
					location_title_html += location.upper()
				location_title_html += '</h3>'
				
				location_inv_html = ''
				all_options = generate_all_product_options(product, init_product) # {}, formerly generate_all_options(product, init_product)
				#print("options: " + str(all_options))
				arrival_time_string = 'NA' # when item will arrive, based on given transfer times and inv qty
				arrival_times = [] # collect arrival times and choose min
				arrival_time = 0 # weeks
				if len(all_options) > 0:
					location_inv_html = '<table>'
					for vrnt_idx in range(len(product)):
						vrnt = product[vrnt_idx]
						# convert option string to list of option name-value pairs
						# option_string = all_options[vrnt_idx]
						# #print("option_string: " + str(option_string))
						# option_list = option_string.split(',')
						# option_names = []
						# option_values = []
						# for option_item_idx in range(len(option_list)):
						# 	if option_item_idx % 2:
						# 		option_value = option_list[option_item_idx]
						# 		option_values.append(option_value)
						# 	else:
						# 		option_name = option_list[option_item_idx]
						# 		option_names.append(option_name)

						vrnt_sku = vrnt[sku_idx]
						option_names = all_options[vrnt_sku][0]
						option_values = all_options[vrnt_sku][1]


						#print("option_names: " + str(option_names))
						#print("option_values: " + str(option_values))
						#vrnt = product[vrnt_idx]
						#print("vrnt: " + str(vrnt))
						#vrnt_sku = vrnt[sku_idx]
						#print("vrnt_sku: " + str(vrnt_sku))

						limited_stock = 0
						
						# go through inv locations, and pull data if valid for internal transfer: ny, nj, la, sf. else need to buy from other locations separately
						for item_inv in all_inv:
							#print("item_inv: " + str(item_inv))
							item_sku = item_inv['sku']
							#print("item_sku: " + str(item_sku))
							if vrnt_sku == item_sku:
								# go through by header
								item_loc_inv = 0
								for inv_loc in locations:
									#print("inv_loc: " + inv_loc)
									loc_inv_header = determiner.determine_inv_location_key(inv_loc, item_inv)
									item_loc_inv = round(float(item_inv[loc_inv_header]))
									#print("item_loc_inv: " + str(item_loc_inv))

									if item_loc_inv > 0:
										# fix this logic by comparing transfer times and choosing min
										# if we know this inv loc has stock and we know it is the same as the location we are addressing, then the item is available immediately
										if location == inv_loc:
											arrival_time_string = 'Immediate'
											break
										# else if the inv loc is not the current location but we have inv, check if location is ny bc first treatment
										# if we know this inv loc has stock, check if it is a valid location for ny pickup
										# if we do not have stock at the current location, then check if we have stock at valid transfer location
										# for now, only consider ny, with above given valid locations
										# first check nj bc shorter transfer time
										if location == 'ny':
											#print("arrival_time: " + str(arrival_time))
											#print("arrival_times: " + str(arrival_times))
											if inv_loc == 'nj':
												arrival_time = nj_to_ny
												arrival_times.append(arrival_time)
											elif arrival_time_string == '' or arrival_time_string == 'NA': # nj is shortest transfer so if set already, but should have already broken loop if set so should always be blank at this point
												if inv_loc == 'la' or inv_loc == 'sf':
													arrival_time = ca_to_ny
													arrival_times.append(arrival_time)
											if len(arrival_times) > 0:
												arrival_time_string = str(min(arrival_times)) + ' weeks'

											# we want to show the limited stock qty associated with the min arrival time
											# if item_loc_inv < 10:
											# 	print("Limited Stock")
											# 	limited_stock = item_loc_inv

								# get limited stock from location with shortest arrival time
								limited_stock_enabled = False # enable if inventory capable for all locations and updates when order placed
								if limited_stock_enabled:
									item_location_inv = generate_vrnt_inv_qty(vrnt_sku,all_inv,location)
									if round(float(item_location_inv)) > 0 and round(float(item_location_inv)) < 10:
										limited_stock = item_location_inv
									else:
										item_nj_inv = generate_vrnt_inv_qty(vrnt_sku,all_inv,'nj')
										if round(float(item_nj_inv)) > 0 and round(float(item_nj_inv)) < 10:
											limited_stock = item_location_inv
										else:
											item_la_inv = generate_vrnt_inv_qty(vrnt_sku,all_inv,'la')
											item_sf_inv = generate_vrnt_inv_qty(vrnt_sku,all_inv,'sf')
											item_ca_inv = round(float(item_la_inv)) + round(float(item_sf_inv))
											if item_ca_inv > 0 and item_ca_inv < 10:
												limited_stock = item_location_inv


	

								# if we went through locations and did not find inv, see if eta
								if arrival_time_string.lower() == 'na':
									
									eta_header = determiner.determine_eta_header(item_inv)
									if eta_header != '':
										item_eta = item_inv[eta_header]
										#print("item_eta: " + str(item_eta))
										if item_eta.lower() != 'none':
											# if no stock and no eta, then it would have been removed earlier, but still check if one got through
											current_date = datetime.today()
											#print("current_date: " + str(current_date))
											eta_date = datetime.strptime(item_eta, '%Y-%m-%d') # "%d-%b-%Y" %d-%m-%Y'
											#print("eta_date: " + str(eta_date))
											eta_delta = eta_date - current_date
											eta_days = eta_delta.days
											#print("eta_days: " + str(eta_days))
											# if loc=la:
											transfer_weeks = ca_to_ny
											eta_weeks = round(float(eta_days) / 7.0, 1) + transfer_weeks
											#print("eta_weeks: " + str(eta_weeks))
											arrival_time_string = str(eta_weeks) + ' weeks'

								break
								

						location_inv_html += '<tr>'
						for option_value_idx in range(len(option_values)):
							option_value = option_values[option_value_idx]
							location_inv_html += '<td>' + option_value + '</td>'
						location_inv_html += '<td>' + arrival_time_string + '</td>'

						# if limited stock, then show stock
						if limited_stock != 0:
							limited_stock_html = '<td>' + str(limited_stock) + '</td>'
							location_inv_html += limited_stock_html

						location_inv_html += '</tr>'
					location_inv_html += '</table>'
				else:
					
					# go through inv locations, and pull data if valid: ny, nj, la, sf
					# for item_inv in all_inv:
					# 	print("item_inv: " + str(item_inv))
					location_inv_html += arrival_time_string

				
				location_html = location_title_html + location_inv_html

				all_locations_html += location_html

	arrival_html = updated_date_html + available_title_html + all_locations_html


	#print("arrival_html: " + str(arrival_html))	
	return arrival_html

# instead of saving description instances and relying on them to align with product variants, 
# make dictionary matching description to product handle
# and then when setting the description, use the product handle as the key
# preview table needed to display table within table in html
def generate_description(product, init_product, all_inv={}, vendor=''):
	print("\n===Generate Description===\n")

	descrip_instances = []

	body_html = ""

	html_descrip = True # user input based on spreadsheet tool. we want to use html bc we need to make a table format for data. 
	
	if html_descrip == True:

		notice_html = generate_product_notice_html(product) # important difference bt description and picture such as when only the bed is included in an image with the whole set

		# display 
		arrival_html = generate_arrival_html(product, init_product, all_inv, vendor)
		#arrival_html = generate_arrival_html(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)
				
		intro_html = generate_intro_html(product)

		colors_html = generate_colors_html(product, init_product)

		materials_html = generate_materials_html(product)

		finishes_html = generate_finishes_html(product)

		dimensions_html = generate_dimensions_html(product, init_product)

		features_html = generate_features_html(product, vendor)

		

		descrip_html = notice_html + arrival_html + intro_html + colors_html + materials_html + finishes_html + dimensions_html + features_html
		body_html = descrip_html

	

	return body_html

# products = { "<sku>": { "handle":"<handle>", "description":"<description>"  } }
# dict = { <handle>:<description> }
def generate_descrip_dict(all_details, init_all_details, all_inv={}, vendor=''):
	print("\n===Generate Description Dictionary===\n")
	# instead of saving description instances and relying on them to align with product variants, 
	# make dictionary matching description to product handle
	# and then when setting the description, use the product handle as the key
	descrip_dict = {}
	

	init_products = isolator.isolate_products(init_all_details)
	products = isolator.isolate_products(all_details) # why isolate products and not go line by line in all details?

	for product_idx in range(len(products)):
		product = products[product_idx]
		item_details = product[0]
		handle = generate_handle(item_details)
		#print("handle: " + handle)
		init_product = init_products[product_idx]
		descrip = generate_description(product, init_product, all_inv, vendor)

		descrip_dict[handle] = descrip

	#print("descrip_dict: " + str(descrip_dict))
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






def generate_intro(item_details):
	#print("\n===Generate Intro===\n")
	intro = ''

	# intro variables based on item details
	product_type = generate_product_type(item_details)
	#print("product_type: \'" + product_type + "\'")

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
		#print("Product type ends with s.")
		product_type_singular = product_type[:-1]


	intro1 = 'This exceptional ' + product_type_singular + ' will make ' + pronoun + ' ' + room_type + ' the most delightful room in your home'

	intro2 = str.capitalize(product_name) + ' is here to help with your design problem. Available in our highest quality materials, this distinguished ' + product_type_singular + ' is elegant, traditional, and crafted by hand, just the way you would expect our preeminent ' + product_type + ' to be'

	intro3 = 'Elegant ' + room_activity + ' is ' + product_name + '\'s speciality—so much so that you\'ll want to keep it forever. From all sides, you see a graceful shape that is perfectly balanced and sturdy, while being exceptionally refined'

	intro_templates = [intro1, intro2, intro3]

	intro = random.choice(intro_templates)

	#print(intro)

	return intro

#product = [] from catalog details
def generate_intro_html(product):
	#print("\n===Generate Intro HTML===\n")
	intro_html = ''

	opt_num = 1
	unique_intros = []
	for variant in product:

		intro = collection = ''

		if len(variant) > 3: # if variant contains intro data. todo: make it check for intro keyord instead of index.
			handle = generate_handle(variant) #variant[1].strip().lower()
			#print("Handle: " + handle)
			collection = variant[collection_idx].strip().lower()
			intro = variant[intro_idx].strip().lower()
			

			#print("Initial Intro: " + intro)
			# if no intro given then generate one
			# if only word given, assume error bc intro cannot be one word
			# for example some of Acme intros are '<span>' for unknown reason
			if intro == '' or intro == 'intro' or intro == 'n/a' or not re.search('\\s',intro):
				intro = generate_intro(variant)
			else:
				intro = reader.fix_typos(intro) # fix common typos
				#print("Intro fixed typos: " + intro)


		# check if intro blank
		if intro != '' and intro != 'n/a':
			# capitalize title of collection, before capitalizing sentences, in case collection starts sentence and has multiple names
			intro = re.sub(collection,collection.title(),intro)
			intro = writer.capitalize_sentences(intro)

			if intro not in unique_intros:
				unique_intros.append(intro)
			
				#vrnt_opts = variant
				#intro = re.sub('\"','\",CHAR(34),\"', intro) # if quotes found in intro, such as for dimensions, then fmla will incorrectly interpret that as closing string
				# intro_html += "<h3>Option " + str(opt_num) + "</h3><p>" + intro + "</p>"
				# opt_num += 1
				#break # once we make an intro for the product we dont need to loop thru any more variants because they all get the same intro
		#print("Intro HTML: " + intro_html)

	if len(unique_intros) == 1:
		intro_html = "<p>" + unique_intros[0] + "</p>"
	else:
		for unique_intro_idx in range(len(unique_intros)):
			unique_intro = unique_intros[unique_intro_idx]
			intro_html += "<h3>Option " + str(unique_intro_idx+1) + "</h3><p>" + unique_intro + "</p>"


	return intro_html

def generate_colors_html(product, init_product):

	#print("\n===Generate Colors HTML===\n")

	final_colors_html = "" # init fmla for this part of the description
	
	if determiner.determine_given_colors(product): # if we are NOT given colors we do not include colors in the description
		#print("Given Colors!")
		final_colors_html += "<table><tr><td>Colors: " # only if at least 1 of the variants has colors

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
				#handle = generate_handle(variant)
				#print("Handle: " + handle)
				colors = variant[color_idx].strip().lower()
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



def generate_materials_html(product):

	final_materials_html = "" # init fmla for this part of the description
	if determiner.determine_given_materials(product): # if we are NOT given materials we do not include materials in the description
		#print("\n===GIVEN MATERIALS===\n")
		if not determiner.determine_given_colors(product):
			final_materials_html = "<table>"

		final_materials_html += "<tr><td>Materials: </td>" # only if at least 1 of the variants has materials
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



def generate_finishes_html(product):

	#print("\n===Generate Finishes HTML===\n")

	final_finishes_html = "" # init fmla for this part of the description
	if determiner.determine_given_finishes(product): # if we are NOT given finishes we do not include finishes in the description
		#print("Given Finishes!")
		if not determiner.determine_given_colors(product) and not determiner.determine_given_materials(product):
			final_finishes_html = "<table>"
		final_finishes_html += "<tr><td>Finishes: </td>" # only if at least 1 of the variants has finishes

		# for now, only handle cases where all variants have same material
		variant1 = product[0]

		finishes = ''

		if len(variant1) > finish_idx:
			#handle = generate_handle(variant1) #variant1[1].strip().lower()
			finishes = variant1[finish_idx].strip().lower()

		finishes_html = '' # init option fmla so if no value given it is empty quotes
		if finishes != '' and finishes != 'n/a':
			finishes_html = "<td>" + finishes.title() + ". </td></tr>"

		final_finishes_html += finishes_html + "</table>"
	elif determiner.determine_given_colors(product) or determiner.determine_given_materials(product):
		# close the description data table
		final_finishes_html += "</table>"

	#print("final_finishes_html: " + final_finishes_html)

	return final_finishes_html





def generate_dimensions_html(product, init_product):
	print("\n===Generate Dimensions HTML===\n")

	dimensions_html = "" # init fmla for this part of the description
	if determiner.determine_given_dimensions(product): # if we are NOT given dimensions we do not include dimensions in the description
		dimensions_html += "<table><tr><td>Dimensions (in.): </td><td>" # only if at least 1 of the variants has dimensions

		#sizes = set_option_values(product, 'Size')
		opt_name = 'Size' # choose what option we want to show
		#opt_names = ['Size','Width','Depth','Height','Features'] # instead of this could only include unique dims but user wants to know dims for all options even if same
		standard_type = opt_name.lower() + "s" # standards are defined in the data/standards folder
		options = reader.read_standards(standard_type) # get dict of options
		size_options = options[opt_name]
		#print("Size Options: " + str(size_options))

		valid_opt = False

		# sort variants
		#print("Sort Init Variants")
		init_sorted_variants = sorter.sort_variants_by_size(init_product)
		#print("Sort Variants")
		sorted_variants = sorter.sort_variants_by_size(product)

		type = ''

		dim_html = ''

		for vrnt_idx in range(len(sorted_variants)):
			variant = sorted_variants[vrnt_idx]
			init_variant = init_sorted_variants[vrnt_idx]

			valid_opt = False

			type = generate_product_type(variant)

			width = depth = height = ''

			if len(variant) > width_idx:
				#handle = variant[1].strip().lower()
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

			#dim_html += ". </td></tr>"

			option_data = generate_options(variant, init_variant)
			print("Option Data: " + str(option_data))
			option_names = []
			option_values = []
			if len(option_data) > 0:
				option_names = option_data[0]
				option_values = option_data[1]

			# order option values from large to small, and correspond with dim_fmla

			# get the value of the size option, if there is one
			opt_idx = 0
			for current_opt_name in option_names:
				# some options like color are implied same size but even material could benefit from clarifying same size although could also be implied
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

					dimensions_html += ', '
			dimensions_html = dimensions_html.rstrip(', ')
			dimensions_html += ". </td></tr></table>" #dim_html += ". </td></tr>"

			#print()
		else:
			dimensions_html += dim_html + ". </td></tr></table>"

	#print("Dimensions HTML: " + dimensions_html + "\n")

	return dimensions_html

def generate_product_dims_html(product, init_product):
	print("\n===Generate Product Dimensions HTML===\n")
	dimensions_html = ''

	if determiner.determine_given_dimensions(product): # if we are NOT given dimensions we do not include dimensions in the description
		dimensions_html += '<h2>Dimensions (in.)</h2>'

		# new row for each option
		# if only 1 size then do not include options in size bc just 1
		# if more than 1 need to put size for all options/vrnts
		if determiner.determine_single_size(product):
			dimensions = generate_dimensions_string(product[0])
			dimensions_html += '<p>' + dimensions + '</p>'
		else:
			dimensions_html += '<table>'
			product_options = generate_product_options(product, init_product)
			dimensionless_opts = ['Color'] # determine dimensionless opts by seeing which opts do not affect dims. test when opt changes does dim change
			# make list of all vrnts dims
			product_dims = [] # [[]], 1 entry for each vrnt
			for vrnt_idx in range(len(product)):
				dimensions = generate_dimensions_string(product[vrnt_idx])
				product_dims.append([dimensions,product_options[vrnt_idx]]) # group by dimensions and need to keep options related to that dim

			# then group vrnts with same dims so only unique dims showing once
			vrnts_by_dim = isolator.isolate_vrnts_by_dim(product_dims) # [[[1,2],[1,2],[1,2],...],[[3,4],[3,4],[3,4],...],...]

			# exclude dimensionless dims to avoid confusing labels
			#dimensionful_opts = determiner.determine_dimensionful_opts(product)#[] # only display opts related to dim

			# display unique dims with correct vrnts
			# vrnts = [[1,2],[1,2],[1,2],...]
			for vrnts in vrnts_by_dim:
				# only need first vrnt dims in group bc grouped by same dim
				dimensions_idx = 0
				options_idx = 1
				dimensions = vrnts[0][dimensions_idx]
				sorted_options = vrnts[0][options_idx] # the common denominator options will be displayed once
				
				option_names = sorted_options[0] # needed to see if option related to dimension bc if not exlcude from table
				option_values = sorted_options[1]
				dimensions_html += '<tr>'
				for opt_idx in range(len(option_values)):
					option_name = option_names[opt_idx]
					option_value = option_values[opt_idx]
					# check if any vrnts have the same dims and see if they have diff dims but same opts to see the dim does not change proportional to that opt
					if option_name not in dimensionless_opts:
						dimensions_html += '<td>' + option_value + '</td>'
				dimensions_html += '<td>' + dimensions + '</td></tr>'

				

				
				
				# if only 1 opt val but different dims then error warning cannot include. in general 2 vrnts with the same option sets is invalid
				# at this point if it encounters invalid opts it will create the dims display but later be excluded by validation fcn
				# bc generate options allows duplicate opts. could make feature in generate product options where duplicate excluded from final
				# as long as that fits

	print("Dimensions HTML: " + dimensions_html + "\n")
	return dimensions_html

def generate_features(item_details):
	item_sku = item_details[sku_idx]
	print("\n===Generate Features for " + item_sku + "===\n") # means lack of features which could be error
	
	# bullet point indicates new line in features fmla so use bullet point for new line
	features = '• Perfectly balanced and sturdy. • Lightweight and easy to carry for convenience. • Durable construction, built to last. '

	#print("Features: " + features)
	return features



def generate_features_html(product, vendor=''):
	#print("\n===Generate Features HTML===\n")
	#features_html = "\"\""
	features_html = ""

	unique_features = []
	for variant in product:

		features = ''

		if len(variant) > 11:
			#handle = variant[1].strip().lower()
			#print("Handle: " + handle)
			features = variant[features_idx].strip()
			#print("Raw Features: " + features)
			# if no intro given then generate one
			if features == '' or str.lower(features) == 'features':
				features = generate_features(variant)

		if features != '' and features != 'n/a':
			# need better way to check if there are no proper nouns that should stay capitalized, b/c too blunt to lowercase everything
			features = features.lower().lstrip(',').strip()
			#print("Lowered and Stripped Features: " + features)


			if vendor == 'acme': # acme provides list of features separated by commas
				#print("Vendor: " + vendor)
				# add new line and bullet point after comma, with period at the end
				init_features_list = features.split(',')
				#print("split features: " + str(init_features_list))
				# remove excess space
				for i in range(len(init_features_list)):
					f = init_features_list[i]
					init_features_list[i] = f.strip()
				#print("stripped features: " + str(init_features_list))


				# remove extra spaces
				for i in range(len(init_features_list)):
					f = init_features_list[i]
					# capitalize first letter
					f = f.capitalize()
					#print("f cap: " + f)
					# add bullet to the beginning
					#f = '• ' + f
					init_features_list[i] = f.strip()

				#print("init_features_list: " + str(init_features_list))
				final_features_string = ''
				for feature_idx in range(len(init_features_list)):
					feature = init_features_list[feature_idx]
					final_features_string += '• ' + feature
					if feature_idx != len(init_features_list)-1:
						final_features_string += '. '

				features = final_features_string


			# add periods before bullets, if not already there
			# make sure no extra periods added so no double periods if sentence already has period at end
			features = re.sub(r"([^\.])\s•",r"\1. •", features) 
			if features[-1] != '.':
				#print("Last character: " + features[-1])
				features += '. '

			features = writer.capitalize_sentences(features).lstrip(',').strip() # if text inadvertently starts with comma, remove (eg , Bunkie board not required, support slats: 14+14, fixed ladder)

			#features = re.sub('\"','\",CHAR(34),\"', features) # if quotes found in features, such as for dimensions, then fmla will incorrectly interpret that as closing string
			
			
			if features not in unique_features:
				unique_features.append(features)

	if len(unique_features) == 1:
		features = unique_features[0]
		if re.search('•|    |ï|Ï',features): # or re.search('    ',features) or re.search('ï|Ï',features):
			features_list_html = "<ul class=\'product_features_list\'>"
			#print("\nFEATURES: " + features)

			features_list_html += re.sub(r'•([^\.]+)\.',r'<li>\1. </li>', features) # bullet point indicates new line
			features_list_html = re.sub(r'    ([^\.]+)\.',r'<li>\1. </li>', features_list_html) # 4 spaces indicates new line
			features_list_html = re.sub(r'ï|Ï([^\.]+)\.',r'<li>\1. </li>', features_list_html) # ï character indicates new line (for Coaster)
			
			features_list_html += "</ul>"

			features_html = features_list_html
		else:
			features_html = '<p class=\'product_features\'>' + features + '</p>'

			#break # for now, once we make features list for variant skip the rest of the variants for now bc it is more complex to organize all variant features in descrip
	else:
		for unique_features_idx in range(len(unique_features)):
			features = unique_features[unique_features_idx]
			if re.search('•|    |ï|Ï',features): # or re.search('    ',features) or re.search('ï|Ï',features):
				features_list_html = "<h3>Option " + str(unique_features_idx+1) + "</h3><ul class=\'product_features_list\'>"
				#print("\nFEATURES: " + features)

				features_list_html += re.sub(r'•([^\.]+)\.',r'<li>\1. </li>', features) # bullet point indicates new line
				features_list_html = re.sub(r'    ([^\.]+)\.',r'<li>\1. </li>', features_list_html) # 4 spaces indicates new line
				features_list_html = re.sub(r'ï|Ï([^\.]+)\.',r'<li>\1. </li>', features_list_html) # ï character indicates new line (for Coaster)
				
				features_list_html += "</ul>"

				features_html += features_list_html
			else:
				features_html += '<h3>Option ' + str(unique_features_idx+1) + '</h3><p class=\'product_features\'>' + features + '</p>'


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
		#print("sheet: " + str(sheet))
		# all_skus = []
		# all_collections = []
		# all_values = []
		for item_json in sheet:
			#print("item_json: " + str(item_json))
			# all_skus.append(item_json['sku'])
			# all_collections.append(item_json['collection'])
			for key in item_json:
				standard_key = determiner.determine_standard_key(key)
				formatted_input = reader.format_vendor_product_data(item_json[key], standard_key) # passing in a single value corresponding to key. also need key to determine format.
				if standard_key != '' and formatted_input != '':
					if key in all_fields_dict.keys():
						#print("add to existing key")
						all_fields_dict[standard_key].append(formatted_input)
					else:
						#print("add new key")
						all_fields_dict[standard_key] = [formatted_input]
		# all_fields_dict['sku'] = all_skus
		# all_fields_dict['collection'] = all_collections
		#print("all_fields_dict: " + str(all_fields_dict))
			
		list_of_fields.append(all_fields_dict)

	#print("list_of_fields: " + str(list_of_fields))
	return list_of_fields


def generate_catalog_from_json(all_items_json):
	print("\n===Auto Generate Catalog Given JSON===\n")
	#print("all_items_json: " + str(all_items_json))

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
		sheet1_sku = all_sheet1_skus[product_idx]
		# sheet1_collection = ''
		# if len(all_sheet1_collections) > 0:
		# 	sheet1_collection = all_sheet1_collections[product_idx]
		# #sheet1_cost = all_sheet1_prices[product_idx]
		# sheet_all_field_values = [sheet1_sku] # corresponding to desired field names
		#print("sheet1_all_field_values: " + str(sheet1_all_field_values))

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
				#print("current_sheet_" + key + ": " + str(current_sheet_value))
				if current_sheet_value != '' and current_sheet_value != 'n/a':
					product_catalog_dict[key] = current_sheet_value
		#print("product_catalog_dict after sheet1: " + str(product_catalog_dict))

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
		# img is not a crucial field if it is for vrnt in a product with an img

		if crucial_fields_given: 
			catalog_info = list(product_catalog_dict.values()) #[sheet1_sku] #, coll_name, product_type, intro, color, material, finish, length, width, height, weight, features, sheet1_cost, img_links, barcode]
			#print("catalog_info: " + str(catalog_info))


			#if image not given, but it is a vrnt in a product that does have an img, then it should be added to the catalog
			# this is a v2 so save a backup:
			# separate crucial fields into its 3 components, sku, cost, and image
			# bc img is only crucial if no other vrnts with img
			# but img becomes crucial before upload so avoid confusion in label

			catalog.append(catalog_info)
		else:
			print("Warning: Missing fields for SKU " + sheet1_sku + ", so product not uploaded!")


	return catalog

def generate_inv_from_data(vendor=''):
	print("\n===Generate Inventory from Data===\n")

	inventory = []

	# we do not know desired field names bc we do not if any inv locations, and if so how many?
	# look for inv keywords
	# we do not have crucial field names bc there may not be any inv info given

	# for unknown no. sheets with unknown contents
	# for user input, we have their list of files to loop thru

	inv_sheet = reader.read_raw_vendor_inv_data(vendor)

	print("\n === Display Inventory Info === \n")

	# for now only assume 1 sheet can contain all inventory
	#print("inv_sheet: " + str(inv_sheet))

	all_inv_sheet_values = {}
	for key in inv_sheet:
		all_inv_sheet_values[key] = inv_sheet[key]
	#print("all_sheet1_values init: " + str(all_inv_sheet_values))

	# see if all fields given by seeing if left blank or key exists?
	all_fields_given = True
	#print("inv_sheet.keys(): " + str(inv_sheet.keys()))
	

	all_inv_sheet_skus = all_inv_sheet_values['sku']
	for product_idx in range(len(all_inv_sheet_skus)):
		inv_sheet_all_field_values = {}
		for key in all_inv_sheet_values:
			#print("key in all_inv_sheet_values: " + str(key))
			inv_sheet_value = all_inv_sheet_values[key][product_idx]
			#print("inv_sheet_value: " + str(inv_sheet_value))
			inv_sheet_all_field_values[key] = inv_sheet_value
		inv_sheet_sku = all_inv_sheet_skus[product_idx]
		
		#print("inv_sheet_all_field_values: " + str(inv_sheet_all_field_values))

		# init blank and then we will check if spots blank to see if we should transfer data
		product_inv_dict = {}

		for key in inv_sheet:
			current_sheet_value = inv_sheet[key][product_idx]
			#print("current_sheet_" + key + ": " + str(current_sheet_value))
			if current_sheet_value != '' and current_sheet_value != 'n/a':
				product_inv_dict[key] = current_sheet_value
		#print("product_inv_dict after sheet1: " + str(product_inv_dict))

		if all_fields_given:
			for key in inv_sheet:
				sheet_field_value = inv_sheet_all_field_values[key]
				if sheet_field_value != '' and sheet_field_value != 'n/a':
					product_inv_dict[key] = sheet_field_value

		#print("product_inv_dict: " + str(product_inv_dict))
		inventory.append(product_inv_dict)



	#print("inventory: " + str(inventory))
	return inventory
	











# use keywords standard for products like prices, specs, and images, to find and read files
# then generate a catalog from the data
def generate_catalog_from_data(vendor='',all_inv={}):
	print("\n===Generate Catalog from Data===\n")

	catalog = []
	items_missing_img = [] # at the end, check if these items are vrnts where other vrnts have img so this should be included w/o img

	desired_field_names = ['sku', 'collection', 'type', 'intro', 'color', 'material', 'finish', 'width', 'depth', 'height', 'weight', 'features', 'cost', 'images', 'barcode'] #corresponding to keys in dict. determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	crucial_field_names = ['sku', 'cost', 'images'] # , cost, images]

	# for unknown no. sheets with unknown contents
	# for user input, we have their list of files to loop thru

	all_sheet_all_field_values = reader.read_raw_vendor_product_data(vendor)

	print("\n === Display Catalog Info === \n")

	# take first sheet and loop thru following sheets to see if matching sku entry
	sheet1 = all_sheet_all_field_values[0]
	#print("sheet1: " + str(sheet1))

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
		sheet1_sku = all_sheet1_skus[product_idx]

		# if item not stocked and not previously stocked, then continue to next item
		# if previously stocked but not currently stocked, set to delete
		prev_skus = all_sheet1_skus #[] temporary make equal to current skus until needed to make prev skus for efficiency
		if len(all_inv) > 0:
			if not determiner.determine_stocked(sheet1_sku, all_inv) and not sheet1_sku in prev_skus:
				continue

		# sheet1_collection = ''
		# if len(all_sheet1_collections) > 0:
		# 	sheet1_collection = all_sheet1_collections[product_idx]
		# #sheet1_cost = all_sheet1_prices[product_idx]
		# sheet_all_field_values = [sheet1_sku] # corresponding to desired field names
		#print("sheet1_all_field_values: " + str(sheet1_all_field_values))

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
				#print("current_sheet_" + key + ": " + str(current_sheet_value))
				if current_sheet_value != '' and current_sheet_value != 'n/a':
					product_catalog_dict[key] = current_sheet_value
		#print("product_catalog_dict after sheet1: " + str(product_catalog_dict))

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
					
					sheet1_sku = sheet1_all_field_values['sku'].lower()
					current_sheet_sku = all_current_sheet_skus[current_sheet_item_idx].lower()
					# problem where it duplicates skus ending with 'a'
					# if vendor == 'acme':
					# 	sheet1_sku = sheet1_sku.strip('a')
					# 	current_sheet_sku = current_sheet_sku.strip('a')

					#current_sheet_collection = all_current_sheet_collections[current_sheet_item_idx]
					
					if sheet1_sku == current_sheet_sku.strip('a'):
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
			#print(product_catalog_dict[crucial_field])
			#print("product_catalog_dict.keys(): " + str(product_catalog_dict.keys()))
			#if crucial_field not in product_catalog_dict.keys():
			if product_catalog_dict[crucial_field] == '' or product_catalog_dict[crucial_field] == 'n/a': # blank is ambiguous but na is clearly marked
				crucial_fields_given = False
				break

		# if sku and cost and image given, we can definitely pass the item to the catalog
		if crucial_fields_given: 
			#print("Crucial Fields Given for " + sheet1_sku)
			catalog_info = list(product_catalog_dict.values()) #[sheet1_sku] #, coll_name, product_type, intro, color, material, finish, length, width, height, weight, features, sheet1_cost, img_links, barcode]
			#print("catalog_info: " + str(catalog_info))
			catalog.append(catalog_info)
		else:
			print("Missing fields for SKU " + sheet1_sku + ", so check which fields are missing.")
			if product_catalog_dict['images'] == 'n/a' and product_catalog_dict['sku'] != 'n/a' and product_catalog_dict['cost'] != 'n/a':
				print("Missing Img but given SKU and Cost, so check if another variant has image.")
				# we do not have full catalog yet, so we cannot isolate products to see if other vrnts have img
				# so save to missing image list and check list after catalog compiled
				# also could include those missing image for now and then remove them 
				items_missing_img.append(product_catalog_dict)
			elif product_catalog_dict['sku'] == 'n/a':
				print("Warning: Missing SKU for item, so product not uploaded!")
			elif product_catalog_dict['cost'] == 'n/a':
				print("Warning: Missing cost for SKU " + sheet1_sku + ", so product not uploaded!")


	#products = isolator.isolate_products(catalog)
	# before returning catalog, add items with missing img but vrnt having img
	for item_missing_img in items_missing_img:
		missing_img_info = list(item_missing_img.values())
		missing_img_handle = generate_handle(missing_img_info)
		print("missing_img_handle: " + missing_img_handle)
		if re.search('loft-bed',missing_img_handle):
			print("Found loft bed variant with no image!")

			missing_img_sku = missing_img_info[sku_idx]
			print("missing_img_sku: " + missing_img_sku)
			# check if another item that passed into the catalog with an image has the same handle
			# if it has the same handle, then check if it is a loft bed, bc only loft beds can assume the image shows both items
			# else, it is more likely the variant does not have an image shown in the other vrnts image so we must flag and manually check
			for item in catalog:
				item_handle = generate_handle(item)
				if missing_img_handle == item_handle:
					
					catalog.append(missing_img_info)

					break # we can break whether or not loft bed bc we found another vrnt of same product (by handle)


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
			common_multiplier = 1.1 #1.8 
			online_only_rate = 1.1
			common_deliv_rate = 1.0 #1.2, delivery calculated by location after base price
		else:
			common_multiplier = 2.0

		if type == 'rugs':
			vrnt_price = cost_value * online_only_rate * common_multiplier + rug_deliv_price
			#print("vrnt_price = " + str(cost_value) + " * " + str(common_multiplier) + " + " + str(rug_deliv_price) + " = " + str(vrnt_price))
		elif type == 'mattresses' or type == 'box springs':
			vrnt_price = cost_value * online_only_rate * mattress_multiplier
		else:
			if seller == 'HFF':
				vrnt_price = cost_value * online_only_rate * ( common_deliv_rate + common_multiplier - 1 )
			else:
				vrnt_price = cost_value * online_only_rate * common_deliv_rate * common_multiplier
		#print("Variant Price Before Rounding: " + str(vrnt_price))

		if seller == 'HFF': # for hff we have lowest price available so no rounding
			vrnt_price = round(vrnt_price,2)
		else:
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

	# only set compare price ~1/3 of the time at random to show that sales are genuine and do not apply to all items only select few, which may increase purchases for perception of sale and time limit
	random_sale_item = random.randrange(1,3)
	if random_sale_item == 1:

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


# should all_details contain inv data, even though we do not know no. locations?
# ideally separate table
def generate_all_inv_qtys(all_inv_data):
	print("\n===Generate All Inventory Quantities===\n")
	# first use keywords to find qty in raw data
	# see if name abbreviation used in field
	# see number of locations for vendor
	# based on inv qty at location, and moving time bt locations, we can get pickup time
	inv_qtys = {}
	return inv_qtys

def generate_vrnt_inv_qty(sku, all_inv, location=''):
	print("\n===Generate Variant Inventory Quantity===\n")
	inv_qty = ''
	if location == '':
		location = 'ny'
	# compare sku
	for item_inv in all_inv:
		if item_inv['sku'] == sku:
			for key,value in item_inv.items():
				if re.search(location,key) and re.search('qty',key):
					inv_qty = value
					break
			break

	print("inv_qty in " + location + ": " + inv_qty)
	return inv_qty

def generate_product_notice_html(product):
	# if optional loft bed, make sure customer knows the loft bed is the item in they are looking at, or it is the optional element not included
	# if we see in intro, both loft bed and optional, together or separate, we can say the loft bed is an optional element
	# eg if the intro says queen optional, it may be referring to optional size which would be misleading
	# considering problem that only one of these items has an image, we must combine these two items
	# then at the img stage we are already ignoring the loft bc there is an image error but we cannot rely on that
	# we must check if that sku is the loft part of the pair, and if so add the variant queen+loft
	# then no need to print notice yet but there may be use for other notices
	notice_html = ''
	return  notice_html

# if it is a loft bed, we might be given optional underbed,
# so generate bundle loft+underbed
# product given in the past has been from the original catalog,
# but now it might be more efficient to pass the product at stage 2, after all products with no bundles are made
# solo product means it can be sold as is, but there may also be bundles of finished products
# solo_product = [ { 'handle':'<handle>', 'sku1':'<sku1>', 'price1':'<price1>' }, { 'handle':'<handle>', 'sku2':'<sku2>', 'price2':'<price2>' }, ... ] fields/keys are shopify product import fields var names
# also useful for sectionals
# should we pass all solo products here and eval if need bundles? yes, else there would be error if accidentally passed solo product with no bundle
# just bc we can handle the case, does not mean it is most efficient
# it should be equally efficient to determine if bundle within this fcn or before it so include within it for robustness
def generate_bundle_vrnts(solo_product):
	print("\n===Generate Bundle Variants===\n")
	bundle_vrnts = [] # default no bundle vrnts and only special cases get bundle vrnts. other products may create new products which are sets of solo products, but this fcn is for bundles within the same product. see generate_bundle_product

	# determine if loft bed bc treated differently
	# loft bed determined by handle bc type still bed, and handle same for all vrnts in fp
	product_handle = solo_product[0]['handle']
	if re.search('loft-bed', product_handle):
		# if twin and queen, add bundle of the 2
		# if colors or other options, no bundle
		bundle_vrnt = {}
		bundle_sku = ''
		for vrnt in solo_product:
			bundle_sku += vrnt['sku']
		bundle_vrnt['sku'] = bundle_sku
		print("bundle_vrnt: " + str(bundle_vrnt))

		# will need to add options to given vrnts in solo product
		# eg for loft bed the bundle option is loft+queen, so then for loft opt is loft only and for queen opt is queen only

	
	return bundle_vrnts

# new products which are bundles of solo products
# eg bedroom set
def generate_bundle_products(solo_products):
	print("\n===Generate Bundle Product===\n")
	bundle_products = []
	return bundle_products


# from all details we can generate solo products too but here we just want bundle vrnts
# we could pass the solo products here directly but then we need solo products to get bundle products?
# test both generate vrnts from all details and from solo products
def generate_all_bundle_vrnts(all_details):
	print("\n===Generate All Bundle Variants===\n")

	products = isolator.isolate_products(all_details)

# generate from sorted final item info for efficiency
# final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + vrnt_inv_tracker + ";" + vrnt_inv_qty + ";" + vrnt_inv_policy + ";" + vrnt_fulfill_service + ";" + vrnt_price + ";" + vrnt_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
def generate_all_bundle_vrnts_info(all_item_info, catalog):
	print("\n===Generate All Bundle Variants Info===\n")
	print("all_item_info: " + str(all_item_info))

	all_final_item_info = []

	# given field names or idx
	product_handle_idx = 0
	product_title_idx = 1
	body_html_idx = 2
	vendor_idx = 3
	product_category_idx = 4
	product_type_idx = 5
	product_tags_idx = 6
	published_idx = 7
	vrnt_opt1_name_idx = 8
	vrnt_opt1_val_idx = 9
	vrnt_opt2_name_idx = 10
	vrnt_opt2_val_idx = 11
	vrnt_opt3_name_idx = 12
	vrnt_opt3_val_idx = 13
	vrnt_sku_idx = 14
	vrnt_weight_idx = 15
	inv_tracker_idx = 16
	inv_qty_idx = 17
	inv_policy_idx = 18
	fulfill_idx = 19
	vrnt_price_idx = 20
	vrnt_compare_price_idx = 21
	req_ship_idx = 22
	taxable_idx = 23
	vrnt_barcode_idx = 24
	product_img_src_idx = 25
	img_position_idx = 26
	img_alt_idx = 27
	vrnt_img_idx = 28
	weight_unit_idx = 29
	tax_code_idx = 30
	vrnt_cost_idx = 31
	product_status_idx = 32

	# already given field names or idx globally but readd here for efficiency
	# order of detail fields
	sku_idx = 0
	collection_idx = 1 
	type_idx = 2
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

	# we must isolate products by splitting item info into lists and taking handle,
	# so then we must reassemble the item at the end of this fcn even if nothing changed and no bundle added
	all_solo_products = isolator.isolate_products_from_info(all_item_info)


	for solo_product in all_solo_products:
		product_handle = solo_product[0][product_handle_idx] # same for all vrnts so use first vrnt
		print("product_handle: " + product_handle)

		# same for all vrnts of product
		product_title = solo_product[0][product_title_idx]
		body_html = solo_product[0][body_html_idx]
		vendor = solo_product[0][vendor_idx]
		standard_product_type = solo_product[0][product_category_idx]
		product_type = solo_product[0][product_type_idx]
		product_tag_string = solo_product[0][product_tags_idx]
		published = solo_product[0][published_idx]
		inv_policy = solo_product[0][inv_policy_idx] #'deny'
		vrnt_fulfill_service = solo_product[0][fulfill_idx]
		vrnt_req_ship = solo_product[0][req_ship_idx]
		vrnt_taxable = solo_product[0][taxable_idx]
		vrnt_weight_unit = solo_product[0][weight_unit_idx]
		vrnt_tax_code = solo_product[0][tax_code_idx]
		product_status = solo_product[0][product_status_idx]

		# first check if multiple sizes or descrip? if it is in descrip then most likely and easy so check that first
		if determiner.determine_product_bundle(solo_product):

			

			# need way to organize images for bundles, but leave blank for now
			product_img_src = ''
			img_position = ''
			img_alt = '' 
			vrnt_img = ''
			barcode = '' # need custom barcodes for bundle products not specified for vendor


			# bundle product
			# get the options so that we can alter existing options as well as add options to new bundle vrnt
			# to assess bundle vrnt options we need to see if solo products color and other opts have multi vals
			#vrnt_options = []
			product_option_string = ';;;;;'
			if re.search('loft-bed', product_handle):
				product_option_string = 'Components;Loft Bed + Queen Bed;;;;'
			
			
			# set values accounting for multiple vrnts
			sku = ''
			item_weight_in_grams = 0.0
			item_price = 0.0
			item_cost = 0.0
			
			for vrnt_idx in range(len(solo_product)):
				vrnt = solo_product[vrnt_idx]
				#opt_names = []
				#opt_vals = []
				#vrnt_options = [opt_names, opt_vals] # do we need to see if multiple color options or can we leave that feature for later? most important to remove size options if only 1 for each item

				# how do we detect if the sizes are referring to the same component or different? raw type?
				# if raw type has loft bed then it is the loft component. likewise for queen bed component

				if vrnt_idx == 0:
					sku = vrnt[vrnt_sku_idx] 
				else:
					sku += " + " + vrnt[vrnt_sku_idx] 
				#bundle_vrnt['sku'] = bundle_sku
				#print("bundle_vrnt: " + str(bundle_vrnt))
				
				vrnt_weight_in_grams = vrnt[vrnt_weight_idx]
				item_weight_in_grams += float(vrnt_weight_in_grams)


				item_price += float(vrnt[vrnt_price_idx])
				item_cost += float(vrnt[vrnt_cost_idx])

			#item_price = round_bundle(item_price)
			item_price = round(item_price,2)
			item_cost = round(item_cost,2)
			item_compare_price = generate_vrnt_compare_price(item_price)

			inv_tracker = '' # leave blank unless inv track capable. get input from generate all products, based on inventory abilities. for now with payment plan we only get 1 location so shopify is good enough
			inv_qty = ''
			for vrnt_idx in range(len(solo_product)):
				vrnt = solo_product[vrnt_idx]
				# if both are available, then treat as available, else treat as unavailable
				# if no stock or eta, then tracker=shopify and qty=0
				# if we have stock in ny, tracker=shopify and qty=ny_qty
				if vrnt[inv_tracker_idx] == 'shopify':
					inv_tracker = vrnt[inv_tracker_idx]
					inv_qty = vrnt[inv_qty_idx]
					break

			final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + str(item_weight_in_grams) + ";" + inv_tracker + ";" + inv_qty + ";" + inv_policy + ";" + vrnt_fulfill_service + ";" + str(item_price) + ";" + item_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + str(item_cost) + ";" + product_status
			all_final_item_info.append(final_item_info)

			# will need to add options to given vrnts in solo product
			# eg for loft bed the bundle option is loft+queen, so then for loft opt is loft only and for queen opt is queen only
			# modify existing vrnt options, based on bundle component options
			# eg loft only, queen only
			for vrnt in solo_product:
				# get opt vals to determine how to change opt vals
				# may need to loop through opts before this loop to see if multiple vals to remove if only 1 val bc opt misleading
				vrnt_opt_vals = [vrnt[vrnt_opt1_val_idx],vrnt[vrnt_opt2_val_idx],vrnt[vrnt_opt3_val_idx]]
				if 'Twin' in vrnt_opt_vals:
					product_option_string = 'Components;Loft Bed;;;;' # take from catalog raw type or based on loft bed is always twin size
				elif 'Queen' in vrnt_opt_vals:
					product_option_string = 'Components;Queen Bed;;;;'

				sku = vrnt[vrnt_sku_idx]
				item_weight_in_grams = vrnt[vrnt_weight_idx]
				inv_tracker = vrnt[inv_tracker_idx]
				inv_qty = vrnt[inv_qty_idx]
				item_price = vrnt[vrnt_price_idx]
				item_compare_price = vrnt[vrnt_compare_price_idx]
				barcode = vrnt[vrnt_barcode_idx]
				product_img_src = vrnt[product_img_src_idx]
				img_position = vrnt[img_position_idx]
				img_alt = vrnt[img_alt_idx]
				vrnt_img = vrnt[vrnt_img_idx]
				item_cost = vrnt[vrnt_cost_idx]

				final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + inv_tracker + ";" + inv_qty + ";" + inv_policy + ";" + vrnt_fulfill_service + ";" + item_price + ";" + item_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
				all_final_item_info.append(final_item_info)

		else: # no bundle so transfer vrnts directly with no addition
			#print("No bundle for " + product_handle)
			for vrnt in solo_product:

				# if no change, reconstruct opt string from opt data
				product_option_string = vrnt[vrnt_opt1_name_idx] + ";" + vrnt[vrnt_opt1_val_idx] + ";" + vrnt[vrnt_opt2_name_idx] + ";" + vrnt[vrnt_opt2_val_idx] + ";" + vrnt[vrnt_opt3_name_idx] + ";" + vrnt[vrnt_opt3_val_idx]
				
				sku = vrnt[vrnt_sku_idx]
				item_weight_in_grams = vrnt[vrnt_weight_idx]
				inv_tracker = vrnt[inv_tracker_idx]
				inv_qty = vrnt[inv_qty_idx]
				item_price = vrnt[vrnt_price_idx]
				item_compare_price = vrnt[vrnt_compare_price_idx]
				barcode = vrnt[vrnt_barcode_idx]
				product_img_src = vrnt[product_img_src_idx]
				img_position = vrnt[img_position_idx]
				img_alt = vrnt[img_alt_idx]
				vrnt_img = vrnt[vrnt_img_idx]
				item_cost = vrnt[vrnt_cost_idx]
				

				final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + inv_tracker + ";" + inv_qty + ";" + inv_policy + ";" + vrnt_fulfill_service + ";" + item_price + ";" + item_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
				all_final_item_info.append(final_item_info)


	return all_final_item_info








# generate from sorted final item info for efficiency
# final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + vrnt_inv_tracker + ";" + vrnt_inv_qty + ";" + vrnt_inv_policy + ";" + vrnt_fulfill_service + ";" + vrnt_price + ";" + vrnt_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
def generate_all_bundle_vrnts_from_catalog(catalog, product_descrip_dict):
	print("\n===Generate All Bundle Variants from Catalog===\n")
	#print("catalog: " + str(catalog))

	all_bundle_vrnts_info = []

	# already given field names or idx globally but readd here for efficiency
	# order of detail fields
	sku_idx = 0
	collection_idx = 1 
	type_idx = 2
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
	

	# separate products by handle
	# group lists by handle element to get isolated products from final item info
	# for efficiency, we could assume items already sorted by handle at this point bc we are passed sorted final item info, but we could leave this in case the first sorting fcn fails
	solo_products = isolator.isolate_products(catalog)

	for solo_product in solo_products:
		product_handle = generate_handle(solo_product[0]) # same for all vrnts so use first vrnt
		# determine if loft bed bc treated differently
		# loft bed determined by handle bc type still bed, and handle same for all vrnts in fp
		if re.search('loft-bed', product_handle):
			print("Product is loft bed, so check if optional items to bundle.")
			opt_names = []
			# how do we know if there is an optional bundle in the loft bed product? description says optional queen bed, but what if that is referring to the size of the loft bed? can we assume loft bed is only twin? no bc that is restrictive.
			# in this case the descrip says optional bed underneath but not reliable. usually we can tell by img so descrip may need to be required here. 
			# in this case we know the queen is not loft bc loft is not in the raw type but in the raw description it says loft bed
			# could check if twin and queen, and then add bundle of the 2
			# most reliable to say if no loft in raw type then not loft but that requires adding parameter
			# although less reliable, for simplicity check descrip for optional bed underneath to confirm not referring to size of loft bed
			# if only colors or other options, no bundle

			# most reliable to draw from raw type bc we can bundle the two together whether or not referring to underbed
			# raw types are loft bed and queen bed
			# component option vals would be loft bed, queen bed, loft+queen

			# first check if multiple sizes or descrip? if it is in descrip then most likely and easy so check that first
			if determiner.determine_product_bundle(solo_product):

				product_title = generate_title(solo_product)
				body_html = product_descrip_dict[product_handle]

				vendor = ''
				
				bundle_vrnt = {}
				bundle_sku = ''
				for vrnt_idx in range(len(solo_product)):
					vrnt = solo_product[vrnt_idx]
					if vrnt_idx == 0:
						bundle_sku = vrnt[sku_idx] 
					else:
						bundle_sku += " + " + vrnt[sku_idx] 
				bundle_vrnt['sku'] = bundle_sku
				#print("bundle_vrnt: " + str(bundle_vrnt))

				# will need to add options to given vrnts in solo product
				# eg for loft bed the bundle option is loft+queen, so then for loft opt is loft only and for queen opt is queen only

				#final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + vrnt_inv_tracker + ";" + vrnt_inv_qty + ";" + vrnt_inv_policy + ";" + vrnt_fulfill_service + ";" + vrnt_price + ";" + vrnt_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
				#all_bundle_vrnts_info.append(final_item_info)

	return all_bundle_vrnts_info


# generate info not only for single variant but for all vrnts in product
# in some cases we need to compare all vrnts to tell info
# but for efficiency see if possible to tell all info from single vrnt
# we need all details to get dims
def generate_all_product_info(all_item_info, all_details):
	print("\n===Generate All Product Info===\n")

	all_final_item_info = []

	# given field names or idx
	product_handle_idx = 0
	product_title_idx = 1
	body_html_idx = 2
	vendor_idx = 3
	product_category_idx = 4
	product_type_idx = 5
	product_tags_idx = 6
	published_idx = 7
	vrnt_opt1_name_idx = 8
	vrnt_opt1_val_idx = 9
	vrnt_opt2_name_idx = 10
	vrnt_opt2_val_idx = 11
	vrnt_opt3_name_idx = 12
	vrnt_opt3_val_idx = 13
	vrnt_sku_idx = 14
	vrnt_weight_idx = 15
	inv_tracker_idx = 16
	inv_qty_idx = 17
	inv_policy_idx = 18
	fulfill_idx = 19
	vrnt_price_idx = 20
	vrnt_compare_price_idx = 21
	req_ship_idx = 22
	taxable_idx = 23
	vrnt_barcode_idx = 24
	product_img_src_idx = 25
	img_position_idx = 26
	img_alt_idx = 27
	vrnt_img_idx = 28
	weight_unit_idx = 29
	tax_code_idx = 30
	vrnt_cost_idx = 31
	product_status_idx = 32


	# we must isolate products by splitting item info into lists and taking handle,
	# so then we must reassemble the item at the end of this fcn even if nothing changed and no bundle added
	# all_solo_products = [[[1,2,3,...],[1,2,3,...],...],[[1,2,3,...],[1,2,3,...],...],...]
	all_solo_products = isolator.isolate_products_from_info(all_item_info)


	for solo_product in all_solo_products:
		product_handle = solo_product[0][product_handle_idx] # same for all vrnts so use first vrnt

		# same for all vrnts of product
		product_title = solo_product[0][product_title_idx]
		body_html = solo_product[0][body_html_idx]
		vendor = solo_product[0][vendor_idx]
		standard_product_type = solo_product[0][product_category_idx]
		product_type = solo_product[0][product_type_idx]
		product_tag_string = solo_product[0][product_tags_idx]
		published = solo_product[0][published_idx]
		inv_policy = solo_product[0][inv_policy_idx] #'deny'
		vrnt_fulfill_service = solo_product[0][fulfill_idx]
		vrnt_req_ship = solo_product[0][req_ship_idx]
		vrnt_taxable = solo_product[0][taxable_idx]
		vrnt_weight_unit = solo_product[0][weight_unit_idx]
		vrnt_tax_code = solo_product[0][tax_code_idx]
		product_status = solo_product[0][product_status_idx]

		# determine if product needs universal/global options, meaning options that depend on other vrnts
		# look for products with all options same but dimensions different like acme dresden collection
		# this is not a bundle but it is an instance where we need to compare all vrnts in product to get info such as large or small based on dims
		
		# init_product_opt_data = determiner.determine_duplicate_opts(solo_product) # [[[names],[values]]]
		# final_opt_data = [] # 
		# product_option_strings = []
		# if len(init_product_opt_data) > 0: # we know duplicate opts so create new opt data
		# 	weights =[]
		# 	widths = []
		# 	depths = []
		# 	heights = []
		# 	for vrnt in solo_product:
		# 		weights.append(vrnt[weight_idx])
		# 		widths.append(vrnt[width_idx])
		# 		depths.append(vrnt[depth_idx])
		# 		heights.append(vrnt[height_idx])
		# 	final_opt_data = generate_global_option_data(init_product_opt_data, weights, widths, depths, heights) # final opt data blank it means insufficient data bc duplicate opts and cannot differ so invalid so exlude from import
		# 	product_option_strings = generate_opt_strings_from_data(final_opt_data)

		
		final_opt_data = generate_global_option_data(solo_product, all_details) # evaluates if duplicate opts internally
		product_option_strings = generate_opt_strings_from_data(final_opt_data)

		for vrnt_idx in range(len(solo_product)):
			vrnt = solo_product[vrnt_idx]
			if len(product_option_strings) > 0:
				product_option_string = product_option_strings[vrnt_idx]
			else:
				# if no change, reconstruct opt string from opt data
				vrnt_opt1_name = vrnt[vrnt_opt1_name_idx]
				vrnt_opt1_val = vrnt[vrnt_opt1_val_idx]
				vrnt_opt2_name = vrnt[vrnt_opt2_name_idx]
				vrnt_opt2_val = vrnt[vrnt_opt2_val_idx]
				vrnt_opt3_name = vrnt[vrnt_opt3_name_idx]
				vrnt_opt3_val = vrnt[vrnt_opt3_val_idx]
				#vrnt_opt_names = [vrnt_opt1_name, vrnt_opt2_name, vrnt_opt3_name]
				product_option_string = vrnt_opt1_name + ";" + vrnt_opt1_val + ";" + vrnt_opt2_name + ";" + vrnt_opt2_val + ";" + vrnt_opt3_name + ";" + vrnt_opt3_val

			

			sku = vrnt[vrnt_sku_idx]
			item_weight_in_grams = vrnt[vrnt_weight_idx]
			inv_tracker = vrnt[inv_tracker_idx]
			inv_qty = vrnt[inv_qty_idx]
			item_price = vrnt[vrnt_price_idx]
			item_compare_price = vrnt[vrnt_compare_price_idx]
			barcode = vrnt[vrnt_barcode_idx]
			product_img_src = vrnt[product_img_src_idx]
			img_position = vrnt[img_position_idx]
			img_alt = vrnt[img_alt_idx]
			vrnt_img = vrnt[vrnt_img_idx]
			item_cost = vrnt[vrnt_cost_idx]

			final_item_info = product_handle + ";" + product_title + ";" + body_html + ";" + vendor.title() + ";" + standard_product_type + ";" + product_type + ";" + product_tag_string + ";" + published + ";" + product_option_string + ";" + sku + ";" + item_weight_in_grams + ";" + inv_tracker + ";" + inv_qty + ";" + inv_policy + ";" + vrnt_fulfill_service + ";" + item_price + ";" + item_compare_price + ";" + vrnt_req_ship + ";" + vrnt_taxable + ";" + barcode + ";" + product_img_src + ";" + img_position + ";" + img_alt + ";" + vrnt_img + ";" + vrnt_weight_unit + ";" + vrnt_tax_code + ";" + item_cost + ";" + product_status
			all_final_item_info.append(final_item_info)


	return all_final_item_info

# product = [[1,2,3,...],[1,2,3,...],...]
def generate_global_option_data(product, all_details):
	handle = product[0][handle_idx]
	print("\n===Generate Global Option Data for " + handle + "===\n")

	global_option_data = []

	vrnt_opt1_name_idx = 8
	vrnt_opt1_val_idx = 9
	vrnt_opt2_name_idx = 10
	vrnt_opt2_val_idx = 11
	vrnt_opt3_name_idx = 12
	vrnt_opt3_val_idx = 13
	vrnt_sku_idx = 14

	

	init_product_opt_data = determiner.determine_duplicate_opts(product) # [[[names],[values]]]
	if len(init_product_opt_data) > 0: # we know duplicate opts so create new opt data
		weights =[]
		widths = []
		depths = []
		heights = []
		for vrnt in product:
			sku = vrnt[vrnt_sku_idx]
			item_details = generate_item_details(all_details, sku)

			weights.append(item_details[weight_idx])
			widths.append(item_details[width_idx])
			depths.append(item_details[depth_idx])
			heights.append(item_details[height_idx])
		print("weights: " + str(weights))
		print("widths: " + str(widths))
		print("depths: " + str(depths))
		print("heights: " + str(heights))
	
	
		# or use differing dim in option val
		dims = [widths, depths, heights]
		differ_dim_idx = 0
		all_differ = True
		for dim_idx in range(len(dims)):
			dim = dims[dim_idx]
			# if all dim vals same, cant use to differ
			# if any 2 dim vals are same we cannot use to differ
			
			for val in dim:
				if dim.count(val) > 1: # if the multiple that are the same also have the same options
					all_differ = False
					break

			# if it did not find 2 same in dim then use this dim to differ
			if all_differ:
				differ_dim_idx = dim_idx
				break

		# if all dims same, see if all weights differ
		# if weight is greatest add opt size large
		# get idx of max element in weights

		# if no differing factors, then mark for exclusion and warn user
		# by returning empty list could imply no differing factors
		if all_differ:
			for vrnt_idx in range(len(init_product_opt_data)):
				vrnt_opt_data = init_product_opt_data[vrnt_idx]
				print("init vrnt_opt_data: " + str(vrnt_opt_data)) # [[names],[vals]]
				differ_dim = dims[differ_dim_idx]
				dim_types = ['width','depth','height']
				differ_dim_type = dim_types[differ_dim_idx]
				final_vrnt_opt_data = []
				opt_names = vrnt_opt_data[0]
				opt_vals = vrnt_opt_data[1]
				for opt_idx in range(len(opt_names)):
					# opt_name = opt_names[opt_idx]
					# opt_val = opt_vals[opt_idx]
					if opt_names[opt_idx] == '':
						opt_names[opt_idx] = differ_dim_type.title()
						opt_vals[opt_idx] = differ_dim[vrnt_idx]
						break


				# if global_option:
				# 	# generate global option, such as size based on weights
				# 	vrnt_weight = vrnt[vrnt_weight_idx]
				# 	print("vrnt_weight: " + vrnt_weight)

				# 	# determine if available option
				# 	# if already 3 options determine how to handle
				# 	# if more than 3 options add descriptor to title
				# 	for opt in vrnt_opt_names:
				# 		if opt == '':
				# 			# we can use this space for the new opt
				# 			new_opt = ''
				# 			idx = option_strings.index(duplicate_opts)

				print("final vrnt_opt_data: " + str(vrnt_opt_data)) # [[names],[vals]]
				global_option_data.append(vrnt_opt_data)


		if len(global_option_data) == 0:
			print("Warning: invalid options for " + handle)

	return global_option_data

def generate_opt_strings_from_data(product_opt_data):
	opt_strings = []

	for vrnt_opt_data in product_opt_data:
		opt_names = vrnt_opt_data[0]
		opt_vals = vrnt_opt_data[1]
		opt_string = ''
		for opt_idx in range(len(opt_names)):
			if opt_idx == 0:
				opt_string += opt_names[opt_idx] + ";" + opt_vals[opt_idx]
			else:
				opt_string += ";" + opt_names[opt_idx] + ";" + opt_vals[opt_idx]

		opt_strings.append(opt_string)


	return opt_strings

def generate_item_details(all_details, sku):
	print("\n===Generate Item Details for " + sku + "===\n")
	item_details = []
	for item in all_details:
		print("item: " + str(item))
		item_sku = item[sku_idx]
		if item_sku == sku:
			item_details = item
			break

	print("item_details: " + str(item_details))
	return item_details


# helper functions
def roundup(x):
	 return int(math.ceil(x / 100.0)) * 100

def rounddown(x):
	 return int(math.floor(x / 100.0)) * 100

def round_price(price):
	rounded_price = roundup(price)
	rounded_price = float(rounded_price)

	return rounded_price - 0.01

def round_bundle(price):
	rounded_price = rounddown(price)
	rounded_price = float(rounded_price)

	return rounded_price - 0.01
