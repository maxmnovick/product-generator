# determiner.py
# determine choices with complicated conditions

import re
import reader # to read color stds to determine std color

def determine_matching_field(desired_field_name, current_field_name):
    print("desired_field_name: " + desired_field_name)
    print("current_field_name: " + current_field_name)

def determine_standard_key(raw_key):
    print("\n===Determine Standard Key for " + raw_key + "===\n")

    standard_key = ''

    all_field_keywords = { 
        'sku':['sku','item#'], 
        'collection':['collection'],
        'features':['features','acme.description'],
        'type':['product type','description'],
        'intro':['intro','short description'],
        'color':['color'],
        'material':['material'],
        'finish':['finish'],
        'width':['width'],
        'depth':['depth','length'],
        'height':['height'],
        'weight':['weight'],
        'cost':['cost','price'],
        'images':['image'],
        'barcode':['barcode']
    }

    for field_key, field_keywords in all_field_keywords.items():
        print("field_key, field_keywords: " + field_key + ", " + str(field_keywords))
        for keyword in field_keywords:
            raw_key_no_space = re.sub('(\\s+|_)','',raw_key.lower()) # unpredictable typos OR format in headers given by vendor such as 'D E S C R I P T I O N'
            keyword_no_space = re.sub('\\s', '', keyword)
            if re.search(keyword_no_space, raw_key_no_space):
                print("keyword " + keyword + " in raw_key " + raw_key)
                standard_key = field_key
                break
        if standard_key != '':
            break

    print("standard_key: " + standard_key)
    return standard_key

def determine_field_name(field, sheet_df):
    print("\n===Determine Field Name: " + field + "===\n")
    sheet_headers = sheet_df.columns.values

    field_keywords = { 
        'sku':['sku','item#'], 
        'collection':['collection'],
        'features':['features','acme.description'],
        'type':['product type','description'],
        'intro':['intro','short description'],
        'color':['color'],
        'material':['material'],
        'finish':['finish'],
        'width':['width'],
        'depth':['depth','length'],
        'height':['height'],
        'weight':['weight'],
        'cost':['cost','price'],
        'images':['image'],
        'barcode':['barcode']
    }
    keywords = field_keywords[field]
    matching_field = False
    field_name = ''
    for keyword in keywords:
        for header in sheet_headers:
            header_no_space = re.sub('(\\s+|_)','',header.lower()) # unpredictable typos OR format in headers given by vendor such as 'D E S C R I P T I O N'
            keyword_no_space = re.sub('\\s', '', keyword)
            if re.search(keyword_no_space, header_no_space):
                field_name = header
                #print("field_name: " + field_name)
                matching_field = True
                break
        if matching_field:
            break
    return field_name
    
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

			if re.search('\'\\d+\"\\s*\\d+(\'|\")',meas_value):
				meas_type = 'combined_rect' #already set by default
				print("Warning for " + handle + ": Width and Depth given in same field, while determining measurement type: \"" + meas_value + "\"!")
			elif re.search('(\")\\s*.+(\")',meas_value) or re.search('(\')\\s*.+(\')',meas_value):
				meas_type = 'invalid'
				print("Warning for " + handle + ": 2 values with the same unit given while determining measurement type: \"" + meas_value + "\"!")
			# assuming meas value followed by meas type
			elif re.search('\\s+',meas_value):
				#print("Measurement contains a space character.")
				meas_vars = re.split('\\s+',meas_value)
				#print("Meas vars: " + str(meas_vars))
				meas_value = meas_vars[0]
				meas_type = meas_vars[1]

	#print("Measurement value: " + meas_value)
	#print("Measurement type: \"" + meas_type + "\"\n")

	return meas_type

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

def determine_inv_location_key(location, item_inv):
	loc_key = ''
	for key in item_inv.keys():
		if re.search(location.lower(),key.lower()):
			#print("key: " + key)
			
			if re.search('qty', key.lower()):
				loc_key = key
				break
			
	return loc_key

def determine_stocked(sheet1_sku, all_inv, locations=[]):
	#print("\n===Determine Stocked===\n")
	#print("sheet1_sku: " + sheet1_sku)
	#print("all_inv: " + str(all_inv))
	stocked = False
	given_info = False # if we are given an item but no stock info we still want to display it
	if len(locations) == 0:
		locations = ['ny', 'nj', 'la', 'sf']
	for item_inv in all_inv:
		if item_inv['sku'] == sheet1_sku:
			#print("item_inv: " + str(item_inv))

			for loc in locations:
				#print("loc: " + loc)
				for key, val in item_inv.items():
					if re.search("qty",key) and re.search(loc,key):
						if round(float(val)) > 0: # problem dataframe reading decimal
							print(sheet1_sku + " is stocked in " + loc)
							stocked = True
							break
					elif re.search('eta',key): # if there is an eta then it will be stocked
						if val != '' and val.lower() != 'none':
							location = re.sub('locations\\.|_warehouse_eta','',key)
							print(sheet1_sku + " will be stocked in " + location)
							stocked = True
							break

				if stocked:
					break

			if not stocked:
				print(sheet1_sku + " Not Stocked")

			break
	
	

	return stocked

def determine_eta_header(item_inv):
	eta_header = ''
	for key in item_inv.keys(): # later may need to check both eta and loc to see if valid location but currently only eta given for la which is valid
		if re.search('eta',key):
			eta_header = key
			break
	return eta_header

def determine_inv_tracking(sku, all_inv):
	inv_tracking = False
	for item_inv in all_inv:
		item_sku = item_inv['sku']
		if sku == item_sku:
			inv_tracking = True
			break

	return inv_tracking

# solo product is from final item info split by ; delimiter
# could use catalog instead if we need to access product intro specifically but body html should be good enough
def determine_product_bundle(solo_product):
	print("\n===Determine Product Bundle===\n")
	#print("solo_product: " + str(solo_product))
	bundle = False

	# determine if loft bed bc treated differently
	# loft bed determined by handle bc type still bed, and handle same for all vrnts in fp
	product_handle_idx = 0
	product_handle = solo_product[0][product_handle_idx] # same for all vrnts so use first vrnt
	if re.search('loft-bed', product_handle):
		print("Product is loft bed, so check if optional items to bundle.")
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

		#intro_idx = 3
		body_html_idx = 2
		for vrnt in solo_product:
			#vrnt_intro = vrnt[intro_idx]
			vrnt_body_html = vrnt[body_html_idx]
			print("vrnt_body_html: " + vrnt_body_html)
			if re.search('optional.*bed.*under', vrnt_body_html.lower()):
				bundle = True
				print("Bundle Product")
				break

	# for loft bed, if no descrip stating optional bed, check if options size twin and queen

	return bundle

# if we do not find a standard color, do we still want to use the custom color as a tag?	
# yes bc need to see color else no color no filter. plus it will show which custom colors could be grouped into a standard color by new keyword
# problem is we need to minimize filter list to only standard colors so we cannot allow custom colors to make tags.
# instead pass warning so we can correct it by adding new keyword to colors.json
def determine_standard_color(color):
	print("\n===Determine Standard Color===\n")
	standard_color = ''
	standard_colors = reader.read_standards('colors')
	#print("standard_colors: " + str(standard_colors))
	for std_color, keywords in standard_colors.items():
		#print("std_color: " + std_color)
		for keyword in keywords:
			if re.search(keyword, color.lower()):
				standard_color = std_color
				break # found keyword so no need to see more
		if standard_color != '': # standard color would only be set if we determined color so no need to see more
			break

	if standard_color == '':
		print("Warning: could not find standard color for color " + color + "! ")

	return standard_color

# need value type to read standards file by name
def determine_standard(init_value, value_type):
	print("\n===Determine Standard for value: " + init_value + "===\n")
	standard = ''
	standards = reader.read_standards(value_type)
	#print("standards: " + str(standards))
	for std, keywords in standards.items():
		#print("std: " + std)
		for keyword in keywords:
			if re.search(keyword, init_value.lower()):
				standard = std
				break # found keyword so no need to see more
		if standard != '': # standard would only be set if we determined value so no need to see more
			break

	if standard == '':
		print("Warning: could not find standard for value " + init_value + "! ")

	return standard

# if we see duplicate opts bt 2 vrnts in same product this will cause error so show warning and handle
def determine_duplicate_opts(product):
	print("\n===Determine Duplicate Options===\n")
	# product = [[1,2,3...],[1,2,3...],...]
	#print("product: " + str(product))

	

	duplicate_opts = []


	vrnt_opt1_name_idx = 8
	vrnt_opt1_val_idx = 9
	vrnt_opt2_name_idx = 10
	vrnt_opt2_val_idx = 11
	vrnt_opt3_name_idx = 12
	vrnt_opt3_val_idx = 13
	
	
	option_strings = []
	option_data = []
	for vrnt in product:

		vrnt_opt_string = vrnt[vrnt_opt1_name_idx] + vrnt[vrnt_opt1_val_idx] + vrnt[vrnt_opt2_name_idx] + vrnt[vrnt_opt2_val_idx] + vrnt[vrnt_opt3_name_idx] + vrnt[vrnt_opt3_val_idx]
		option_strings.append(vrnt_opt_string)

		opt_names = [vrnt[vrnt_opt1_name_idx], vrnt[vrnt_opt2_name_idx], vrnt[vrnt_opt3_name_idx]]
		opt_vals = [vrnt[vrnt_opt1_val_idx], vrnt[vrnt_opt2_val_idx], vrnt[vrnt_opt3_val_idx]]
		option_data.append([opt_names,opt_vals])

	# if we find matching options bt 2 vrnts in same product then it will be considered invalid unless we use other info to create more options bc they are 2 vrnts so must have different options but the info in the description is limited
	for option_string in option_strings:
		count = option_strings.count(option_string)
		if count > 1:
			# found 2 vrnts with same options so not enough info in single vrnt so we must compare with another variant to see what options to add
			print("Duplicate Opts")
			duplicate_opts = option_data
			break

	print("duplicate_opts: " + str(duplicate_opts))
	return duplicate_opts

def determine_duplicate_product_opts(product_opt_data): # [[[names],[values]]]
	print("\n===Determine Duplicate Options===\n")
	# product_opt_data = [[names],[vals]]
	#print("product_opt_data: " + str(product_opt_data))

	duplicate_opts = []
	
	
	option_strings = []
	option_data = []
	for vrnt_opt_data in product_opt_data:

		opt_names = vrnt_opt_data[0] #[vrnt[vrnt_opt1_name_idx], vrnt[vrnt_opt2_name_idx], vrnt[vrnt_opt3_name_idx]]
		opt_vals = vrnt_opt_data[1] #[vrnt[vrnt_opt1_val_idx], vrnt[vrnt_opt2_val_idx], vrnt[vrnt_opt3_val_idx]]
		vrnt_opt_string = ''
		for opt_idx in range(len(opt_names)):
			vrnt_opt_string += opt_names[opt_idx] + opt_vals[opt_idx]
		option_strings.append(vrnt_opt_string)
		
		option_data.append([opt_names,opt_vals])

	# if we find matching options bt 2 vrnts in same product then it will be considered invalid unless we use other info to create more options bc they are 2 vrnts so must have different options but the info in the description is limited
	for option_string in option_strings:
		count = option_strings.count(option_string)
		if count > 1:
			# found 2 vrnts with same options so not enough info in single vrnt so we must compare with another variant to see what options to add
			print("Duplicate Opts")
			duplicate_opts = option_data
			break

	print("duplicate_opts: " + str(duplicate_opts))
	return duplicate_opts