# title-generator.py
# given vendor, year of publication, colors, materials, and finishes,
# create tags

import re, generator

vendor = "Ashley"
input = "descrip"
arranged_data = []

all_handles = generator.extract_data(vendor, input, "tsv")

num_items = len(all_handles)

if num_items > 0:
	for handle_idx in range(len(all_handles)):
		handles = all_handles[handle_idx]

		handle = title = ''

		if len(handles) > 0:
			handle = handles[1].strip().lower()
			#print("Handle: " + handle)

		handle_words = re.split('-',handle)
		#print("Handle Words: " + str(handle_words))

		for word in handle_words:
			word = word.capitalize()
			title += word + ' '
		title = title.rstrip()
		print(title)
