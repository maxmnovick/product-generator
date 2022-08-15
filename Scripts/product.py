# product.py
# functions for a product,
# such as change description, or add tags

import re, string, math, collection

def set_type(current_collection, all_types, item_idx, vndr):
	# get the given name of the current item
	name = collection.determine_item_name(current_collection, item_idx, vndr)
	print("Given Name: " + name)

	product_type = ""
	type_set = False

	# we are not creating bundles that do not have single skus because inventory system cannot handle such bundles
	set_keyword = "set"
	if re.search(set_keyword, name):
		product_type = "set"

	if product_type != "set":

		# for a given item, check which product type it matches
		for current_type in all_types:

			type_keywords = read_keywords(current_type)

			# first look at item name to determine type. only look at category type for collection if the name is insufficient to decide product type
			for key_idx in range(len(type_keywords)):
				if re.search(type_keywords[key_idx], name):
					# account for mirror supports for dresser, b/c may find dresser keyword but not dressers type
					if current_type == "dressers":
						if re.search("mirror support", name):
							product_type = "mirrors supports"
						else:
							product_type = current_type
					else:
						product_type = current_type
					type_set = True
					break;

			if type_set:
				break

		# if we can't decide product type from item name, use category type of the collection
		if not type_set:
			room_set_row_idx = 0
			room_set_row = current_collection[room_set_row_idx].split("\t")

			category_type_idx = 11
			category_type = room_set_row[category_type_idx]
			print("Category Type: " + category_type)

			if category_type == "BEDROOMS":
				product_type = "bedroom sets"

				# there are bedroom collections that do not include bed, so do not have size variants
				bedroom_key1 = "wardrobe"
				bedroom_key2 = "w/d"
				bedroom_key3 = "dresser/chest"
				bedroom_key4 = "night\s*stand"
				bedroom_key5 = "n/s"
				bedroom_keywords = [ bedroom_key1, bedroom_key2, bedroom_key3, bedroom_key4, bedroom_key5]
				bedroom_types = [ "wardrobes", "wardrobes", "dresser-chest sets", "nightstand sets", "nightstand sets"]

				for key_idx in range(len(bedroom_keywords)):
					if re.search(bedroom_keywords[key_idx], name):
						product_type = bedroom_types[key_idx]
						break;

			elif category_type == "DINING":
				product_type = "dining sets"
			elif category_type == "LIVING":
				product_type = "living room sets"
			elif category_type == "WALL UNITS":
				product_type = "wall units"
			elif category_type == "CLEARANCE":
				clearance_keywords = ["sectional", "chair", "leather set"]
				clearance_types = ["sectionals", "chairs", "living room sets"]

				for key_idx in range(len(clearance_keywords)):
					if re.search(clearance_keywords[key_idx], name):
						product_type = clearance_types[key_idx]
						break;

			elif category_type == "OTHER":
				other_keywords = [ "wooden slats frame", "platform", "mattress"]
				other_types = ["bed frames", "bed platforms", "mattresses"]

				for key_idx in range(len(other_keywords)):
					if re.search(other_keywords[key_idx], name):
						product_type = other_types[key_idx]
						break;
			else:
				print("Unrecognized Category Type while setting Product Type!")

	print("Type: " + product_type + "\n")

	return product_type

# set handle for a room set using a collection isolated in a vendor catalog
def set_handle(current_collection, item_idx, product_type):
	# Handle is derived from Name in the first row of the collection (x,y)=(1,0)

	# must make sure the collection contains the first row since the first row does not contain a parent sku, which was used to isolate collections
	room_set_row_idx = 0
	room_set_row = current_collection[room_set_row_idx].split("\t")
	#print("Room Set Row: " + str(room_set_row))
	name_field_idx = 0 # if csv, idx=1. if tsv, idx=0
	room_set_name = room_set_row[name_field_idx] # now we have the name of the room set
	#print("Room Set Name: " + room_set_name)

	# see if the collection name is already the first word in the item name
	collection_name = room_set_name.split(" ")[0].lower() # the first word in the bundle name is the collection name
	item_name = collection.determine_item_name(current_collection, item_idx)
	if not re.search(collection_name, item_name):
		item_name = collection_name + " " + item_name

	item_name = replace_option_codes(item_name, product_type)
	item_name = fix_typos(item_name)

	handle = item_name.replace(" ","-").replace("w/", "").replace(",", "").replace("--","-")
	print("Handle: " + handle + "\n")

	return handle

# set title based on name of room set
def set_title(current_collection, item_idx, product_type):
	room_set_row_idx = 0
	room_set_row = current_collection[room_set_row_idx].split("\t")

	name_field_idx = 0 # if csv, idx=1. if tsv, idx=0
	room_set_name = room_set_row[name_field_idx] # now we have the name of the room set

	# see if the collection name is already the first word in the item name
	collection_name = room_set_name.split(" ")[0].lower() # the first word in the bundle name is the collection name
	item_name = collection.determine_item_name(current_collection, item_idx)
	if not re.search(collection_name, item_name):
		item_name = collection_name + " " + item_name

	item_name = replace_option_codes(item_name, product_type)
	item_name = fix_typos(item_name)

	title = string.capwords(item_name) # now we have the name of the room set
	print("Title: " + title + "\n")

	return title

# set description based on name of room set
def set_description(current_collection):
	room_set_row_idx = 0
	room_set_row = current_collection[room_set_row_idx].split("\t")

	descrip_field_idx = 1 # if csv, idx=1. if tsv, idx=0
	description = re.sub('\"', '\'', room_set_row[descrip_field_idx])# replace commas with semicolons to avoid separating fields by commas
	description = re.sub(',', ';', description)

	print("Body HTML: " + description + "\n")

	return description

def set_tags(vndr):
	tags = vndr + "2020"

	print("Tags: " + tags + "\n")

	return tags

def set_img_src(current_collection):
	# Image Src is derived from the columns Image 1-14

	room_set_row_idx = 0
	room_set_row = current_collection[room_set_row_idx].split("\t")
	img_1_idx = 17

	img_src = room_set_row[img_1_idx]

	print("Image Src: " + img_src + "\n")

	return img_src

def set_sku(vrnt_itms):
	# Variant SKU is derived from Parent SKU and sub-SKUs

	# first iteration uses only parent sku for simplicity
	#room_set_row_idx = 0
	#room_set_row = vrnt_itms[room_set_row_idx] # no split by tab separator b/c variant_items is array of arrays
	#parent_sku_idx = 109 # 1 less than parent sku when taken from sub-items b/c parent_sku=sku for room set product
	#sku_idx = parent_sku_idx - 1

	#parent_sku = room_set_row[sku_idx]

	sku_idx = 109
	single_item = vrnt_itms[0] # not handling bundles yet
	variant_sku = single_item[sku_idx]#set_variant_sku(vrnt_itms)

	#sku = parent_sku + "-" + variant_sku

	print("SKU: " + variant_sku + "\n")

	return variant_sku

def set_variant_sku(items):
	vrnt_sku = ''
	sku_idx = 109 # b/c rows not shifted like parent row in set_sku()

	prev_item_sku = ''
	multiplier = 2
	for item in items[1:]:
		item_sku = item[sku_idx]
		#print("Item " + str(item_idx) + " SKU: " + item_sku)
		if item_sku != prev_item_sku:
			vrnt_sku += item[sku_idx] + "+"
		else:
			print("check if already a multiplier: " + vrnt_sku[-2])
			if vrnt_sku[-2] != '*': # not a multiplier, so normal addition sku format
				vrnt_sku = vrnt_sku[:-1] # remove hanging plus sign
				multiplier = 2
			else:
				vrnt_sku = vrnt_sku[:-3] # remove hanging multiplier
			vrnt_sku += "*" + str(multiplier) + "+"
			multiplier += 1

		prev_item_sku = item_sku

	vrnt_sku = vrnt_sku[:-1] # replace extra plus sign at the beginning and end of the sku

	#print("Variant SKU: " + vrnt_sku)

	return vrnt_sku

def get_sku(item):
	sku_idx = 109
	print("Get SKU of item: " + str(item))
	sku = ''
	if len(item) > 0:
		sku = item[sku_idx]
	return sku

def set_price(vrnt_itms):
	# Variant Price is derived from Parent SKU and sub-SKUs
	vrnt_price = vrnt_cost = 0 # init

	price_idx = 3 # if csv, idx=3. if tsv, idx=2

	# first iteration uses only room set price for simplicity
	#room_set_row_idx = 0
	#room_set_row = vrnt_itms[room_set_row_idx]

	bundle = False
	if bundle:
		for item in vrnt_itms[1:]:
			item_cost = item[price_idx]
			print("Item Cost: " + item_cost)
			vrnt_cost += int(item_cost)
	else:
		for item in vrnt_itms:
			item_cost = item[price_idx]
			print("Item Cost: " + item_cost)
			vrnt_cost += int(item_cost)

	#cost = room_set_row[price_idx]
	print("Cost: " + str(vrnt_cost))

	if vrnt_cost > 0:
		landed_cost = float(vrnt_cost) * 1.15
		vrnt_price = roundup(landed_cost * 2.4)-0.01
		print("Price: " + str(vrnt_price) + "\n")
	else:
		print("Invalid Cost")

	return str(vrnt_price)

def set_compare_at_price(price):
	compare_price = roundup(float(price) * 1.20)-0.01

	return str(compare_price)

def set_cost(vrnt_itms):
	# Variant Price is derived from Parent SKU and sub-SKUs
	vrnt_cost = 0 # init

	price_idx = 3 # if csv, idx=3. if tsv, idx=2

	bundle = False
	if bundle:
		for item in vrnt_itms[1:]:
			item_cost = item[price_idx]
			print("Item Cost: " + item_cost)
			vrnt_cost += int(item_cost)
	else:
		for item in vrnt_itms:
			item_cost = item[price_idx]
			print("Item Cost: " + item_cost)
			vrnt_cost += int(item_cost)

	#cost = room_set_row[price_idx]
	print("Cost: " + str(vrnt_cost))

	if vrnt_cost == 0:
		print("Invalid Cost")

	return str(vrnt_cost)

def set_weight(vrnt_itms):
	vrnt_weight = 0 # init
	weight_idx = 9

	bundle = False
	if bundle:
		for item in vrnt_itms[1:]:
			item_weight = item[weight_idx]
			if item_weight == '':
				print("Warning: Invalid Item Weight!")
			else:
				print("Item Weight: " + item_weight)
				vrnt_weight += float(item_weight)
	else:
		for item in vrnt_itms:
			item_weight = item[weight_idx]

			if item_weight == '':
				print("Warning: Invalid Item Weight!")
			else:
				print("Item Weight: " + item_weight)
				vrnt_weight += float(item_weight)

	#cost = room_set_row[price_idx]
	print("Weight: " + str(vrnt_weight))

	if vrnt_weight == 0:
		print("Invalid Weight")

	return str(vrnt_weight)

def set_option_name(type, vrnt_num, vrnt_opts):
	vrnt_opt_names = []
	if len(vrnt_opts) != 0:
		vrnt_opt_names = vrnt_opts[0]
	else:
		print("No variant options while setting option name\n")
	name = ''
	if len(vrnt_opt_names) != 0:
		vrnt_idx = vrnt_num - 1
		name = vrnt_opt_names[vrnt_idx]

	# if type == 'bedroom sets':
# 		print("\n=== Set Options for  Bedroom Set ===\n")
#
# 		if len(vrnt_opt_names) != 0:
# 			for opt_name in vrnt_opt_names:
# 				if re.search(opt_name, "size"):
# 					name = "Size"
# 					break
# 		print("\n=== Set Options for Bedroom Set ===\n")
# 	elif type == "nightstand sets":
# 		print("\n=== Set Options for  Nightstand Set ===\n")
#
# 		if len(vrnt_opt_names) != 0:
# 			name = vrnt_opt_names[vrnt_num]
#
# 	elif type == "dining sets":
# 		print("\n=== Set Options for Dining Room Set ===\n")
# 	elif type == "living room sets":
# 		print("\n=== Set Options for Living Room Set ===\n")
# 		name = "Room Configuration"
# 		print("\n=== Set Options for Living Room Set ===\n")
# 	elif type == "wall units":
# 		print("\n=== Set Options for Wall Unit ===\n")
# 	elif type == "sectionals":
# 		print("\n=== Set Options for Sectional ===\n")
# 	elif type == "chairs":
# 		print("\n=== Set Options for Chair ===\n")

	print("Option Name: " + name)

	return string.capwords(name)

def set_option_value(type, vrnt_num, vrnt_opts):
	vrnt_opt_values = []
	if len(vrnt_opts) != 0:
		vrnt_opt_values = vrnt_opts[1]
	else:
		print("No variant options while setting option value\n")

	value = ''

	# at this point we already have the option names and values sorted by isolate_variant_options function
	if len(vrnt_opt_values) != 0:
		vrnt_idx = vrnt_num - 1
		value = vrnt_opt_values[vrnt_idx]

# 	if type == 'bedroom sets':
# 		print("\n=== Set Options for Bedroom Set ===\n")
# 		if vrnt_num == 1:
# 			value = "King"
# 		elif vrnt_num == 2:
# 			value = "Queen"
# 	elif type == 'nightstand sets':
# 		print("\n=== Set Options for Nightstand Set ===\n")
# 		if vrnt_num == 1:
# 			value = "2 Drawer"
# 		elif vrnt_num == 2:
# 			value = "3 Drawer"
# 	elif type == "dining sets":
# 		print("\n=== Set Options for Dining Room Set ===\n")
# 	elif type == "living room sets":
# 		print("\n=== Set Options for Living Room Set ===\n")
# 		value = "Sectional + Chair + Ottoman"
# 	elif type == "wall units":
# 		print("\n=== Set Options for Wall Unit ===\n")
# 	elif type == "sectionals":
# 		print("\n=== Set Options for Sectional ===\n")
# 	elif type == "chairs":
# 		print("\n=== Set Options for Chair ===\n")

	print("Option Value: " + value + "\n")

	return string.capwords(value)

# ====== Helper Functions =====
def roundup(x):
	return int(math.ceil(x / 100.0)) * 100

def read_types():
	print("=== Read Types ===\n")

	types_filename = "../Data/product-types.csv"

	types = []
	lines = []

	with open(types_filename, encoding="UTF8") as types_file:

		current_line = ""
		for types_info in types_file:
			current_line = types_info.strip()
			lines.append(current_line)

		types_file.close()

	# line_num = 1
	# for line in lines:
	# 	print("Line " + str(line_num) + ": " + line + "\n")
	#
	# 	line_num += 1

	for line in lines:
		types_in_line = line.split(",")
		for type in types_in_line:
			types.append(type)

	print("Types: " + str(types))

	print("=== Read Types ===\n")

	return types

def read_keywords(product_type, file_type):
	#print("=== Read Keywords ===\n")

	if file_type == "csv":
		keys_filename = "../Data/keywords/" + product_type + "-keywords.csv"

		keys = []
		lines = []

		try:
			with open(keys_filename, encoding="UTF8") as keys_file:

				current_line = ""
				for key_info in keys_file:
					current_line = key_info.strip()
					lines.append(current_line)

				keys_file.close()
		except:
			print("No keywords for products of type " + product_type)

		for line in lines:
			keys_in_line = line.split(",")
			for key in keys_in_line:
				keys.append(key)
	elif file_type == "json":
		keys_filename = "../Data/keywords.json"

		keys = []
		lines = []

		try:
			with open(keys_filename, encoding="UTF8") as keys_file:

				current_line = ""
				for key_info in keys_file:
					current_line = key_info.strip()
					lines.append(current_line)

				keys_file.close()
		except:
			print("Warning: No keywords file!")

		# combine into 1 line
		condensed_json = ''
		for line in lines:
			condensed_json += line

		# parse condensed_json
		parsed_json = json.loads(condensed_json)

		# the result is a python dictionary from which we can extract keywords for a given product type
		keys = parsed_json[type]

	print("Keywords for " + product_type + ": " + str(keys))

	#print("=== Read Keywords ===\n")

	return keys

def replace_option_codes(item_name, product_type):
	codes = []
	try:
		codes = read_option_codes(product_type)
	except:
		print("No option codes for products of type " + product_type)

	for code in codes:
		item_name = re.sub(code,'',item_name)
		item_name = re.sub('\s+',' ',item_name) # replace multiple consecutive spaces with a single space

	return item_name.strip()

def read_option_codes(product_type):
	print("=== Read Option Codes ===\n")

	codes_filename = "../Data/option-codes/" + product_type + "-option-codes.csv"

	codes = []
	lines = []

	with open(codes_filename, encoding="UTF8") as codes_file:

		current_line = ""
		for code_info in codes_file:
			current_line = code_info.strip()
			lines.append(current_line)

		codes_file.close()

	for line in lines:
		codes_in_line = line.split(",")
		for code in codes_in_line:
			codes.append(code)

	print("Option Codes: " + str(codes))

	print("=== Read Option Codes ===\n")

	return codes

def fix_typos(item_name):
	errors = ["rrr", "Emprio"]
	fixes = ["rr", "Emporio"]

	fixed_name = item_name

	# important to search to check for error before substituting
	for i in range(len(errors)):
		if re.search(errors[i],item_name):
			#print('error: ' + errors[i])
			fixed_name = re.sub(errors[i], fixes[i],item_name)

			print("Fixed Name: " + fixed_name)

	return fixed_name

def check_uppercase_code(catalog_line):
	code = catalog_line.split(",")[0]
	stripped_code = re.sub('[\W_]+', '', code)

	return stripped_code.isupper()
