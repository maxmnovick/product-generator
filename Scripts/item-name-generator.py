# item-name-generator.py
# used for zoho inventory
# item name is Product Title + option values with slashes b/t each value

import generator, re

vendor = "Ashley"
input = "descrip"
extension = "tsv"

arranged_names = [] # store item names instead of printing

all_details = generator.extract_data(vendor, input, extension)

num_items = len(all_details)

if num_items > 0:
	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		
		final_name = ''
		
		# look at item handle to determine title, and other details to determine options
		if len(item_details) > 0:
		
			product_title = generator.generate_title(item_details)
			#print("Product Title: " + product_title)
			final_name += product_title
			
			option_data = generator.generate_options(item_details)
			option_values = []
			if len(option_data) > 0:
				option_values = option_data[1]
				#print("Option Values: " + str(option_values))
				
			for value in option_values:
				final_name += "/" + value
		
		else:
			print("Warning: No details for this item!")
			
		#print("Final Name: " + final_name + "\n")
		print(final_name)