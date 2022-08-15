# given Category Type from ESF vendor, determine appropriate Product Type for Inventory

import catalog

vendor = "ESF"

# input list of category types
# get product catalog file (given by vendor-ESF here)
catalog_filename = "../Data/" + vendor + "-product-catalog-single-sample.csv"
#print("products_filename: " + products_filename)

input_products = catalog.read_catalog(catalog_filename, vendor)

#print(input_products[0])

# search for Category Type field


# set category type
category_type = "BEDROOMS"

# set product_type
if category_type == "BEDROOMS":
	product_type = "bedroom sets"
elif category_type == "DINING":
	product_type = "dining sets"
elif category_type == "LIVING":
	product_type = "living room sets"
elif category_type == "WALL UNITS":
	product_type = "wall units"
elif category_type == "CLEARANCE":
	product_type = "Determine appropriate product type based on given vendor info."
elif category_type == "OTHER":
	product_type = "Determine appropriate product type based on given vendor info."

# output list of product types

#print(product_type)
