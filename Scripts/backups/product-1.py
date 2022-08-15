# product.py
# functions for a product,
# such as change description, or add tags

import re, string, math

def check_uppercase_code(catalog_line):
	code = catalog_line.split(",")[0]
	stripped_code = re.sub('[\W_]+', '', code)

	return stripped_code.isupper()

# set handle for a room set using a collection isolated in a vendor catalog
def set_handle(collection):
	# Handle is derived from Name in the first row of the collection (x,y)=(1,0)

	# must make sure the collection contains the first row since the first row does not contain a parent sku, which was used to isolate collections
	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")
	#print("Room Set Row: " + str(room_set_row))
	name_field_idx = 0 # if csv, idx=1. if tsv, idx=0
	room_set_name = room_set_row[name_field_idx] # now we have the name of the room set
	#print("Room Set Name: " + room_set_name)

	handle = room_set_name.lower().replace(" ","-")
	print("Handle: " + handle)

	return handle

# set title based on name of room set
def set_title(collection):
	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")

	name_field_idx = 0 # if csv, idx=1. if tsv, idx=0
	title = string.capwords(room_set_row[name_field_idx]) # now we have the name of the room set

	print("Title: " + title)

	return title

# set description based on name of room set
def set_description(collection):
	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")

	descrip_field_idx = 1 # if csv, idx=1. if tsv, idx=0
	description = room_set_row[descrip_field_idx]

	print("Description: " + description)

	return description

def set_type(collection):
	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")

	category_type_idx = 11
	category_type = room_set_row[category_type_idx]
	print("Category Type: " + category_type)

	if category_type == "BEDROOMS":
		product_type = "bedroom sets"
	elif category_type == "DINING":
		product_type = "dining sets"
	elif category_type == "LIVING":
		product_type = "living room sets"
	elif category_type == "WALL UNITS":
		product_type = "wall units"
	elif category_type == "CLEARANCE":
		product_type = "Determine appropriate product type based on given vendor info."
	elif category_type == "OTHER":
		product_type = "Determine appropriate product type based on given vendor info."

	print("Type: " + product_type)

	return product_type

def set_tags(vndr):
	tags = vndr + "2020"

	print("Tags: " + tags)

	return tags

def set_img_src(collection):
	# Image Src is derived from the columns Image 1-14

	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")
	img_1_idx = 17

	img_src = room_set_row[img_1_idx]

	print("Image Src: " + img_src)

	return img_src

def set_sku(vrnt_itms):
	# Variant SKU is derived from Parent SKU and sub-SKUs

	# first iteration uses only parent sku for simplicity
	room_set_row_idx = 0
	room_set_row = vrnt_itms[room_set_row_idx] # no split by tab separator b/c variant_items is array of arrays
	parent_sku_idx = 109 # 1 less than parent sku when taken from sub-items b/c parent_sku=sku for room set product
	sku_idx = parent_sku_idx - 1

	parent_sku = room_set_row[sku_idx]
	variant_sku = set_variant_sku(vrnt_itms)

	sku = parent_sku + "-" + variant_sku

	print("SKU: " + sku)

	return sku

def set_variant_sku(items):
	vrnt_sku = ''
	sku_idx = 109 # b/c rows not shifted like parent row in set_sku()

	for item in items[1:]:
		item_sku = item[sku_idx]
		#print("Item " + str(item_idx) + " SKU: " + item_sku)
		vrnt_sku += item[sku_idx] + "+"

	vrnt_sku = vrnt_sku[:-1] # replace extra plus sign at the beginning and end of the sku

	#print("Variant SKU: " + vrnt_sku)

	return vrnt_sku

def set_price(vrnt_itms):
	# Variant Price is derived from Parent SKU and sub-SKUs
	vrnt_price = vrnt_cost = 0 # init

	price_idx = 3 # if csv, idx=3. if tsv, idx=2

	# first iteration uses only room set price for simplicity
	#room_set_row_idx = 0
	#room_set_row = vrnt_itms[room_set_row_idx]

	for item in vrnt_itms[1:]:
		item_cost = item[price_idx]
		print("Item Cost: " + item_cost)
		vrnt_cost += int(item_cost)

	#cost = room_set_row[price_idx]
	print("Cost: " + str(vrnt_cost))

	landed_cost = float(vrnt_cost) * 1.15
	vrnt_price = roundup(landed_cost * 2.4)-0.01
	print("Price: " + str(vrnt_price))

	return str(vrnt_price)

def set_option_name(type):
	name = ''
	if type == 'bedroom sets':
		name = "Size"

	print("Option Name: " + name)

	return name

def set_option_value(type):
	value = ''
	if type == 'bedroom sets':
		value = "King"

	print("Option Value: " + value)

	return value

# ====== Helper Functions =====
def roundup(x):
	return int(math.ceil(x / 100.0)) * 100
