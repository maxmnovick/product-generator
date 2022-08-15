# description-generator.py
# create product descriptions based on given info
# insert info into product description template

# read catalog with dimension info

import re, generator, reader

vendor = "Global"
input = "descrip"
arranged_data = []

def arrange_details():
	all_details = generator.extract_data(vendor, input, "tsv")
	arranged_details = []

	num_items = len(all_details)
	if num_items > 0:

		#arranged_colors = arrange_colors(all_details)
		#arranged_materials = arrange_materials(all_details)
		#arranged_finishes = arrange_finishes(all_details)

		for det_idx in range(len(all_details)):
			details = all_details[det_idx]

			colors = materials = finishes = ''

			color_data = []
			material_data = []
			finish_data = []

			final_details = color_details = material_details = finish_details = ''

			if len(details) > 0:
				sku = details[0].strip().lower()
				handle = details[1].strip().lower()
				colors = details[2].strip().lower()
				#print("Colors: " + colors)
				materials = details[3].strip().lower()
				materials = re.sub('full ','',materials)
				materials = re.sub(' front','',materials)
				materials = re.sub(' back','',materials)
				#print("Materials: " + materials)
				finishes = details[4].strip().lower()
				#print("Finishes: " + finishes)

			if colors != "n/a":
				color_data = re.split(',|/|&',colors)
			#print("Color Data: " + str(color_data))
			if materials != "n/a":
				material_data = re.split(',|/|&',materials)
			#print("Material Data: " + str(material_data))
			if finishes != "n/a":
				finish_data = re.split(',|/|&',finishes)
			#print("Finish Data: " + str(finish_data))

			color_details = "Color: "
			for color in color_data:
				color = color.strip()
				color = color.rstrip(' -') # for Global but maybe also for others
				if color != '':
					color = re.sub('\"','\'',color)
					color_details += color + ", "
			color_details = color_details.rstrip(', ')
			color_details += ". "
			#print("Color Details: " + color_details)
			material_details = "Material: "
			for material in material_data:
				material = material.strip()
				material = material.rstrip(' -') # for Global but maybe also for others
				if material != '':
					material = re.sub('\"','\'',material)
					material_details += material + ", "
			material_details = material_details.rstrip(', ')
			material_details += ". "
			#print("Material Details: " + material_details)
			finish_details = "Finish: "
			for finish in finish_data:
				finish = finish.strip()
				finish = finish.rstrip(' -') # for Global but maybe also for others
				if finish != '':
					finish = re.sub('\"','\'',finish)
					finish_details += finish + ", "
			finish_details = finish_details.rstrip(', ')
			finish_details += ". "
			#print("Finish Details: " + finish_details)

			det_string = ''
			if colors != "n/a":
				det_string = "\"" + color_details + "\""

			if materials != "n/a":
				det_string += ",CHAR(10),\"" + material_details + "\""

			if finishes != "n/a":
				det_string += ",CHAR(10),\"" + finish_details + "\""

			# if arranging details separate from other parts of description
			# final_details = "=CONCATENATE(\"" + color_details + "\""
			#
			# if materials != "n/a":
			# 	final_details += ",CHAR(10),\"" + material_details + "\""
			#
			# if finishes != "n/a":
			# 	final_details += ",CHAR(10),\"" + finish_details + "\""
			#
			# final_details += ")"

			#det_string = arranged_colors + arranged_materials + arranged_finishes

			#print(final_details)
			arranged_details.append(det_string)

		arranged_data = arranged_details
	else:
		print("Warning: No details given!")

	return arranged_details

def determine_given_dimensions(product_details):
	given_dims = True

	for variant_details in product_details:
		width = depth = height = ''

		if len(variant_details) > 5:
			width = variant_details[5]

			if len(variant_details) > 6:
				depth = variant_details[6]

				if len(variant_details) > 7:
					height = variant_details[7]
		else:
			given_dims = False

		if width == '' or width.lower() == 'n/a':
			# no width given but maybe other dims given
			if depth == '' or depth.lower() == 'n/a':
				# no width or depth given but maybe height given
				if height == '' or height.lower() == 'n/a':
					given_dims = False

	return given_dims

def arrange_dimensions():
	# get dimensions

	all_details = generator.extract_data(vendor, input, "tsv")

	arranged_dimensions = []

	handle = previous_handle = dim_string = ''

	num_items = len(all_details)

	if num_items > 0:

		isolated_products = generator.isolate_products(all_details)

		for product in isolated_products:
			# isolated product

			sizes = {
				"King":'',
				"Queen":'',
				"Full":''
			}

			dim_string = ''
			if determine_given_dimensions(product):
				dim_string = "Dimensions (in): " # only if at least 1 of the variants has dimensions

				for variant_idx in range(len(product)):
					item_details = product[variant_idx]
					#print("dim: " + str(item_details))

					width = depth = height = ''

					if len(item_details) > 5:
						handle = item_details[1]
						#print("Handle: " + handle)
						width = item_details[5]

						if len(item_details) > 6:
							depth = item_details[6]

							if len(item_details) > 7:
								height = item_details[7]

					#print("Width: " + width + ", Depth: " + depth + ", Height: " + height)
					#print("Depth: " + depth)
					#print("Height: " + height)

					# get list of option name-value pairs
					option_data = generator.generate_options(item_details)
					option_names = []
					option_values = []
					if len(option_data) > 0:
						option_names = option_data[0]
						option_values = option_data[1]

					size_opt = False

					# get the value of the size option, if there is one
					opt_idx = 0
					for opt_name in option_names:
						if opt_name == 'Size':
							size_opt = True
							break
						opt_idx += 1

					width_fmla = depth_fmla = height_fmla = '\"\"'
					if width != '' and width != 'n/a':
						width_fmla = "\"" + width + "\",CHAR(34),\" W \""
					if depth != '' and depth != 'n/a':
						depth_fmla = "\"" + depth + "\",CHAR(34),\" D \""
					if height != '' and height != 'n/a':
						height_fmla = "\"" + height + "\",CHAR(34),\" H \""

					dim_fmla = width_fmla + ",\"x \"," + depth_fmla + ",\"x \"," + height_fmla + "\". \""

					final_dim_fmla = ''
					if size_opt:
						size_value = option_values[opt_idx]

						sizes[size_value] = dim_fmla

					else:
						final_dim_fmla = "\"" + dim_string + "\"," + dim_fmla
						arranged_dimensions.append(final_dim_fmla)

					# todo: handle situation where multiple values or range of values given
					#if not reader.is_number(width):
						#print("Warning: Width value is not a number!")

				if size_opt:
					for size, dims in sizes.items():
						if dims != '':
							print(size + ": " + dims)
							#print(dim_string)
							arranged_dimensions.append(final_dim_fmla)
	else:
		print("Warning: No dimensions given!")

	return arranged_dimensions

# use input descrip when input data has details and dimension data
if input == "dim":

	dim_string = arrange_dimensions()

elif input == "details":

	det_string = arrange_details()

elif input == "descrip":

	dim_strings = arrange_dimensions()

	#print("\n======\n")

	det_strings = arrange_details()

	for idx in range(len(dim_strings)):
		descrip_string = "=CONCATENATE(" + det_strings[idx] + ",CHAR(10)," + dim_strings[idx] + ")"
		print(descrip_string)

	# # get descriptions
	# body_html = details = dimensions = ''
	#
	# all_descriptions = generator.extract_data(input)
	#
	# arranged_descriptions = []
	#
	# handle = previous_handle = ''
	#
	# num_items = len(all_descriptions)
	#
	# if num_items > 0:
	# 	for des_idx in range(len(all_descriptions)):
	# 		des = all_descriptions[des_idx]
	#
	# 		des_string = 'null\n'
	#
	# 		color = material = finish = ''
	#
	# 		if len(des) > 0:
	# 			handle = des[0]
	# 			body_html = des[1]
	# 			if len(des) > 2:
	# 				details = des[2]
	# 				detail_parts = details.split(".")
	# 				color = detail_parts[0].strip()
	# 				material = detail_parts[1].strip()
	# 				finish = detail_parts[2].strip()
	# 				if len(des) > 3:
	# 					dimensions = des[3]
	#
	# 		if handle != previous_handle:
	# 			des_string = handle + ": \n" + body_html + "\n" + color + ". \n" + material + ". \n" + finish + ". \n" + dimensions + "\n"
	#
	# 		des_num = des_idx + 2
	# 		print(des_string)
	# 		arranged_descriptions.append(des_string)
	#
	# 		previous_handle = handle
	#
	# 	arranged_data = arranged_descriptions

# format dimensions for description
#print("Dimensions: " + str(width) + "\" W" + str(depth) + "\" D" + str(height) + "\".")

generator.write_data(arranged_data, input)
