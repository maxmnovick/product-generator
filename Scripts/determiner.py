# determiner.py
# determine choices with complicated conditions

import re

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
                print("field_name: " + field_name)
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