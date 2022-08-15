# option-generator.py
# generate Option Values and Names
# based on given variant sku w/ known option keywords

import generator, reader, re

vendor = "Global"
input = "descrip"
output = "option"
extension = "tsv"

arranged_types = []

all_details = generator.extract_data(vendor, input, extension)

num_items = len(all_details)

if num_items > 0:
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]

		sku = final_opt_value = ''

		all_keywords = reader.read_keywords(output)

		# look at item sku to determine options
		# if nothing apparent from sku, then check other fields like color and material
		# do not rely entirely on sku b/c could be ambiguous codes that may appear as part of other words not meant to indicate options
		# example: W is code for wenge brown for vendor=Global, but W is likely to mean something else for other vendors
		if len(item_details) > 0:
			sku = item_details[0].strip().lower()
			
			# option codes must only be considered valid when they are the entire word in the sku, so must remove dashes to separate codes
			dashless_sku = re.sub('-',' ',sku)

			# loop for each type of option, b/c need to fill in value for each possible option (eg loop for size and then loop for color in case item has both size and color options)
			for option, option_keywords in all_keywords.items():
				print("Option: " + option)
				print("Option Keywords: " + str(option_keywords))
				for keyword in option_keywords:
					print("Keyword: " + keyword)
					if re.search(keyword,dashless_sku):
						final_opt_value = option
						break

				if final_opt_value != '':
					break
		else:
			print("Warning: No details for this item!")

		print("Final Option Value: " + final_opt_value + "\n")
		#print(final_opt_value)