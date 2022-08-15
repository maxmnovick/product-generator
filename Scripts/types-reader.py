# types-reader.py

def read_types():
	print("=== Read Types ===\n")

	types_filename = "../Data/product-types.csv"

	types = []
	lines = []

	with open(types_filename, encoding="UTF8") as types_file:

		current_line = ""
		for catalog_info in types_file:
			current_line = catalog_info.strip()
			lines.append(current_line)

		types_file.close()

	# line_num = 1
	# for line in lines:
	# 	print("Line " + str(line_num) + ": " + line + "\n")
	#
	# 	line_num += 1

	for line in lines:
		types_in_line = line.split(",")
		for type in types_in_line:
			types.append(type)

	print("Types: " + str(types))

	print("=== Read Types ===\n")

	return types

all_types = read_types()
