# sort categories so that Mstar products are shown in the front
#
# Usage: sort-categories.py <name-of-category-to-sort> <sort-field> <sort-value>
#
# Example 1: move products with vendor=Mstar to top of all categories
# sort-categories.py all-categories vendor Mstar
#
# Example 2: group products in same series together in all categories
# sort-categories.py all-categories series all
#
# I'm not trying to make you feel any different way. I'm just trying to find a solution for you.

import collection

# get arguments or parameters
collection_arg = "Standard-Sofas"
sort_field_arg = "vendor"
sort_value_arg = "mstar"

# get products file for cross-referencing
vendor_products_filename = "../Data/" + sort_value_arg.lower() + "-products-export.csv"
sort_field_products_filename = ""
if sort_field_arg == "vendor":
	sort_field_products_filename = vendor_products_filename

elif sort_field_arg == "type":
	print("sort field argument: type")
elif sort_field_arg == "series":
	print("sort field argument: series")
else:
	print("unrecognized sort field argument")

sort_field_products = collection.read_collection(sort_field_products_filename)
#print("vendor_products: " + str(vendor_products) + "\n")
sort_field_product_handles = collection.isolate_collection_field(sort_field_products, "handle")

# get collection file
collection_filename = "../Data/" + collection_arg.lower() + "-Smart-Collections-export.csv"
input_collection = collection.read_collection(collection_filename) # array of strings, where each string is csv row of collection where commas separate data fields
#print("input_collection: " + str(input_collection) + "\n")

# slice input collection to current category or isolate desired category,
# before isolating linked products
input_categories = collection.isolate_categories(input_collection)

sorted_linked_products = []

for category in input_categories:

	# linked products restricted to only linked products of single collection before sorting,
	# so must know loop iterations or rows splitting collections, based on product count
	input_linked_products = collection.isolate_collection_field(category, "linked products")

	# sort products linked to a single collection
	#print("===compare linked products to mstar products and sort===")
	sorted_linked_products.extend(collection.sort_linked_products(input_linked_products, sort_field_product_handles, sort_value_arg))

# after all linked products are sorted seprately for separate collections, arrange 1 collection at a time, and then bring them together in sequence
arranged_collection = collection.arrange_collection(input_collection, collection_arg, sorted_linked_products)

# by the time you write to collection file, all collections should be arranged and placed in sequence in a collection of collections
collection.write_collection(arranged_collection, collection_arg)
