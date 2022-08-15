# tag-generator.py
# given vendor, year of publication, colors, materials, and finishes,
# create tags

import re, generator

vendor = "Ashley"
publication_year = "2020"

input = "descrip"
arranged_data = []

all_details = generator.extract_data(vendor, input, "tsv")

num_items = len(all_details)

if num_items > 0:
	for det_idx in range(len(all_details)):
		details = all_details[det_idx]

		sku = handle = colors = materials = finishes = ''

		color_data = []
		material_data = []
		finish_data = []

		tags = color_tags = material_tags = finish_tags = ''

		if len(details) > 0:
			sku = details[0].strip().lower()
			handle = details[1].strip().lower()
			colors = details[4].strip().lower()
			#print("Colors: " + colors)
			materials = details[5].strip().lower()
			materials = re.sub('full ','',materials)
			materials = re.sub(' front','',materials)
			materials = re.sub(' back','',materials)
			#print("Materials: " + materials)
			finishes = details[6].strip().lower()
			#print("Finishes: " + finishes)

		if colors != "n/a":
			color_data = re.split(',|/|&|\\band|\\bwith',colors)
		#print("Color Data: " + str(color_data))
		if materials != "n/a":
			material_data = re.split(',|/|&|\\band|\\bwith',materials)
		#print("Material Data: " + str(material_data))
		if finishes != "n/a":
			finish_data = re.split(',|/|&|\\band|\\bwith',finishes)
		#print("Finish Data: " + str(finish_data))

		for color in color_data:
			color = color.strip()
			color = color.rstrip(' -') # for Global but maybe also for others
			color = color.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
			if color != '':
				color_tags += "color-" + color + ", "
		color_tags = color_tags.rstrip(', ')
		#print("Color Tags: " + color_tags)
		for material in material_data:
			material = material.strip()
			material = material.rstrip(' -') # for Global but maybe also for others
			material = material.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
			if material != '':
				material_tags += "material-" + material + ", "
		material_tags = material_tags.rstrip(', ')
		#print("Material Tags: " + material_tags)
		for finish in finish_data:
			finish = finish.strip()
			finish = finish.rstrip(' -') # for Global but maybe also for others
			finish = finish.rstrip(' w') # b/c splits on slash so abbrev w/ needs special handling
			if finish != '':
				finish_tags += "finish-" + finish + ", "
		finish_tags = finish_tags.rstrip(', ')
		#print("Finish Tags: " + finish_tags)

		tags = vendor + publication_year

		if colors != "n/a":
			tags += ", " + color_tags

		if materials != "n/a":
			tags += ", " + material_tags

		if finishes != "n/a":
			tags += ", " + finish_tags

		print(tags)
