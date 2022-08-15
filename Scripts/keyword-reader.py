# keyword-reader.py

import json

type = "nightstands"

keys_filename = "../Data/keywords/keywords.json"

keys = []
lines = []

try:
	with open(keys_filename, encoding="UTF8") as keys_file:

		current_line = ""
		for key_info in keys_file:
			current_line = key_info.strip()
			lines.append(current_line)

		keys_file.close()
except:
	print("Warning: No keywords file!")

# combine into 1 line
condensed_json = ''
for line in lines:
	condensed_json += line

# parse condensed_json
parsed_json = json.loads(condensed_json)

# the result is a python dictionary from which we can extract keywords for a given product type
keys = parsed_json[type]

print("Keywords for " + type + ": " + str(keys))
