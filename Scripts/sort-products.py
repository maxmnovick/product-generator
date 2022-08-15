# sort products so they appear in standard format

all_product_names = ["King Panel Headboard"]
current_product_names = ["Narrow Chest", "Dresser", "Mirror"]
standard_product_names = ""

for product_name in all_product_names:

  for current_product_name in current_product_names:

    if product_name == current_product_name:

        standard_product_names += product_name

        break

    standard_product_names += ","

print(standard_product_names)
