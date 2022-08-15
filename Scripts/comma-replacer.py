# comma-replacer.py

def extract_data(input):
	catalog_filename = "../Data/" + input + "-init-data.csv"

	lines = []
	data = ''
	all_data = []

	with open(catalog_filename, encoding="UTF8") as catalog_file:

		current_line = ""
		for catalog_info in catalog_file:
			current_line = catalog_info.strip()
			lines.append(current_line)

		catalog_file.close()

	# skip header line
	for line in lines[1:]:
		all_data.append(line)

	return all_data

def write_data(arranged_data, input):
	catalog_filename = "../Data/" + input + "less-final-data.csv"
	catalog_file = open(catalog_filename, "w", encoding="utf8") # overwrite existing content

	for row_idx in range(len(arranged_data)):
		catalog_file.write(arranged_data[row_idx])
		catalog_file.write("\n")
		#print(catalog[row_idx])

	catalog_file.close()

input = "comma"

data = extract_data(input)

arranged_data = []
commaless = ''

for idx in range(len(data)):
	#print("datum: " + datum)
	datum = data[idx]

	commaless = datum.replace(",", "\",\"")

	print(commaless)
	arranged_data.append(commaless)

write_data(arranged_data, input)
