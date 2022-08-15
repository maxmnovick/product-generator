# type-generator.py
# generate types based on product handle
# name input <vendor>-<input>-init-data.<extension>

import generator, reader, re

vendor = "Ashley"
input = "descrip"
output = "type"
extension = "tsv"

arranged_types = [] # store types instead of printing

all_details = generator.extract_data(vendor, input, extension)

num_items = len(all_details)

if num_items > 0:
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]

		handle = final_type = ''

		handle_data = []

		all_keywords = reader.read_keywords(output)

		# look at item handle to determine type
		if len(item_details) > 0:
			handle = item_details[1].strip().lower() # need to know field number in given table

			# keywords in form without dashes so remove dashes from handle to compare to keywords
			dashless_handle = re.sub('-', ' ', handle)

			for type, type_keywords in all_keywords.items():
				#print("Type: " + type)
				#print("Type Keywords: " + str(type_keywords))
				for keyword in type_keywords:
					#print("Keyword: " + keyword)
					if re.search(keyword,dashless_handle):
						final_type = type
						break

				if final_type != '':
					break
		else:
			print("Warning: No details for this item!")

		print(final_type)
