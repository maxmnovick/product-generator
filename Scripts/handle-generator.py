# handle-generator.py
# generate handles based on descriptions or titles
import re, generator, reader

vendor = "Beautyrest"
input = "name"
output = "title"
extension = "tsv"

arranged_data = []

all_data = generator.extract_data(vendor, input, extension)

num_items = len(all_data)

if num_items > 0:

	if input == "name":
		all_names = all_data

		for item_idx in range(len(all_names)):
			item_details = all_names[item_idx]

			descrip = final_title_suffix = final_handle_suffix = final_handle = ''

			descrip_data = []

			all_keywords = reader.read_keywords(output)

			# look at item handle to determine type
			if len(item_details) > 0:
				# need to know field number in given table
				sku = item_details[0].strip().lower()
				descrip = item_details[1].strip().lower()
				collection_name = item_details[2].strip().lower()
				#print("Collection Name: " + collection_name)

				# keywords in form without dashes so remove excess from descrip to compare to keywords
				plain_descrip = descrip.lower().strip()

				for title_suffix, title_keywords in all_keywords.items():
					#print("Title Suffix: " + title_suffix)
					#print("Title Keywords: " + str(title_keywords))
					for keyword in title_keywords:
						#print("Keyword: " + keyword + "\n")
						if re.search(keyword,plain_descrip):
							final_title_suffix = title_suffix
							break

					if final_title_suffix != '':
						break

				# go from title format to handle format by adding dashes b/t words, b/c already lowercase
				final_handle_suffix = re.sub(' ','-',final_title_suffix)
				#print("Final Handle Suffix: " + final_handle_suffix)
				collection_name = re.sub(' ','-',collection_name)

				final_handle = collection_name + "-" + final_handle_suffix
			else:
				print("Warning: No details for this item!")

			print(final_handle)
			#print("===Final Handle: " + final_handle + "===\n")

	elif input == "titles":
		all_titles = all_data

		for title_idx in range(len(all_titles)):
			titles = all_titles[title_idx]

			title = handle = ''

			if len(titles) > 0:
				title = titles[0].strip().lower()
				#print("Title: " + title)

			title_words = re.split(' ',title)
			#print("Title Words: " + str(title_words))

			for word in title_words:
				word = word.lower()
				handle += word + '-'
			handle = handle.rstrip('-')
			print(handle)
