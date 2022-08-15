# collection-type-generator.py
# use product type to determine collection type
# b/c zoho requires collection type

import generator, reader, re

vendor = "Ashley"
input = "descrip"
output = "collection type"
extension = "tsv"

arranged_types = [] # store types instead of printing

all_details = generator.extract_data(vendor, input, extension)

num_items = len(all_details)

if num_items > 0:
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]

		final_collection_type = ''

		all_keywords = reader.read_keywords(output)

		# look at item handle to determine type
		if len(item_details) > 0:
			product_type = generator.generate_product_type(item_details)

			for type, type_keywords in all_keywords.items():
				#print("Type: " + type)
				#print("Type Keywords: " + str(type_keywords))
				for keyword in type_keywords:
					#print("Keyword: " + keyword)
					if re.search(keyword,product_type):
						final_collection_type = type
						break

				if final_collection_type != '':
					break
		else:
			print("Warning: No details for this item!")

		#print(product_type + ", " + final_collection_type)
		print(final_collection_type)