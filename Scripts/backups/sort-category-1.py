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

sorted_category_final_field = "Product: Position"
sorted_category_fields = ["ID", "Handle", "Command", "Title", "Sort Order",
"Published", "Must Match", "Rule: Product Column", "Rule: Relation",
"Rule: Condition", "Product: ID", "Product: Handle",
sorted_category_final_field]

# get arguments or parameters
category_arg = "Standard-Sofas"
sort_field_arg = "vendor"
sort_value_arg = "mstar"

# get collection file
category_filename = "../Data/" + category_arg + "-Smart-Collections-export.csv"
# get products file for cross-referencing
vendor_products_filename = "../Data/" + "Mstar" + "-products-export.csv"

sorted_category_filename = "../Data/" + category_arg + "-Smart-Collections-sorted-import.csv"
sorted_category_file = open(sorted_category_filename, "w", encoding="utf8") # overwrite existing content

headers = ""
for field in sorted_category_fields:
	headers += "\"" + field + "\""
	if field != sorted_category_final_field:
		headers += ","

#print(headers)
sorted_category_file.write(headers)
sorted_category_file.write("\n")

# INCOMPLETE: sample input collection with 1 row:
#collection = ['\"<ID>\", \"<Handle>\", \"<Command>\", \"<Title>\", \"<Body HTML>\", \"<Sort Order>\", \"<Template Suffix>\", \"<Must Match>\", \"<Rule: Product Column>\", \"<Rule: Relation>\", \"<Rule: Condition>\", \"<Product: ID>\", \"<Product: Handle>\", \"<Product: Position>\"']

def read_collection(filename):
	collection = []

	with open(filename, encoding="utf8") as collection_file:
		next(collection_file) # cast 1st line into oblivion

		current_line = ""
		for collection_info in collection_file:
			collection_info = collection_info.strip()

			current_line += collection_info
			if "\"" in collection_info[-1:]:
				collection.append(current_line)
				current_line = ""
			else:
				pass

		collection_file.close()

	return collection

if sort_field_arg == "vendor":

	vendor_collection = read_collection(vendor_products_filename)
	#print("vendor_collection: " + str(vendor_collection) + "\n")
	vendor_product_handles = []

	for product in vendor_collection:
		#print("original collection row: " + product)

		init_product_info = product.split("\",") # ["ID", "Handle", "Command", ....]
		for info in range(len(init_product_info)):
			init_product_info[info] = init_product_info[info].replace("\"", "")
		#print("init_product_info: " + str(init_product_info))

		vendor_product_handles.append(init_product_info[1])

elif sort_field_arg == "series":
	pass

else:
	print("unrecognized sort field argument")

#print("vendor_product_handles: " + str(vendor_product_handles) + "\n")

# for 1 collection, to test

input_collection = read_collection(category_filename) # array of strings, where each string is csv row of collection where commas separate data fields
#print("input_collection: " + str(input_collection) + "\n")

def isolate_linked_products(collection):

	linked_products = []

	for row in collection:
		#print("original collection row: " + collection[row_idx])

		init_collection_info = row.split("\",")
		for info in range(len(init_collection_info)):
			init_collection_info[info] = init_collection_info[info].replace("\"", "")
		#print("init_collection_info: " + str(init_collection_info))

		# check if new collection by comparing current row's collection handle to previous row's collection handle

		linked_products.append(init_collection_info[22:24])

		#print("linked_products: " + str(linked_products) + "\n")

	return linked_products

input_linked_products = isolate_linked_products(input_collection)

#print("===compare linked products to mstar products and sort===")
def sort_linked_products(init_linked_products, sort_value):

	linked_products = init_linked_products
	#print("linked_products: " + str(linked_products))

	for linked_product in linked_products:

		linked_product_id = linked_product[0]
		linked_product_handle = linked_product[1]
		#print("linked_product_handle: \"" + linked_product_handle + "\"")

		linked_product_vendor = ""
		for vendor_product_handle in vendor_product_handles:
			if linked_product_handle == vendor_product_handle:
				linked_product_vendor = sort_value
				break

		if linked_product_vendor == sort_value:
			#print(linked_product_handle + ": Mstar")
			# put product in position 1 of collection and shift other products to fill the empty space
			#linked_product.append("Mstar")
			linked_products.insert(0, linked_products.pop(linked_products.index(linked_product)))
		else:
			pass
			#linked_product.append("not Mstar")

	return linked_products

sorted_linked_products = sort_linked_products(input_linked_products, sort_value_arg)

# replace original linked product fields with sorted version
collection_title = category_arg.replace("-", " ")
for row_idx in range(len(input_collection)):

	init_collection_info = input_collection[row_idx].split("\",")
	for info in range(len(init_collection_info)):
		init_collection_info[info] = init_collection_info[info].replace("\"", "")

	# unchanged collection info
	collection_id = init_collection_info[0]
	collection_handle = init_collection_info[1]
	collection_command = init_collection_info[2]
	collection_title = init_collection_info[3]
	collection_sort_order = init_collection_info[5]
	collection_published = init_collection_info[8]
	collection_match = init_collection_info[18]
	collection_rule_product_column = init_collection_info[19]
	collection_rule_relation = init_collection_info[20]
	collection_rule_condition = init_collection_info[21]

	# sorted linked product info
	linked_product_id = sorted_linked_products[row_idx][0]
	linked_product_handle = sorted_linked_products[row_idx][1]
	#linked_product_vendor = sorted_linked_products[row_idx][2]

	# unchanged linked product position order b/c id and handle shifted instead
	linked_product_position = init_collection_info[24]

	sorted_category_info = "\"" + collection_id + "\",\"" + collection_handle + "\",\"" + collection_command + "\",\"" + collection_title + "\",\"" + collection_sort_order + "\",\"" + collection_published + "\",\"" + collection_match + "\",\"" + collection_rule_product_column + "\",\"" + collection_rule_relation + "\",\"" + collection_rule_condition + "\",\"" + linked_product_id + "\",\"" + linked_product_handle + "\",\"" + linked_product_position + "\""

	#sorted_products = linked_product_handle + ", " + linked_product_vendor
	#print(sorted_products)

	#print(sorted_category_info + "\n")
	sorted_category_file.write(sorted_category_info)
	sorted_category_file.write("\n")

sorted_category_file.close()
