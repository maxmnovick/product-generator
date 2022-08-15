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

		# look at item handle to determine type
		if len(item_details) > 0:
			sku = item_details[0].strip().lower()

			# loop for each type of option, b/c need to fill in value for each possible option (eg loop for size and then loop for color in case item has both size and color options)
			for option, option_keywords in all_keywords.items():
				#print("Option: " + option)
				#print("Option Keywords: " + str(option_keywords))
				for keyword in option_keywords:
					#print("Keyword: " + keyword)
					if re.search(keyword,sku):
						final_opt_value = option
						break

				if final_opt_value != '':
					break
		else:
			print("Warning: No details for this item!")

		print(final_opt_value)