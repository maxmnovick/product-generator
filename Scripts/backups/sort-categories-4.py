# sort categories so that Mstar products are shown in the front
#
# Usage: sort-categories.py <name-of-category-to-sort> <sort-field> <sort-value>
#
# Example 1: move products with vendor=Mstar to top of all categories
# sort-categories.py all-categories vendor mstar
#
# Example 2: group products in same series together in all categories
# sort-categories.py all-categories series all
#
# I'm not trying to make you feel any different way. I'm just trying to find a solution for you.

import collection
import argparse

print("===Sort Categories===\n")

# get arguments or parameters
# create an ArgumentParser object to read command line arguments
parser = argparse.ArgumentParser(description='Sort a collection of products.')
parser.add_argument('collection')
args = parser.parse_args()

collection_arg = args.collection
print("Collection Argument:\t" + collection_arg)
sort_field_arg = "vendor"
print("Sort Field Argument:\t" + sort_field_arg)
sort_value_arg = "mstar"
print("Sort Value Argument:\t" + sort_value_arg)
print()

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
#print("Collection Filename: " + collection_filename)
input_collection = collection.read_collection(collection_filename) # array of strings, where each string is csv row of collection where commas separate data fields
#print("Input Collection: " + str(input_collection) + "\n")

# slice input collection to current category or isolate desired category,
# before isolating linked products
# input categories should be in same order as original collection, so they can be arranged with sorted linked products
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
arranged_collection = collection.arrange_collection(input_collection, sorted_linked_products)

# by the time you write to collection file, all collections should be arranged and placed in sequence in a collection of collections
collection.write_collection(arranged_collection, collection_arg)
