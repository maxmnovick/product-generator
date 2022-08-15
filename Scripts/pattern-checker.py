# check-pattern.py

import re

clearance_names = ["2347 Sectional SET", "Chair Model 365 White SET", "6311 Sectional SET",
	"Air Fabric Sectional with Sliding Seats SET", "365 Dining Chair Black SET",
	"Sara Full Leather SET"]

clearance_keywords = ["sectional", "chair", "leather set"]
clearance_types = ["sectionals", "chairs", "living room sets"]

for name in clearance_names:
	for key_idx in range(len(clearance_keywords)):

		print('Looking for "%s" in "%s" ->' % (clearance_keywords[key_idx], name.lower()), end=' ')

		if re.search(clearance_keywords[key_idx], name.lower()):
			print("pattern found in string")
			product_type = clearance_types[key_idx]
			print("Product Type: " + product_type + "\n")
			break;
		else:
			print('no match')
