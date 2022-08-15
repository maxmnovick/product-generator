# Change product properties
# Change tags
# so that preorder items are shown as preorder,
# and newly stocked products are no longer shown as preorder
#
# Use Excelify to export Products with these data fields:
# - Basic Columns
# - Inventory / Variants
# - Variant Cost
#
# Usage: change-product-properties.py <name-of-collection-to-change-properties> <property-to-change> <action-to-take> <value-to-change>

import collection

print("===Change Product Properties===\n")

collection_arg = "preorder"
print("Collection Argument:\t" + collection_arg)
property_arg = "tag" # could be any product property
print("Property Argument:\t" + property_arg)
action_arg = "add" # could be add, change, remove
print("Action Argument:\t" + action_arg)
value_arg = "preorder"
print("Value Argument:\t" + value_arg)
print()

# get collection file
collection_filename = "../Data/" + collection_arg.lower() + "-products-export.csv"
#print("Collection Filename: " + collection_filename)
input_collection = collection.read_collection(collection_filename)
#print("Input Collection: " + str(input_collection) + "\n")

input_tags = []

if property_arg == "tags":

	input_tags = collection.isolate_collection_field(input_collection, property_arg)

	property_value = ", " + value_arg

	if action_arg == "add":
		# if no preorder tag, add one;
		if tags.find(value_arg) == -1:
			tags.append(property_value)
	elif action_arg == "remove":
		# if a preorder tag, remove it
		tags.replace(property_value, "")
	elif action_arg == "change":
		change_value = ""
		tags.replace(property_value, change_value)
	else:
		print("Warning: Invalid Action Argument. Options: add, remove, change.")

changed_tags = collection.change_product_properties(input_collection, input_tags, action_arg, value_arg)

arranged_products = collection.arrange_products(input_collection, changed_tags)

changed_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Tags", "Tags Command", "Variant Price", "Variant Compare At Price",
	"Variant Inventory Tracker", "Variant Inventory Qty",
	"Variant Inventory Item ID", "Variant ID", "Variant Command",
	"Option1 Name", "Option1 Value",
	"Option2 Name", "Option2 Value",
	"Option3 Name", "Option3 Value" ]

collection.write_collection(arranged_products, collection_arg, changed_product_fields)
