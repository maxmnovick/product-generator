# Discontinue a single product by changing variable fields to assigned values

disco_product_fields = ["ID", "Handle", "Command", "Title", "Vendor", "Type",
	"Tags", "Tags Command", "Published", "Variant Inventory Tracker",
	"Variant Inventory Qty"]

# get values for product to be discontinued
# sample product: allura-night-stand
init_product_info = ["nightstands", "HomeElegance", "color-white, style-modern"] # sample table row with given product info

disco_type = "DISCONTINUED"

disco_vendor = init_product_info[1] + "-Dropped"

disco_tags = init_product_info[2]
disco_date_metrics = ["year", "month", "day of month", "day of week"]
# =======get date values from calendar=======
disco_date_values = ["2020", "1", "29", "Wednesday"]
for index in range(4):
	disco_date_tag = "discontinued-" + disco_date_metrics[index] + "-" + disco_date_values[index]
	disco_tags += ", " + disco_date_tag
print("tags: " + disco_tags)

disco_product_info = [disco_type, disco_vendor, disco_tags]

# =======discontinue collection=======
headers = ""
for field in disco_product_fields:
	headers += field
	if field != "Variant Inventory Qty":
		headers += ", "

# display/export table csv
print(headers)
for product in
