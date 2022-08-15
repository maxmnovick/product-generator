# option-generator.py
# generate Option Values and Names
# based on given variant sku w/ known option keywords

import generator, reader, re

vendor = "Ashley"
input = "descrip"
output = "option"
extension = "tsv"

arranged_options = []

all_details = generator.extract_data(vendor, input, extension)

num_items = len(all_details)

if num_items > 0:
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		#print("Item Details: " + str(item_details))

		sku = color = title = ''

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

						# if no codes found in sku or title, check other fields for this item such as color field
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



		names = ''
		for name in final_opt_names:
			names += name + ','
		names = names.rstrip(',')
		#print("Final Option Names: " + names)
		values = ''
		for value in final_opt_values:
			values += value + ','
		values = values.rstrip(',')
		#print("Final Option Values: " + values)

		final_opt_string = final_opt_string.rstrip(',')
		#print("Final Option String: " + final_opt_string + "\n\n")
		print(final_opt_string)
