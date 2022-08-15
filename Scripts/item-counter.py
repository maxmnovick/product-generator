# item-counter.py
# count number of unique items when given line items with 1 line per 1 item added to inventory

import numpy as np
import generator

vendor = "Liberty"
input = "invoice"
extension = "tsv"

# line1 = ["Splat Back Side Chair (RTA)", "116-C2501 S"]
# line2 = ["Splat Back Side Chair (RTA)", "116-C2501 S"]
# line3 = ["Bench (RTA)", "116-C9001B"]
# line4 = ["Nido Chair - Light Tan (RTA)", "198-C9001 S-TN"]
# line5 = ["Nido Chair - Light Tan (RTA)", "198-C9001 S-TN"]
# all_lines = [line1, line2, line3, line4, line5]

all_lines = generator.extract_data(vendor, input, extension)

items = []

field_title = "sku" # we know that all variants of the same product have the same handle

def isolate_detail_field(all_details, field_title):
	detail_field_values = []

	sku_idx = 0
	field_idx = 0
	if field_title == "sku":
		field_idx = sku_idx

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		field_value = item_details[field_idx]
		detail_field_values.append(field_value)

	return detail_field_values

skus = np.array(isolate_detail_field(all_lines, field_title))

_, idx, cnt = np.unique(skus, return_index=True, return_counts=True)

unique_skus = skus[np.sort(idx)]
counts = cnt[np.argsort(idx)]
indices = np.sort(idx)

num_items = len(unique_skus)

print("No. Unique Items: " + str(num_items) + "\n")