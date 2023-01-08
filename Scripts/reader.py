# reader.py
# functions for a reader

import json, re, pandas
import determiner # custom
import generator # to generate handle, to warn if an item has an error by handle (consider assigning ID based on init order of input details, to save compute)

class Measurement:
	def __init__(self, meas_value, meas_type):
		self.meas_value = meas_value
		self.meas_type = meas_type

# get data from a file and format into a list (same as generator version of this fcn but more general)
def extract_data(input, extension, data_type="details"):
	input = re.sub(' ','-',input)
	data_type = re.sub(' ','-',data_type)
	#catalog_filename = "../Data/" + input + "-init-data." + extension
	catalog_filename = "../Data/" + input + "-" + data_type + "." + extension
	#catalog_filename = "../Data/" + vendor + "-" + input + "-details." + extension

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
	input = re.sub(' ','-',input)
	catalog_filename = "../Data/" + input + "-final-data.csv"
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	for row_idx in range(len(arranged_data)):
		catalog_file.write(arranged_data[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()

# valid for json files
def read_keywords(key_type):
	key_type = re.sub(' ','-',key_type)
	keys_filename = "../data/keywords/" + key_type + "-keywords.json"
	#print("keys_filename: " + keys_filename)

	lines = [] # capture each line in the document

	try:
		with open(keys_filename, encoding="UTF8") as keys_file:
			line = ''
			for key_info in keys_file:
				line = key_info.strip()
				lines.append(line)

			keys_file.close()
	except:
		print("Warning: No keywords file!")

	# combine into 1 line
	condensed_json = ''
	for line in lines:
		condensed_json += line

	#print("Condensed JSON: " + condensed_json)

	# parse condensed_json
	keys = json.loads(condensed_json)

	return keys

# valid for json files
def read_standards(standard_type):
	standard_type = re.sub(' ','-',standard_type)
	keys_filename = "../data/standards/" + standard_type + ".json"

	lines = [] # capture each line in the document

	try:
		with open(keys_filename, encoding="UTF8") as keys_file:
			line = ''
			for key_info in keys_file:
				line = key_info.strip()
				lines.append(line)

			keys_file.close()
	except:
		print("Warning: No keywords file!")

	# combine into 1 line
	condensed_json = ''
	for line in lines:
		condensed_json += line

	#print("Condensed JSON: " + condensed_json)

	# parse condensed_json
	keys = json.loads(condensed_json)

	return keys

# valid for json files
def read_typos():
	keys_filename = "../data/keywords/typos.json"

	lines = [] # capture each line in the document

	try:
		with open(keys_filename, encoding="UTF8") as keys_file:
			line = ''
			for key_info in keys_file:
				line = key_info.strip()
				lines.append(line)

			keys_file.close()
	except:
		print("Warning: No typos file!")

	# combine into 1 line
	condensed_json = ''
	for line in lines:
		condensed_json += line

	#print("Condensed JSON: " + condensed_json)

	# parse condensed_json
	keys = json.loads(condensed_json)

	return keys

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def determine_measurement_type(measurement, handle):

	#print("=== Determine Measurement Type=== ")

	meas_type = 'rectangular' # default to rectangular WxD b/c most common. alt option: round

	measurement = measurement.lower() # could contain words such as "Round" or "n/a"
	#print("Measurement: " + measurement)

	blank_meas = True
	if measurement != 'n/a' and measurement != '':
		blank_meas = False

	if not blank_meas:
		# eg "9\' x 2\'"
		if re.search('\'|\"',measurement): # given in units of feet and/or inches

			#print("===Measurement Given in Custom Format===")

			meas_ft_value = meas_in_value = 0.0

			#if re.search("round",measurement):
				#print("Measurement is of Round Object, so Diam or Rad?")

			meas_vars = []
			meas_value = measurement # from here on use value

			if re.search('\'\d+\"\s*\d+(\'|\")',meas_value):
				meas_type = 'combined_rect' #already set by default
				print("Warning for " + handle + ": Width and Depth given in same field, while determining measurement type: \"" + meas_value + "\"!")
			elif re.search('(\")\s*.+(\")',meas_value) or re.search('(\')\s*.+(\')',meas_value):
				meas_type = 'invalid'
				print("Warning for " + handle + ": 2 values with the same unit given while determining measurement type: \"" + meas_value + "\"!")
			# assuming meas value followed by meas type
			elif re.search('\s+',meas_value):
				#print("Measurement contains a space character.")
				meas_vars = re.split('\s+',meas_value)
				#print("Meas vars: " + str(meas_vars))
				meas_value = meas_vars[0]
				meas_type = meas_vars[1]

	#print("Measurement value: " + meas_value)
	#print("Measurement type: \"" + meas_type + "\"\n")

	return meas_type

# input could already be in standard format, which is plain number with default unit of inches
# if input in format a'b" need to convert to standard format and keep original format for use later or make a function to convert it back
def format_dimension(measurement, handle):
	#print("=== Format Dimension for " + measurement + "=== ")

	# define local variables
	total_meas = '1' # return output, result of this function. default=1 for zoho inventory

	measurement = measurement.lower() # could contain words such as "Round", "Square" or "n/a"

	blank_meas = True
	if measurement != 'n/a' and measurement != '':
		blank_meas = False

	if not blank_meas:

		# eg "9\' x 2\'"
		if re.search('\'|\"',measurement): # given in units of feet and/or inches

			#print("===Measurement Given in Custom Format===")

			meas_ft_value = meas_in_value = 0.0

			#if re.search("round",measurement):
				#print("Measurement is of Round Object, so Diam or Rad?")

			meas_vars = []
			meas_value = measurement # from here on use value
			meas_type = 'rectangular' # default to rectangular WxD b/c most common. option: round

			# assuming meas value followed by meas type
			if re.search('\s+',meas_value):
				#print("Measurement contains a space character.")
				meas_vars = re.split('\s+',meas_value,1)
				#print("Meas vars: " + str(meas_vars))
				meas_value = meas_vars[0]
				meas_type = meas_vars[1]

			#print("Measurement value: " + meas_value)
			#print("Measurement type: \"" + meas_type + "\"\n")

			# if we find a foot symbol in the measurment
			if re.search("\'",measurement):
				#print("Measurement before removing non-digits: " + measurement)
				# TODO: remove all non-digits

				meas_ft_and_in = meas_value.split("\'")
				#print("Measurement Feet and Inches: " + str(meas_ft_and_in))
				meas_ft = meas_ft_and_in[0].strip()
				if meas_ft != '' and meas_ft.lower() != 'n/a':
					#print("Meas Ft: \"" + meas_ft + "\"")
					meas_ft_value = float(meas_ft)

# 				if meas_ft == '':
# 					print("Meas Ft is blank!")
				#print("Measurement Feet: " + meas_ft)
				#print("Measurement Feet Value: " + str(meas_ft_value))

				meas_in = meas_ft_and_in[1].rstrip("\"").strip()
				if meas_in != '' and meas_in.lower() != 'n/a':
					#print("Meas In: \"" + meas_in + "\"")
					meas_in_value = float(meas_in)

# 				if meas_in == '':
# 					print("Meas In is blank!")
				#print("Measurement Inches: " + meas_in)
				#print("Measurement Inches Value: " + str(meas_in_value))
			# if measured in inches, not feet
			elif re.search("\"",meas_value):
				meas_value_data = re.split('\"',meas_value,1)
				meas_in = meas_value_data[0].rstrip("\"").strip()

				if meas_in != '' and meas_in.lower() != 'n/a':
					#print("Meas In: \"" + meas_in + "\"")
					meas_in_value = float(meas_in)

# 				if meas_in == '':
# 					print("Meas In is blank!")
				#print("Measurement Inches: " + meas_in)
				#print("Measurement Inches Value: " + str(meas_in_value))

			total_meas = str(int(round(meas_ft_value * 12.0 + meas_in_value)))

		else:
			#print("Default Measurement")
			total_meas = measurement

	else:
		print("Warning for " + handle + ": Invalid measurement found while formatting a dimension: \"" + measurement + "\"!")

	#print("Total Measurement (in): " + total_meas)
	return total_meas

def read_raw_vendor_product_data(vendor, file_keywords=[]):
	print("\n===Read Raw Vendor Product Data===\n")
	if len(file_keywords) == 0:
		file_keywords = ["price","spec","image"] # equivalent to files selected on web format
	print("file_keywords: " + str(file_keywords))

	ext = 'tsv'

	desired_field_names = ['sku', 'collection', 'type', 'intro', 'color', 'material', 'finish', 'width', 'depth', 'height', 'weight', 'features', 'cost', 'images', 'barcode'] #corresponding to keys in dict. determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	current_sheet_field_name = '' # loop thru each sheet and each field in each sheet

	all_sheet_all_field_values = [] # only relevant fields?
	for data_type in file_keywords:
		current_sheet_all_field_values = {} # could init to have desired fields so when we loop thru later we can check if they are blank, otherwise it will return undefined for that key. or just check if key exists
		print("\n====== Read Sheet: " + data_type + " ======\n")
		# remove leading zeros from sku in price list to match sku in spec sheet
		filepath = "../data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
		if not re.search("sheet",data_type):
			filepath = "../data/" + vendor + "-" + data_type.replace(" ","-") + "-sheet." + ext

		current_sheet_df = pandas.read_table(filepath).fillna('n/a')
		current_sheet_df.columns = current_sheet_df.columns.str.strip() # remove excess spaces
		current_sheet_headers = current_sheet_df.columns.values
		#print("current_sheet_headers: " + str(current_sheet_headers))
		# first check if any desired fields
		# format data. standardize keys. remove extra characters from values.
		for desired_field_name in desired_field_names:

			current_sheet_field_name = determiner.determine_field_name(desired_field_name, current_sheet_df) # actual name in raw data sheet
			if current_sheet_field_name != '':
				all_current_sheet_field_values = []
				text_fields = ['type','features','intro','finish','material'] # plain text is interpreted specifically
				dim_fields = ['width','depth','height','weight'] # consider special formatting or rounding for dims
				if desired_field_name == 'sku':
					all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().str.lstrip("0").tolist()
				elif desired_field_name == 'cost':
					all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.replace("$","").str.replace(",","").str.strip().tolist()
				elif desired_field_name == 'images':
					all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().str.lstrip("[").str.rstrip("]").tolist()
				elif desired_field_name in text_fields:
					all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().str.replace(";","-").tolist()
				elif desired_field_name in dim_fields:
					#print("dim field")
					all_current_sheet_field_dims = current_sheet_df[current_sheet_field_name].astype('string').str.strip().tolist()
					for field_val in all_current_sheet_field_dims:
						if field_val != 'n/a' and field_val != '':
							field_val = str(round(float(field_val)))
						all_current_sheet_field_values.append(field_val)
					#print("all_current_sheet_field_values: " + str(all_current_sheet_field_values))
				else:
					all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().tolist()
				#print("all_current_sheet_field_values: " + desired_field_name + " " + str(all_current_sheet_field_values))
				current_sheet_all_field_values[desired_field_name] = all_current_sheet_field_values
			# for header in current_sheet_headers:
			# 	if determiner.determine_matching_field(field_name, header):
			# 		print("field_name matches header: " + field_name + ", " + header)

		#all_current_sheet_field_values = current_sheet_df[current_sheet_field_name]
		#print("current_sheet_all_field_values: " + str(current_sheet_all_field_values))
		all_sheet_all_field_values.append(current_sheet_all_field_values)

	#print("all_sheet_all_field_values: " + str(all_sheet_all_field_values))
	return all_sheet_all_field_values

def read_raw_vendor_inv_data(vendor):

	ext = 'tsv'

	# we dont have desired field names for inventory because we need to see what fields are available and use them all
	# we do have keywords, such as inventory, inv, location
	desired_field_names = ['location'] #corresponding to keys in dict. determine by type of generator. bc this is product generator we are look for product fields to form catalog, before it is converted to import
	current_sheet_field_name = '' # loop thru each sheet and each field in each sheet

	data_type = 'inv' # short for inventory
	
	current_sheet_all_field_values = {} # could init to have desired fields so when we loop thru later we can check if they are blank, otherwise it will return undefined for that key. or just check if key exists
	print("\n====== Read Sheet: " + data_type + " ======\n")
	# remove leading zeros from sku in price list to match sku in spec sheet
	filepath = "../data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
	if not re.search("sheet",data_type):
		filepath = "../data/" + vendor + "-" + data_type.replace(" ","-") + "-sheet." + ext

	current_sheet_df = pandas.read_table(filepath).fillna('n/a')
	current_sheet_df.columns = current_sheet_df.columns.str.strip() # remove excess spaces
	#print("current_sheet_df: " + str(current_sheet_df))
	current_sheet_headers = current_sheet_df.columns.values
	#print("current_sheet_headers: " + str(current_sheet_headers))
	# first check if any desired fields
	# format data. standardize keys. remove extra characters from values.
	for field_idx in range(len(current_sheet_headers)):
		current_sheet_field_name = current_sheet_headers[field_idx] # actual name in raw data sheet
		#print("current_sheet_field_name: " + current_sheet_field_name)
		# if the field name has the keyword location then see if we can determine the location name and number by field name
		# format: location_ny_qty or locations.<location_name>_qty, example: locations.la_qty
		if re.search("qty", current_sheet_field_name):
			location_name = re.sub("locations\\.|_qty","", current_sheet_field_name)
			if len(location_name) > 3:
				location_name = location_name.title()
			else:
				location_name = location_name.upper()
			print("location_name: " + location_name)

		all_current_sheet_field_values = current_sheet_df[current_sheet_field_name].astype('string').str.strip().tolist() # []

		#print("all_current_sheet_field_values: " + current_sheet_field_name + " " + str(all_current_sheet_field_values))
		current_sheet_all_field_values[current_sheet_field_name] = all_current_sheet_field_values
				
				

	inv_sheet_all_field_values = current_sheet_all_field_values

	return inv_sheet_all_field_values

def format_vendor_product_data(raw_data, key):
	print("\n===Format Vendor Product Data===\n")
	print("raw_data: " + str(raw_data))

	data = str(raw_data) # should it be blank init so we can check it has been set easily?

	text_fields = ['type','features','intro','finish','material'] # plain text is interpreted specifically
	if key == 'sku':
		data = str(raw_data).strip().lstrip("0")
	elif key == 'cost':
		data = str(raw_data).replace("$","").replace(",","").strip()
	elif key == 'images':
		data = str(raw_data).strip().lstrip("[").rstrip("]")
	elif key in text_fields:
		data = str(raw_data).strip().replace(";","-")
	else:
		data = str(raw_data).strip()
	print("data: " + key + " " + str(data))

	return data

def format_field_values(field_name, all_details, init_all_details=[]):
	print("Format field values for " + field_name)

	# General Info from Details table
	field_values = []
	field_idx = 0

	# order of detail fields makes it faster compute, but could change to find key to make more robust
	sku_idx = 0
	collection_idx = 1
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
	
	if field_name == 'sku':
		field_idx = sku_idx

		# simplest transfer no formatting
		for item_details in all_details:
			value = item_details[field_idx]
			field_values.append(value)


	elif field_name == 'width':
		field_idx = width_idx

		# Read and Format Measurements
		# assign to reader
		default_meas_type = "rectangular"

		measurements = []

		# use dims from details table for shopify description and zoho inventory
		#print("=== Get Widths ===")
		# field values: all_widths = []
		for item_idx in range(len(all_details)):
			item_details = all_details[item_idx]
			init_item_details = init_all_details[item_idx]

			handle = generator.generate_handle(item_details) # we need to know which products have invalid measurements
			#print("Item: " + handle)

			#width = item_details[width_idx]
			#print("Width: " + width)
			#init_width = init_item_details[width_idx]
			#print("Init Width: " + init_width)

			meas_type = determiner.determine_measurement_type(item_details[width_idx], handle) # we need to know if the measurement is of a round or rectangular object so we can format output

			#print("Width: " + width)
			#init_width = init_item_details[width_idx]
			#print("Init Width: " + init_width)

			width = format_dimension(item_details[width_idx], handle)

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

			field_values.append(width)
			#measurements.append(m)

			#print("=== Got Widths ===")
			#print("Width: " + width)
			#init_width = init_item_details[width_idx]
			#print("Init Width: " + init_width)

		#writer.display_all_item_details(init_all_details)
	elif field_name == 'depth':
		for item_idx in range(len(all_details)):
			item_details = all_details[item_idx]
			handle = generator.generate_handle(item_details) # we need to know which products have invalid measurements
			depth = format_dimension(item_details[depth_idx], handle)
			item_details[depth_idx] = depth
			field_values.append(depth)

	elif field_name == 'height':
		for item_details in all_details:
			handle = generator.generate_handle(item_details) # we need to know which products have invalid measurements
			height = format_dimension(item_details[height_idx], handle)
			item_details[height_idx] = height
			field_values.append(height)

	elif field_name == 'weight':
		#print("\n===Get All Weights===\n")
		for item_details in all_details:
			
			#print("item_details: " + str(item_details))
			handle = generator.generate_handle(item_details) # we need to know which products have invalid measurements
			weight = ''
			# check for blank handle here for precaution
			if handle == '':
				print("WARNING: Blank handle while getting weights!")
			else:
				weight = format_dimension(item_details[weight_idx], handle)
			item_details[weight_idx] = weight
			field_values.append(weight)

	elif field_name == 'cost':
		for item_details in all_details:
			cost = ''
			if len(item_details) > cost_idx:
				cost = item_details[cost_idx]
			if cost.lower() == 'n/a':
				field_values.append('')
			else:
				field_values.append(cost)

	elif field_name == 'barcode':
		for item_details in all_details:
			barcode = ''
			if len(item_details) > barcode_idx:
				barcode = item_details[barcode_idx]
			if barcode.lower() == 'n/a':
				field_values.append('')
			else:
				field_values.append(barcode)

	elif field_name == 'img':
		for item_details in all_details:
			img_src = ''
			if len(item_details) > img_src_idx:
				img_src = item_details[img_src_idx]
				img_src = re.sub(";",",",img_src) # semicolons will be interpreted as column delimeters later so they are reserved, and we want all img srcs in same column for import
			if img_src.lower() == 'n/a':
				field_values.append('')
			else:
				field_values.append(img_src)

	elif field_name == 'vrnt_img':
		for item_idx in range(len(all_details)):
			item_details = all_details[item_idx]
			vrnt_img = ''
			if len(item_details) > img_src_idx:
				img_src = item_details[img_src_idx]
				if not re.search(",",img_src): # we can only be sure it is correct variant img if only 1 img and 1 variant, else need more processing
					vrnt_img = img_src
			field_values.append(vrnt_img)

	print("field_values: " + str(field_values))
	return field_values


# file keywords like price, spec, img, inv
# then we cna look for files with those keys in them
# def read_all_items_info(file_keywords, vendor=''):
# 	print("\n===Read All Item Info===\n")
# 	print("file_keywords: " + str(file_keywords))

# 	for key in file_keywords:
# 		filename = key + "-sheet.tsv" # acme-price-sheet.tsv
# 		if vendor != '':
# 			filename = vendor + "-" + filename
		
# fix common typos
def fix_typos(text):
	#print("\n===Fix Typos===\n")

	typos = read_typos()
	#print("typos: " + str(typos))
	for correction, typo_keywords in typos.items():
		# print("correction: " + str(correction))
		# print("typo_keywords: " + str(typo_keywords))
		for typo_keyword in typo_keywords:
			# print("typo_keyword: " + typo_keyword)
			# if re.search(typo_keyword, text):
			# 	print('found typo ' + typo_keyword)
			text = re.sub(typo_keyword,correction,text)
			break # found keyword for this typo, so go to next typo

	return text