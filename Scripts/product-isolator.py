# product-isolator.py

import numpy as np
import generator

vendor = "Liberty"
input = "invoice" # options: invoice, details
extension = "tsv"

all_data = []
field_title = ""

if input == "invoice":
# 	line1 = ["116-C2501 S", "Splat Back Side Chair (RTA)"]
# 	line2 = ["116-C2501 S", "Splat Back Side Chair (RTA)"]
# 	line3 = ["116-C9001B", "Bench (RTA)"]
# 	line4 = ["198-C9001 S-TN", "Nido Chair - Light Tan (RTA)"]
# 	line5 = ["198-C9001 S-TN", "Nido Chair - Light Tan (RTA)"]
# 	all_data = [line1, line2, line3, line4, line5]
	
	field_title = "sku"
	
elif input == "details":
# 	details1 = ["VICTORIA-KB", "gabe-bed", "oak", "rubber", "n/a", "91", "80", "56"]
# 	details2 = ["VICTORIA-QB", "gabe-bed", "oak", "rubber", "n/a", "91", "64", "56"]
# 	details3 = ["VICTORIA-CH", "gabe-chest", "oak", "rubber", "n/a", "38", "18", "50"]
# 	details4 = ["LINDA-BL-FB (M)", "gabriel-bed", "black", "n/a", "MDF", "87", "57", "56"]
# 	details5 = ["LINDA-BL-KB (M)", "gabriel-bed", "black", "n/a", "MDF", "93", "78", "56"]
# 	details6 = ["LINDA-BL-QB (M)", "gabriel-bed", "black", "n/a", "MDF", "93", "63", "56"]
# 	all_data = [details1, details2, details3, details4, details5, details6]
	
	field_title = "handle" # we know that all variants of the same product have the same handle

all_data = generator.extract_data(vendor, input, extension)

products = []

def isolate_detail_field(all_details, field_title):
	detail_field_values = []

	sku_idx = 0
	handle_idx = 1
	field_idx = 0
	if field_title == "handle":
		field_idx = handle_idx
	elif field_title == "sku":
		field_idx = sku_idx

	for item_idx in range(len(all_details)):
		item_details = all_details[item_idx]
		field_value = item_details[field_idx]
		detail_field_values.append(field_value)

	return detail_field_values

def isolate_product_from_details(all_details, start_idx, stop_idx):
	product_rows = []

	for variant_idx in range(start_idx, stop_idx):
		product_rows.append(all_details[variant_idx])

	return product_rows

parent_values = np.array(isolate_detail_field(all_data, field_title))

_, idx, cnt = np.unique(parent_values, return_index=True, return_counts=True)

unique_parent_values = parent_values[np.sort(idx)]
counts = cnt[np.argsort(idx)]
indices = np.sort(idx)

num_products = len(unique_parent_values)

# isolate products and append to products array
for product_idx in range(num_products):
	product_start_idx = indices[product_idx]
	product_stop_idx = product_start_idx + counts[product_idx]

	product_rows = isolate_product_from_details(all_data, product_start_idx, product_stop_idx)
	products.append(product_rows)

	product_start_idx = product_stop_idx
	if product_start_idx > len(all_data) - 1:
		break;

print("Products: " + str(products))

# accepts list of products, where products are lists of instances of that product
def display_unique_items(products):
	for product in products:
		product_instance = product[0] # instance of product if given invoice, or variant of product if given details
		sku = product_instance[0]
		descrip = product_instance[1]
		qty = len(product)
		
		print(sku + "," + descrip + "," + str(qty))

if input == "invoice":
	display_unique_items(products)
	
# TODO: if given skus for parts that make up a product, we must confirm that there is no parent sku before using a concatenated sku as a last resort
# the concatenated sku could correspond to a Jennifer-made sku that is compatible with inventory system
# to confirm that there is no parent sku, we must go to the vendor page and look at all skus in the given collection
# for example if the sku contains a dash, remove the code after the dash and look for all items matching code before the dash, b/c those are in the same collection
# then if we know what larger product the given part is part of, we can look for a corresponding title that indicates it is the parent product
# for example if we are given a table base and top, look for a title with only table because that must be the parent sku 
# if 2 types of table, such as pedestal, rectangular, and gathering, consider the variant of table as a possible parent sku 
# what we need: entire vendor catalog, in standard spreadsheet format, for cross-reference
# catalog fields we need: sku, title
# use sku to find all items in collection, 
# use title to find parent sku (b/c parent sku does not necessarily indicate that it is the parent but title is always clear)
	
