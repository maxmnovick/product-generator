# product-isolator.py

import numpy as np

details1 = ["VICTORIA-KB", "gabe-bed", "oak", "rubber", "91", "80", "56"]
details2 = ["VICTORIA-QB", "gabe-bed", "oak", "rubber", "91", "64", "56"]
details3 = ["LINDA-BL-FB (M)", "gabriel-bed", "black", "MDF", "87", "57", "56"]
details4 = ["LINDA-BL-KB (M)", "gabriel-bed", "black", "MDF", "93", "78", "56"]
details5 = ["LINDA-BL-QB (M)", "gabriel-bed", "black", "MDF", "93", "63", "56"]

all_details = [details1, details2, details3, details4, details5]

products = []

def isolate_detail_field(all_details, field_title):
	detail_field_values = []

	handle_idx = 1
	field_idx = 0
	if field_title == "handle":
		field_idx = handle_idx

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

field_title = "handle" # we know that all variants of the same product have the same handle

handles = np.array(isolate_detail_field(all_details, field_title))

_, idx, cnt = np.unique(handles, return_index=True, return_counts=True)

unique_handles = handles[np.sort(idx)]
counts = cnt[np.argsort(idx)]
indices = np.sort(idx)

num_products = len(unique_handles)

# isolate products and append to products array
for product_idx in range(num_products):
	product_start_idx = indices[product_idx]
	product_stop_idx = product_start_idx + counts[product_idx]

	product_rows = isolate_product_from_details(all_details, product_start_idx, product_stop_idx)
	products.append(product_rows)

	product_start_idx = product_stop_idx
	if product_start_idx > len(all_details) - 1:
		break;

print("Products: " + str(products))
