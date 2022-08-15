# catalog.py
# functions for a catalog,
# such as read catalog, isolate fields, extract data for manipulation
# read catalogs from different vendors, b/c they come in different formats

import product

#======ESF=====
# read from csv [ "Code", "Name", "Description 2", "Price", "MAP price", "Default set qts", "Width", "Depth", "Height", "Weight", "Volume", "Manufacturer", "Category Type", "Stock Status", "New Arrivals", "Parent Category", "Category", "Refine Categories", "Image 1"]

def display_headers(vndr):

	print("=== Display Headers ===\n")

	catalog_headers = extract_catalog_headers(vndr)

	print(catalog_headers)

	print("=== Display Headers ===\n")

def display_data(vndr):

	print("=== Display Data ===\n")

	catalog_data = extract_catalog_data(vndr)

	print(catalog_data)

	print("=== Display Data ===\n")

def display_row(vndr, rwnm):

	print("=== Display Row " + str(rwnm) + " ===\n")

	catalog_row = extract_catalog_row(vndr, rwnm)

	print("Row " + str(rwnm) + ": " + str(catalog_row))

	print("=== Display Row " + str(rwnm) + " ===\n")

# display whole catalog, including headers
def display_catalog(vndr):

	print("=== Display Catalog ===\n")

	catalog_data = extract_catalog(vndr)

	print(catalog_data)

	print("=== Display Catalog ===\n")

def extract_catalog_headers(vndr):

	print("=== Extract Catalog Headers ===\n")

	catalog_filename = "../Data/" + vndr + "-catalog-sample.csv"

	catalog_headers = []

	with open(catalog_filename, encoding="UTF8") as catalog_file:

		current_line = ""
		for catalog_info in catalog_file:
			current_line = catalog_info.strip()
			catalog_headers.append(current_line)
			break

		catalog_file.close()

	print("=== Extract Catalog Headers ===\n")

	return catalog_headers

def extract_catalog_data(vndr):

	print("=== Extract Catalog Data ===\n")

	catalog_rows = split_catalog_rows(vndr)

	print("=== Extract Catalog Data ===\n")

	return catalog_headers

def extract_catalog_row(vndr, rwnm):

	print("=== Extract Catalog Row " + str(rwnm) + " ===\n")

	catalog_rows = split_catalog_rows(vndr)

	catalog_row = catalog_rows[rwnm-2]

	print("=== Extract Catalog Row " + str(rwnm) + " ===\n")

	return catalog_row

def split_catalog_rows(vndr):

	print("=== Split Catalog Rows ===\n")

	catalog_lines = split_catalog_lines(vndr)

	rows = []

	# remove blank lines so lines with text are compacted
	# compact_lines = []
	# for line in catalog_lines:
	# 	if line != '':
	# 		compact_lines.append(line)
	# 	else:
	# 		pass

	line_num = 1
	current_info = ""
	previous_info = ""
	for line in catalog_lines:
		if line_num != 1:
			new_row = determine_new_row(line, line_num, vndr)
			if new_row:
				# continue adding lines to current info string until next new line found
				if current_info != "":

					print("\nPrevious Row: " + current_info + "\n")

					rows.append(current_info)
					current_info = ""

			elif line != '': # if new line but not new row, add period and space if not already
				line = line + ". "

			current_info += line

		line_num += 1

	print("=== Split Catalog Rows ===\n")

	return rows

def split_catalog_lines(vndr):

	print("=== Split Catalog Lines ===\n")

	catalog_filename = "../Data/" + vndr + "-catalog-sample.csv"

	lines = []

	with open(catalog_filename, encoding="UTF8") as catalog_file:

		current_line = ""
		for catalog_info in catalog_file:
			current_line = catalog_info.strip()
			lines.append(current_line)

		catalog_file.close()

	# line_num = 1
	# for line in lines:
	# 	print(str(line_num) + ": " + line + "\n")
	#
	# 	line_num += 1

	print("=== Split Catalog Lines ===\n")

	return lines

def determine_new_row(ln, lnnm, vndr):
	new_row = False

	# How to recognize when you have come to the end of a row in the ESF catalog?
	# Could check next line to see if first column is blank or all caps?
	# I know where the first row ends and the second begins b/c I know that the next row first cell is all caps. Plus the last entry in the row is a Finish, which has finite variations.
	# Problem is not all rows begin with all caps, so need exception rule.
	# Code field (column 1) is blank for Sets and Special Order items
	# the only field that uses multiple lines is the description field, so we could isolate that field to separate rows
	# when you come to the end of a line, check the first few letters of the next line. If they are all caps, then start a new row.
	if vndr == "ESF":
		blank_line = False
		blank_code = False
		uppercase_code = False

		# if first value in line is all caps, or only first value in line is blank, consider this new row
		print(str(lnnm) + ": " + ln + "\n")

		print("Is line " + str(lnnm) + " the start of a new row?")

		print("Is line " + str(lnnm) + " blank?")
		if ln == "":
			print("Yes, line " + str(lnnm) + " is blank. So, it is not the start of a new row.")
			blank_line = True
		else:
			print("No, line " + str(lnnm) + " is not blank. So, it may be the start of a new row.")

			print("What is the first character in line " + str(lnnm) + "?")

			char1 = ln[0]
			print("The first character in line " + str(lnnm) + " is '" + char1 + "'.")

			print("Is the first character in line " + str(lnnm) + " a comma?") # b/c comma indicates code is blank
			if char1 == ",":
				print("Yes, the first character in line " + str(lnnm) + " is a comma. So, it is the start of a new row. It is also the start of a new collection.")
				blank_code = True
			else:
				print("No, the first character in line " + str(lnnm) + " is not a comma. So, it may be the start of a new row.")
				blank_code = False

				# check if all uppercase code
				uppercase_code = product.check_uppercase_code(ln)

		if blank_line:
			new_row = False
		elif blank_code:
			new_row = True
		elif uppercase_code:
			new_row = True

	decision = ""
	if new_row:
		decision = "is"
	else:
		decision = "is not"

	print("Line " + str(lnnm) + " " + decision + " the start of a new row.\n")

	return new_row
