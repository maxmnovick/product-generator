# collection.py
# functions for a collection,
# such as change condition, or sort products

import numpy as np
import datetime, re, catalog, product

# see what variations/options are actually included in this collection, out of all possible variations for this product type
def determine_valid_options(collection, type):
	print("\n=== Determine Valid Options for " + type + " ===\n")

	valid_option = False
	valid_opt_names = []

	item_names = determine_item_names(collection)

	valid_opt_names = []
	opt_codes = []

	# list of potential options a product could have
	size_option = False
	room_config_option = False

	#bs_pot_opt_names = ["size", "room configuration"] # bedroom set
	#ns_pot_opt_names = ["size", "bed side"] # nightstand
	#dr_pot_opt_names = ["width"] # dresser
	#all_pot_opt_names = [ bs_pot_opt_names, ns_pot_opt_names, dr_pot_opt_names ]

	all_pot_opt_names = {"bedroom sets": ['size','room configuration'], "nightstands": ['size','bed side'], "dressers": ['width'] }

	if type in all_pot_opt_names:
		potential_opt_names = all_pot_opt_names[type]

		if type == "bedroom sets":
			#potential_opt_names = all_pot_opt_names[type]

			# variant options
			sizes = [ 'king', 'queen' ]
			size_codes = [ 'ks', 'qs' ]
			size_code = ''

			opt_codes.append(size_codes)

			for pot_opt_name in potential_opt_names:
				#print("Potential Option Name: " + pot_opt_name)
				valid_option = False
				for item_name in item_names:

					#print("Item Name: " + item_name)

					if pot_opt_name == "size":
						size_opt_idx = 0 # first option in list of options
						for code in opt_codes[size_opt_idx]:
							#print("Option Name Code: " + code)
							#print("Does " + item_name + " contain " + code + "?")
							if re.search(code, item_name):
								#print("Code found in Item Name")
								valid_option = True
								break
							#else:
								#print("No Code in Item Name")
						if valid_option:
							#print("We know this is a valid option because we found a keyword in one of the items.")
							valid_opt_names.append(pot_opt_name)
							break

		elif type == "nightstands":
			#potential_opt_names = all_pot_opt_names[1]

			# variant options: either size or side
			sizes = [ "2 drawer", "3 drawer" ]
			size_codes = [ "2 dr", "3 dr" ]
			opt_codes.append(size_codes)
			size_code = ''

			sides = ["left", "right"]
			opt_codes.append(sides)
			side_code = ''

			# only loop through nightstand items
			ns_item_names = isolate_items_of_type(type, item_names)

			for pot_opt_name in potential_opt_names:
				#print("Potential Option Name: " + pot_opt_name)
				valid_option = False

				for item_name in ns_item_names:
					#print("Item Name: " + item_name)

					if pot_opt_name == "size":
						size_opt_idx = 0 # first option in list of options
						for code in opt_codes[size_opt_idx]:
							#print("Option Name Code: " + code)
							#print("Does " + item_name + " contain " + code + "?")
							if re.search(code, item_name):
								#print("Code found in Item Name")
								valid_option = True
								break
							#else:
								#print("No Code in Item Name")
						if valid_option:
							#print("We know this is a valid option because we found a keyword in one of the items.")
							valid_opt_names.append(pot_opt_name)
							break

					elif pot_opt_name == "bed side":
						side_opt_idx = 1
						for code in opt_codes[side_opt_idx]:
							#print("Option Name Code: " + code)
							#print("Does " + item_name + " contain " + code + "?")
							if re.search(code, item_name):
								#print("Code found in Item Name")
								valid_option = True
								break
							#else:
								#print("No Code in Item Name")
						if valid_option:
							#print("We know this is a valid option because we found a keyword in one of the items.")
							valid_opt_names.append(pot_opt_name)
							break

		elif type == "dressers":
			#potential_opt_names = all_pot_opt_names[2]

			# variant options: width
			widths = [ "120 cm", "150 cm" ]
			width_codes = [ "120 dr", "150 dr" ]
			opt_codes.append(width_codes)
			width_code = ''

			# only loop through nightstand items
			dr_item_names = isolate_items_of_type(type, item_names)

			for pot_opt_name in potential_opt_names:
				valid_option = False
				for item_name in dr_item_names:
					if pot_opt_name == "width":
						width_opt_idx = 0 # first option in list of options
						for code in opt_codes[width_opt_idx]:
							if re.search(code, item_name):
								valid_option = True
								break
						if valid_option:
							valid_opt_names.append(pot_opt_name)
							break
	else:
		print("Catalog Reader cannot determine valid options for products of type " + type + ".\n")

	if len(valid_opt_names) != 0:
		print("Valid Option Names: " + str(valid_opt_names) + "\n")
	else:
		print("No valid Options for this Collection.")
		display_collection_name(collection)


	print("\n=== Determined Valid Options ===\n")

	return valid_opt_names

def isolate_items_of_type(product_type, all_item_names):
	type_item_names = []
	type_keywords = product.read_keywords(product_type)

	for item_name in all_item_names:
		for key in type_keywords:
			if re.search(key, item_name):
				type_item_names.append(item_name)
				break

	return type_item_names

# see what values are actually included in this option for this collection, out of all possible values for this option for this product type
def determine_option_values(collection, type, opt_names):

	print("\n=== Determine Option Values ===\n")

	opt_values = []

	valid_opt_values = []

	opt_codes = []

	#bs_potential_sizes = [ 'king', 'queen' ]
	#ns_potential_sizes = [ "2 drawer", "3 drawer" ]
	#all_potential_sizes = [ bs_potential_sizes, ns_potential_sizes ]
	all_potential_sizes = {"bedroom sets": [ 'king', 'queen' ], "nightstands": [ "2 drawer", "3 drawer" ]}

	all_potential_widths = {"dressers": [ '120 centimeter', '150 centimeter' ]}

	potential_options = []

	if type in all_potential_sizes:
		potential_sizes = all_potential_sizes[type]

		if type == "bedroom sets":
			# variant options: either size or side
			#potential_sizes = all_potential_sizes[0]
			potential_options.append(potential_sizes)
			size_codes = [ 'ks', 'qs' ]
			size_code = ''

			opt_codes.append(size_codes)

			valid_opt_values = check_all_options_for_values(collection, opt_codes, opt_names, potential_options)

		elif type == "nightstands":

			# variant options: either size or side
			#potential_sizes = all_potential_sizes[1]
			potential_options.append(potential_sizes)
			size_codes = [ "2 dr", "3 dr" ]
			opt_codes.append(size_codes)

			potential_sides = ["left", "right"]
			potential_options.append(potential_sides)
			side_codes = potential_sides
			opt_codes.append(side_codes)

			valid_opt_values = check_all_options_for_values(collection, opt_codes, opt_names, potential_options)

	if type in all_potential_widths:
		potential_widths = all_potential_widths[type]

		if type == "dressers":
			# variant options: width
			#potential_widths = dr_potential_widths
			potential_options.append(potential_widths)
			width_codes = [ "120 dr", "150 dr" ]
			opt_codes.append(width_codes)

			valid_opt_values = check_all_options_for_values(collection, opt_codes, opt_names, potential_options)

	if len(valid_opt_values) != 0:
		print("Valid Option Values: " + str(valid_opt_values) + "\n")
	else:
		print("No valid values in this Option for this Collection.")
		display_collection_name(collection)

	print("\n=== Determined Option Values ===\n")

	return valid_opt_values

def check_all_options_for_values(collection, opt_codes, opt_names, potential_options):

	valid_opt_values = []

	item_names = determine_item_names(collection)

	current_opt_values = []

	for opt_name in opt_names:
		#print("Option Name: " + opt_name)

		if opt_name.lower() == "size":
			print("Determine Values for Size Option.")
			opt_idx = 0
		if opt_name.lower() == "width":
			print("Determine Values for Width Option.")
			opt_idx = 0
		elif opt_name.lower() == "bed side":
			print("Determine Values for Bed Side Option.")
			opt_idx = 1
		else:
			continue

		current_codes = opt_codes[opt_idx]
		current_pot_opts = potential_options[opt_idx]

		current_opt_values = isolate_option_values(item_names, current_codes, current_pot_opts)

		valid_opt_values.append(current_opt_values)

	return valid_opt_values

def isolate_option_values(item_names, value_codes, potential_options):

	valid_value = False

	current_opt_values = []

	for code_idx in range(len(value_codes)):
		code = value_codes[code_idx]
		#print("Option Value Code: " + code)
		for item_name in item_names: # formerly checking all codes for each name, but need to check all names for each code to ensure max options is max codes
			#print("Item Name: " + item_name)
			#print("Does " + item_name + " contain " + code + "?")
			if re.search(code, item_name):
				#print("yes, the code is found")
				#print("We know this is a valid option Value because we found a keyword in one of the items.")
				valid_value = True
				break
			#else:
				#print("no, the code is not found")
		if valid_value:
			option = potential_options[code_idx]
			print("Valid Option: " + option)
			current_opt_values.append(option)
			continue

	return current_opt_values

def display_collection_name(collection):
	set_row_idx = 0
	item_name_idx = 0
	collection_name = collection[set_row_idx].split("\t")[item_name_idx]
	print("Collection Name: " + collection_name + "\n")

# special function to determine item names because the name field is at a different index for different row types
def determine_item_names(collection):

	#print("\n=== Determine Item Names ===\n")

	display_collection_name(collection)

	item_name = ''
	item_names = []

	item_name_idx = 0

	current_row_idx = 0
	for item in collection:
		if current_row_idx != 0:
			item_name_idx = 1

		item_values = item.split("\t")
		potential_item_name = item_values[item_name_idx]

		if catalog.determine_special_order(potential_item_name):
			item_name_idx = 0
			item_name = item_values[item_name_idx]
		else:
			item_name = potential_item_name

		#print("Item " + str(current_row_idx) + " Name: " + item_name)

		item_name = re.sub('[\.]', '', item_name)
		item_name = re.sub('[,]', '', item_name)

		item_names.append(item_name.lower())

		current_row_idx += 1

	#print("\n=== Determined Item Names ===\n")

	return item_names

def determine_item_name(collection, item_idx, vndr):
	item_name = ''

	if vndr == "ESF":
		item_name_idx = 1
		if item_idx == 0:
			item_name_idx = 0

		item_values = collection[item_idx].split("\t")
		potential_item_name = item_values[item_name_idx]

		if catalog.determine_special_order(potential_item_name):
			item_name_idx = 0
			item_name = item_values[item_name_idx]
		else:
			item_name = potential_item_name

	elif vndr == "Aico":
		item_name_idx = 1

		item_values = collection[item_idx].split("\t")

		item_name = item_values[item_name_idx]

	#print("Item " + str(current_row_idx) + " Name: " + item_name)

	item_name = re.sub('[\.]', '', item_name)
	item_name = re.sub('[,]', '', item_name)

	return item_name.lower()

def isolate_variant_options(variant_option_names, variant_values):

	print("\n=== Isolate Variant Options ===\n")

	variant_options = []
	opt_names = []
	opt_values = []

	if len(variant_values) > 0:
		for value_set_idx in range(len(variant_values)):

			current_opt_values = variant_values[value_set_idx]

			for current_value_idx in range(len(current_opt_values)):

				print("Name: " + variant_option_names[value_set_idx] + ", Value: " + current_opt_values[current_value_idx] + "\n")
				opt_names.append(variant_option_names[value_set_idx])
				opt_values.append(current_opt_values[current_value_idx])

				#print("Current value index: " + str(current_value_idx))
				current_value_num = current_value_idx + 1
				print("Current value number: " + str(current_value_num))
				print("Number of values: " + str(len(current_opt_values)))

				print()

		variant_options.append(opt_names)
		variant_options.append(opt_values)
	else:
		print("No Variant Options to Isolate")

	print("\n=== Isolated Variant Options ===\n")

	return variant_options

# return each item in the variant, for all variants
def isolate_variants(collection, type, valid_opt_names, previous_skus):

	print("\n=== Isolate Variants ===\n")

	room_set_row_idx = 0
	room_set_row = collection[room_set_row_idx].split("\t")

	variants = []
	variant_items = [] # if including bundle row [ room_set_row ]

	#bs_sizes = [ 'king', 'queen' ]
	#ns_sizes = [ "2 drawer", "3 drawer" ]
	#all_sizes = [ bs_sizes, ns_sizes ]
	all_sizes = {"bedroom sets": [ 'king', 'queen' ], "nightstands": [ "2 drawer", "3 drawer" ]}

	#bs_size_codes = [ 'ks', 'qs' ]
	#ns_size_codes = [ "2 dr", "3 dr" ]
	#all_size_codes = [ bs_size_codes, ns_size_codes ]
	all_size_codes = {"bedroom sets": [ 'ks', 'qs' ], "nightstands": [ "2 dr", "3 dr" ]}

	#dr_widths = [ '120 centimeter', '150 centimeter' ]
	all_widths = {"dressers":[ '120 centimeter', '150 centimeter' ]}
	#dr_width_codes = [ '120 dr', '150 dr' ]
	all_width_codes = {"dressers":[ '120 dr', '150 dr' ]}

	# keywords multiple set types can use
	type_keywords = product.read_keywords(type)

	if type in all_sizes:
		sizes = all_sizes[type]
		size_codes = all_size_codes[type]
		size_code = ''

		if type == "bedroom sets":
			print("\n=== Make Variant for Bedroom Set ===\n")

			# variant options
			#sizes = all_size[0]
			#size_codes = all_size_codes[0]

			for opt_idx in range(len(sizes)):
				variant_items = [ room_set_row ] # very important to reset this between options if including the bundle row in the variant

				size_code = size_codes[opt_idx]
				size = sizes[opt_idx]

				valid_size = False

				# bed parts
				wsf_key1 = "wooden slat frame " + size
				wsf_key2 = "wooden slats frame " + size
				wsf_key3 = size_code + " wooden slat"
				wsf_keywords = [ wsf_key1, wsf_key2, wsf_key3 ]
				for key in wsf_keywords:
					wsf_item = isolate_collection_item(collection, key)
					if wsf_item:
						variant_items.append(wsf_item)
						valid_size = True
						break

				platform_keyword = "platform " + size_code
				platform_item = isolate_collection_item(collection, platform_keyword)
				if platform_item:
					variant_items.append(platform_item)

					hb_keyword = "h/b\s*" + size_code
					hb_item = isolate_collection_item(collection, hb_keyword)
					if hb_item:
						variant_items.append(hb_item)
						valid_size = True
				else: # if no platform item, there should be bed item
					bed_key1 = size_code + " bed"
					bed_key2 = size + " size bed"
					bed_key3 = "bed " + size_code
					bed_keywords = [ bed_key1, bed_key2, bed_key3 ]
					for key in bed_keywords:
						bed_item = isolate_collection_item(collection, key)
						if bed_item:
							variant_items.append(bed_item)
							valid_size = True
							break

				# bedroom parts

				if valid_size:
					for key in type_keywords:
						nightstand_item = isolate_collection_item(collection, key)
						if nightstand_item:
							variant_items.append(nightstand_item)
							break

					dresser_keyword = "dresser"
					dresser_item = isolate_collection_item(collection, dresser_keyword)
					if dresser_item:
						variant_items.append(dresser_item)

					mirror_keyword = "mirror"
					mirror_item = isolate_collection_item(collection, mirror_keyword)
					if mirror_item:
						variant_items.append(mirror_item)

					variants.append(variant_items)

				print("\n=== Made Variant for Bedroom Set ===\n")

		elif type == "wardrobes":
			print("\n=== Wardrobe Has 1 Variant ===\n")
			for item in collection[1:]:
				wardrobe_item = item.split("\t")
				if wardrobe_item:
					variant_items.append(wardrobe_item)

			variants.append(variant_items)

		elif type == "dresser-chest sets":
			print("\n=== Dresser-Chest Set Has 1 Variant ===\n")
			for item in collection[1:]:
				dc_item = item.split("\t")
				if dc_item:
					variant_items.append(dc_item)

			variants.append(variant_items)
		elif type == "nightstands":
			print("\n=== Make Variant for Nightstands ===\n")

			# variant options: either size or side
			#sizes = all_sizes[1]
			#size_codes = all_size_codes[1]

			sides = ["left","right"]
			side_codes = sides

			size_code = side_code = ''
			size_option = side_option = False

			valid_variant = True

			# we know that if the set includes a left and right night stand, it should have that 1 variant
			# if those also have size options, there would be the 2 variants that would affect both nightstands

			# assumption: if left/right options, then no size option

			# if one of the valid option names is size, then we know there is a size option with at least 1 variant
			for v_opt_name in valid_opt_names:
				print("Valid Option Name: " + v_opt_name)
				if re.search("size", v_opt_name):
					print("Size Option Found")
					size_option = True
					continue
				else:
					print("Size Option Not Found")

				if re.search("side", v_opt_name):
					print("Side Option Found")
					side_option = True
					continue
				else:
					print("Side Option Not Found")

			if size_option:
				print("Size Option found while Isolating Variants")
				for opt_idx in range(len(sizes)):
					valid_variant = True
					variant_items = [] # very important to reset this between options

					size_code = size_codes[opt_idx]
					size = sizes[opt_idx]
					print("Check size: " + size)

					ns_keyword = size_code # only size code b/c no variants of product type as with bed set
					print("Nightstand Keyword: " + ns_keyword)

					ns_item = isolate_collection_item(collection, ns_keyword)
					if ns_item:
						variant_items.append(ns_item)
						valid_variant = True
					else:
						valid_variant = False

					if valid_variant:
						print("Add variant to list of variants for this collection.")
						variants.append(variant_items)
			if side_option:
				print("Side Option found while Isolating Variants")
				for opt_idx in range(len(sides)):
					valid_variant = True
					variant_items = [] # very important to reset this between options

					side_code = side_codes[opt_idx]
					side = sides[opt_idx]
					print("Check side: " + side)

					ns_keyword = side_code # only side code b/c no variants of product type as with bed set
					print("Nightstand Keyword: " + ns_keyword)

					ns_item = isolate_collection_item(collection, ns_keyword)
					if ns_item:
						variant_items.append(ns_item)
						valid_variant = True
					else:
						valid_variant = False

					if valid_variant:
						print("Add variant to list of variants for this collection.")
						variants.append(variant_items)
			else: # should be a single nightstand in the collection, so double it only if it is a set
				for key in type_keywords:
					ns_item = isolate_collection_item(collection, key)
					if ns_item:
						variant_items.append(ns_item)
						#variant_items.append(ns_item) # double append b/c we know it is a set of 2 nightstands
						break
				variants.append(variant_items)

	if type in all_widths:
		widths = all_widths[type]
		width_codes = all_width_codes[type]
		width_code = ''

		width_option = False

		valid_variant = True

		for v_opt_name in valid_opt_names:
			print("Valid Option Name: " + v_opt_name)
			if re.search("width", v_opt_name):
				print("Width Option Found")
				width_option = True
				continue
			else:
				print("Width Option Not Found")

		if type == "dressers":
			print("\n=== Make Variant for Dressers ===\n")
			# variant options: width
			#widths = dr_widths
			#width_codes = dr_width_codes

			if width_option:
				print("Width Option found while Isolating Variants")
				for opt_idx in range(len(widths)):
					valid_variant = True
					variant_items = [] # very important to reset this between options

					width_code = width_codes[opt_idx]
					width = widths[opt_idx]
					print("Check size: " + width)

					dr_keyword = width_code # only size code b/c no variants of product type as with bed set
					print("Dresser Keyword: " + dr_keyword)

					dr_item = isolate_collection_item(collection, dr_keyword)
					if dr_item:
						variant_items.append(dr_item)
						valid_variant = True
					else:
						valid_variant = False

					if valid_variant:
						print("Add variant to list of variants for this collection.")
						variants.append(variant_items)

	else:
		if type == "mirrors":
			print("\n=== Make Variant for Mirror ===\n")

			valid_variant = True
			variant_items = [] # very important to reset this between options

			for key in type_keywords:
				print("Mirror Keyword: " + key)

				mirror_item = isolate_collection_item(collection, key)
				if mirror_item:
					if catalog.determine_unique_sku(product.get_sku(mirror_item),previous_skus):
						print("Unique SKU found while making mirror variant")
						variant_items.append(mirror_item)
						valid_variant = True
						break # okay to break b/c should be only 1 item in variant
				else:
					valid_variant = False

			if valid_variant:
				print("Add variant to list of variants for this collection.")
				variants.append(variant_items)
		elif type == "chests":
			print("\n=== Make Variant for Chest ===\n")

			valid_variant = True
			variant_items = [] # very important to reset this between options

			for key in type_keywords:
				print("Chest Keyword: " + key)

				mirror_item = isolate_collection_item(collection, key)
				if mirror_item:
					variant_items.append(mirror_item)
					valid_variant = True
				else:
					valid_variant = False

			if valid_variant:
				print("Add variant to list of variants for this collection.")
				variants.append(variant_items)
		elif type == "dining sets":
			print("\n=== Make Variant for Dining Room Set ===\n")
			# variant options
			room_configurations = [ "Table + 4 Chairs", "Table + 4 Chairs + Buffet" ]

			for opt_idx in range(len(room_configurations)):
				valid_variant = True
				variant_items = [ room_set_row ] # very important to reset this between options

				# dining room parts
				table_keyword = "table"
				table_item = isolate_collection_item(collection, table_keyword)
				if table_item:
					variant_items.append(table_item)

				chair_keyword = "chair"
				chair_item = isolate_collection_item(collection, chair_keyword)
				if chair_item:
					variant_items.append(chair_item)

				if re.search("buffet", room_configurations[opt_idx].lower()):
					buffet_keyword = "chair"
					buffet_item = isolate_collection_item(collection, buffet_keyword)
					if buffet_item:
						variant_items.append(buffet_item)
					else:
						valid_variant = False

				if valid_variant:
					variants.append(variant_items)
		elif type == "living room sets":
			print("\n=== Make Variant for Living Room Set ===\n")

			# variant options
			room_configuration = "Sectional + Chair + Ottoman"

			# living room parts
			sectional_keyword = "sectional"
			sectional_item = isolate_collection_item(collection, sectional_keyword)
			if sectional_item:
				variant_items.append(sectional_item)

			chair_keyword = "chair"
			chair_item = isolate_collection_item(collection, chair_keyword)
			if chair_item:
				variant_items.append(chair_item)

			ottoman_keyword = "ottoman"
			ottoman_item = isolate_collection_item(collection, ottoman_keyword)
			if ottoman_item:
				variant_items.append(ottoman_item)

			variants.append(variant_items)

			print("\n=== Made Variant for Living Room Set ===\n")

		elif type == "wall units":
			print("\n=== Make Variant for Wall Unit ===\n")
		elif type == "sectionals":
			print("\n=== Make Variant for Sectional ===\n")
		elif type == "chairs":
			print("\n=== Make Variant for Chair ===\n")

		else:
			print("\nUnrecognized Product Type\n")

	for variant in variants:
		item_idx = 0
		for item in variant:
			print("Item " + str(item_idx) + ": " + str(item))
			item_idx += 1
		print()

	print("\n=== Isolated Variants ===\n")

	return variants

def determine_already_isolated(current_item,previous_item):
	already_isolated = False
	if product.get_sku(current_item) == product.get_sku(previous_item):
		already_isolated = True

	return already_isolated

def isolate_collection_item(collection, keywords):

	print("\n=== Isolate Collection Item ===\n")

	isolated_item = False

	item_values = []
	item_name_idx = 1

	print("Item Keyword: " + keywords)

	special_key = "special order"
	current_row_idx = 0
	for item in collection[1:]: # do not include room set row b/c may contain keywords used to identify variant items (eg sectional)
		item_name = ''

		item_values = item.split("\t")
		potential_item_name = re.sub('[\.]', '', item_values[item_name_idx])
		potential_item_name = re.sub('[,]', '', potential_item_name)
		#print("Item " + str(current_row_idx) + " Name: " + item_name)

		# if special order is in the potential item name, that means the actual item name is shifted 1 to the left
		if catalog.determine_special_order(potential_item_name): #
			item_name_idx = 0
			item_name = re.sub('[\.]', '', item_values[item_name_idx])
			item_name = re.sub('[,]', '', item_name)
			item_name_idx = 1 # item name index has to go back to 1 for initial check of potential name
		else:
			item_name = potential_item_name

		print("Item Name: " + item_name)

		if re.search(keywords, item_name.lower()): #if keywords in item_name.lower():
			isolated_item = True
			print("\nIsolated Item " + str(current_row_idx) + " Name: " + item_name)
			break

		current_row_idx += 1

	if isolated_item == False:
		item_values = []
		print("\nno match")

	print("\n=== Isolated Collection Item ===\n")

	return item_values

def arrange_headers(fields):
	headers = ""
	for field in fields:
		headers += "\"" + field + "\""
		#print("field: " + field + ", fields[-1]: " + fields[-1])
		if field != fields[-1]:
			headers += ","

	#print(headers)
	return headers

# each input value must be surrounded by quotes
def read_collection(filename):

	print("=== Read Collection: " + filename.replace("../Data/", "") + " ===\n")

	collection = [] # initialize array to hold rows in collection table

	with open(filename, encoding="utf8") as collection_file:
		next(collection_file) # cast 1st line into oblivion

		current_line = ""
		current_row = 1
		for collection_info in collection_file:
			collection_info = collection_info.strip()

			current_line += collection_info
			# if the line ends with a quotation mark, we know it is the end of the row
			if "\"" in collection_info[-1:]:
				#print("Row " + str(current_row) + ":\t" + current_line + "\n")
				collection.append(current_line)
				current_line = ""
			else:
				pass

			current_row += 1

		collection_file.close()

	print("\n=== End Collection: " + filename.replace("../Data/", "") + " ===\n\n")

	return collection

def isolate_category(collection):
	# isolate first category

	print("=== Isolate Category ===")
	category_rows = []

	product_counts = isolate_collection_field(collection, "products count")
	#print("product_counts: " + str(product_counts))

	category_start_idx = 1
	category_stop_idx = int(product_counts[category_start_idx-1])
	#print("category_stop_idx: " + str(category_stop_idx))

	for row_idx in range(category_stop_idx):
		category_rows.append(collection[row_idx])

	return category_rows

def isolate_category_from_collection(collection, start_idx, stop_idx):
	# isolate first category
	category_rows = []

	for row_idx in range(start_idx, stop_idx):
		category_rows.append(collection[row_idx])

		#if row_idx == start_idx or row_idx == stop_idx:
			#print("Row " + str(row_idx) + ":\t" + collection[row_idx] + "\n")

	print()

	return category_rows

def isolate_categories(collection):

	print("=== Isolate Categories ===\n")

	categories = []

	#product_counts = isolate_collection_field(collection, "products count")
	#print("product_counts: " + str(product_counts))

	collection_handles = np.array(isolate_collection_field(collection, "handle"))

	_, idx, cnt = np.unique(collection_handles, return_index=True, return_counts=True)

	unique_category_handles = collection_handles[np.sort(idx)]
	counts = cnt[np.argsort(idx)]
	indices = np.sort(idx)

	#unique_category_handles = collection_handles[np.sort(idx)]
	print("Unique Category Handles: " + str(unique_category_handles))

	#unique_category_handles, indices, counts = count_categories(collection)

	num_categories = len(unique_category_handles)
	print("Number of Categories:\t" + str(num_categories) + "\n")

	print("Number of Rows per Category: ")
	for category_idx in range(num_categories):
		print(unique_category_handles[category_idx] + ": " + str(counts[category_idx]))
	print()

	print("Indices of Category: ")
	for category_idx in range(num_categories):
		print(unique_category_handles[category_idx] + ": " + str(indices[category_idx]))
	print()



	for category_idx in range(num_categories):
		category_start_idx = indices[category_idx]
		#print("category_start_idx: " + str(category_start_idx))
		category_stop_idx = category_start_idx + counts[category_idx]
		#print("category_stop_idx: " + str(category_stop_idx))

		#print("Category:\n Handle: " + unique_category_handles[category_idx] + ",\n Rows: [ " + str(category_start_idx) + ", " + str(category_stop_idx) + " )\n")
		category_rows = isolate_category_from_collection(collection, category_start_idx, category_stop_idx)

		category_start_idx = category_stop_idx

		categories.append(category_rows)

		if category_start_idx > len(collection) - 1:
			break

	print("\n=== End Isolate Categories ===\n\n")

	return categories

def count_categories(collection):

	collection_handles = isolate_collection_field(collection, "handle")

	return np.unique(collection_handles, return_index=True, return_counts=True)

# can use for exported Products, Smart Collections, and probably others but untested
def isolate_collection_field(collection, field_title):

	print("=== Isolate Collection Field: " + field_title + " ===\n")

	collection_field_values = []

	# need to know order of data fields
	handle_idx = 1
	products_count_idx = 15
	product_id_idx = 22
	product_handle_idx = 23

	# set default values
	default_idx = handle_idx
	default_idx_start = product_id_idx
	default_idx_stop = product_handle_idx + 1

	# set init column idx to default
	column_idx = default_idx
	column_idx_start = default_idx_start
	column_idx_stop = default_idx_stop

	category_start_idx = 0

	for row_idx in range(len(collection)):
		#print("original collection row: " + collection[row_idx])

		init_collection_row = format_collection_row(collection, row_idx)

		if field_title == "handle":
			column_idx = handle_idx
			handle = init_collection_row[column_idx]
			collection_field_values.append(handle)

			#print("Handle:\t" + handle)

		elif field_title == "products count":
			column_idx = products_count_idx
			products_count = init_collection_row[column_idx]
			collection_field_values.append(products_count)

			#print("Products Count:\t" + products_count)

		elif field_title == "linked products":


			column_idx_start = product_id_idx
			column_idx_stop = product_handle_idx + 1

			#print("Linked Product Handle:\t" + init_collection_row[product_handle_idx])

			linked_product = init_collection_row[column_idx_start:column_idx_stop]
			collection_field_values.append(linked_product)

			#print("Linked Product:\t" + str(linked_product))

		else:
			print("unrecognized field title parameter")

	print("\n=== End Collection Field: " + field_title + " ===\n\n")

	return collection_field_values

def format_collection_row(collection, idx):
	row = collection[idx].split("\",")
	for field_idx in range(len(row)):
		row[field_idx] = row[field_idx].replace("\"", "")

	return row
	#print("init_collection_info: " + str(init_collection_info))

def sort_linked_products(init_linked_products, product_handles, sort_value):

	print("=== Sort Linked Products ===\n")

	linked_products = init_linked_products
	#print("linked_products: " + str(linked_products))

	for linked_product in linked_products:

		linked_product_id = linked_product[0]
		linked_product_handle = linked_product[1]
		#print("linked_product_handle: \"" + linked_product_handle + "\"")

		linked_product_value = ""
		for product_handle in product_handles:
			if product_handle == linked_product_handle:
				linked_product_value = sort_value
				break

		# look for mstar, and if found move item to the top of the list
		if linked_product_value == sort_value:
			#print(linked_product_handle + ": Mstar")
			# put product in position 1 of collection and shift other products to fill the empty space
			linked_product.append("Mstar")
			linked_products.insert(0, linked_products.pop(linked_products.index(linked_product)))
		else:
			linked_product.append("not Mstar")

	#for linked_product in linked_products:
		#print("Sorted Linked Product:\t" + linked_product[1])

	print("\n=== End Linked Products ===\n\n")

	return linked_products

# gather info for sorted category from different sources and format uniformly for import
def arrange_collection(collection, linked_products):
	# replace original linked product fields with sorted version

	print("=== Arrange Collection ===\n")

	print("Length of Collection: " + str(len(collection)) + "\n")

	categories = []

	for row_idx in range(len(collection)):
		#print("Row: " + str(row_idx))

		init_collection_row = format_collection_row(collection, row_idx)

		# unchanged collection info
		collection_id = init_collection_row[0]
		collection_handle = init_collection_row[1]
		collection_command = init_collection_row[2]
		collection_title = init_collection_row[3]
		collection_sort_order = init_collection_row[5]
		collection_published = init_collection_row[8]
		collection_match = init_collection_row[18]
		collection_rule_product_column = init_collection_row[19]
		collection_rule_relation = init_collection_row[20]
		collection_rule_condition = init_collection_row[21]

		# sorted linked product info
		linked_product_id = linked_products[row_idx][0]
		linked_product_handle = linked_products[row_idx][1]
		linked_product_vendor = linked_products[row_idx][2]

		# unchanged linked product position order b/c id and handle shifted instead
		linked_product_position = init_collection_row[24]

		sorted_category_info = "\"" + collection_id + "\",\"" + collection_handle + "\",\"" + collection_command + "\",\"" + collection_title + "\",\"" + collection_sort_order + "\",\"" + collection_published + "\",\"" + collection_match + "\",\"" + collection_rule_product_column + "\",\"" + collection_rule_relation + "\",\"" + collection_rule_condition + "\",\"" + linked_product_id + "\",\"" + linked_product_handle + "\",\"" + linked_product_position + "\""

		sorted_products = linked_product_handle + ", " + linked_product_vendor
		#print("Row " + str(row_idx) + ": " + sorted_products)

		categories.append(sorted_category_info)

	print("\n=== End Collection ===\n\n")

	return categories

def set_disco_prices(collection_row):

	disco_prices = []

	# set variant price and compare price, if field not empty string
	if collection_row[33] != "":
		init_variant_price = collection_row[33]
	else:
		print("Alert! Variant price appears to be set to 0! Correct price immediately!")
	init_variant_compare_price = collection_row[34] if collection_row[34] != "" else "0"

	disco_price = init_variant_compare_price if float(init_variant_compare_price) > float(init_variant_price) else init_variant_price
	disco_compare_price = ""

	disco_prices.append(disco_price)
	disco_prices.append(disco_compare_price)

	return disco_prices

def set_disco_vendor(collection_row):

	disco_vendor = ""
	disco_vendor_suffix = "-Dropped"

	# alter vendor if not already set to "Dropped" version
	if collection_row[5].endswith(disco_vendor_suffix):
		init_product_vendor = collection_row[5].split("-")
		if len(init_product_vendor) > 2:
			disco_vendor = init_product_vendor[0] + disco_vendor_suffix
		else:
			disco_vendor = collection_row[5]
	else:
		disco_vendor = collection_row[5] + disco_vendor_suffix

	return disco_vendor

def set_disco_tags(collection_row, disco_date):
	# alter tags
	disco_tags = collection_row[7]
	disco_date_metrics = ["year", "month", "day of month", "day of week"]
	# =======get date values from calendar=======
	disco_date_values = [disco_date.year, disco_date.month, disco_date.day, disco_date.strftime("%A")]
	for index in range(len(disco_date_metrics)):
		disco_date_tag = "discontinued-" + disco_date_metrics[index] + "-" + str(disco_date_values[index])
		disco_tags += ", " + disco_date_tag
	#print("tags: " + disco_tags)

	return disco_tags

def change_product_properties(init_products, init_properties, action, value):
	pass


def arrange_products(init_products, changed_properties, change_property):

	print("=== Arrange Products ===\n")

	print("Length of Collection: " + str(len(init_products)) + "\n")

	products = []

	current_date = datetime.datetime.now()

	for row_idx in range(len(init_products)):

		init_collection_row = format_collection_row(init_products, row_idx)

		# unchanged product info
		product_id = init_collection_row[0]
		product_handle = init_collection_row[1]
		product_title = init_collection_row[3]

		# changed product info
		product_command = ""
		product_vendor = ""
		product_type = ""
		product_tags = ""
		product_tags_command = ""
		product_var_inv_tracker = ""
		product_var_inv_qty = ""

		# generally unchanged variant info, needed for Excelify import
		variant_inv_item_id = init_collection_row[18]
		variant_id = init_collection_row[19]
		variant_command = init_collection_row[20]
		option1_name = init_collection_row[21]
		option1_value = init_collection_row[22]
		option2_name = init_collection_row[23]
		option2_value = init_collection_row[24]
		option3_name = init_collection_row[25]
		option3_value = init_collection_row[26]

		variant_price = variant_compare_price = ""
		variant_prices = [variant_price, variant_compare_price]
		if change_property == "discontinue":
			variant_prices = set_disco_prices(init_collection_row)

			product_vendor = set_disco_vendor(init_collection_row)

			product_command = "UPDATE"

			product_type = "DISCONTINUED"

			product_tags = set_disco_tags(init_collection_row, current_date)

			product_tags_command = "REPLACE"

			product_var_inv_tracker = "shopify"

			product_var_inv_qty = "0"

		elif change_property == "tags":

			product_tags = changed_properties

		if len(variant_prices) == 2:
			variant_price = variant_prices[0]
			variant_compare_price = variant_prices[1]
		else:
			print("Warning: Variant price and compare price not set.")

		changed_product_info = "\"" + product_id + "\",\"" + product_handle + "\",\"" + product_command + "\",\"" + product_title + "\",\"" + product_vendor + "\",\"" + product_type + "\",\"" + product_tags + "\",\"" + product_tags_command + "\",\"" + variant_price + "\",\"" + variant_compare_price + "\",\"" + product_var_inv_tracker + "\",\"" + product_var_inv_qty + "\",\"" + variant_inv_item_id + "\",\"" + variant_id + "\",\"" + variant_command + "\",\"" + option1_name + "\",\"" + option1_value + "\",\"" + option2_name + "\",\"" + option2_value + "\",\"" + option3_name + "\",\"" + option3_value + "\""

		products.append(changed_product_info)

	print("\n=== End Products ===\n\n")

	return products

def write_collection(collection, category_handle, collection_headers):

	import_type = "Smart-Collections-sorted" if collection_headers[-1] == "Product: Position" else "Products-changed"
	category_filename = "../Data/" + category_handle.lower() + "-" + import_type + "-import.csv"
	category_file = open(category_filename, "w", encoding="utf8") # overwrite existing content

	collection_headers = arrange_headers(collection_headers)

	category_file.write(collection_headers)
	category_file.write("\n")
	#print(collection_headers)

	for row_idx in range(len(collection)):
		#print(sorted_category_info + "\n")
		category_file.write(collection[row_idx])
		category_file.write("\n")
		#print(collection[row_idx])

	category_file.close()
