# reader.py
# functions for a reader

import json, re

class Measurement:
	def __init__(self, meas_value, meas_type):
		self.meas_value = meas_value
		self.meas_type = meas_type

def extract_data(input, extension):
	input = re.sub(' ','-',input)
	#catalog_filename = "../Data/" + input + "-init-data." + extension
	catalog_filename = "../Data/" + input + "-details." + extension
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
	keys_filename = "../Data/keywords/" + key_type + "-keywords.json"

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
	keys_filename = "../Data/standards/" + standard_type + ".json"

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
	#print("=== Format Dimension === ")

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
			total_meas = measurement

	else:
		print("Warning for " + handle + ": Invalid measurement found while formatting a dimension: \"" + measurement + "\"!")

	#print("Total Measurement (in): " + total_meas)
	return total_meas
