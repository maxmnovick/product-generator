# description-generator.py
# input all details
# output all descriptions formulas for insertion to spreadsheet
# description parts:
# - Intro/Overview
# - Colors
# - Materials
# - Finishes
# - Dimensions
# - Features/Comments

import generator

vendor = "Ashley"
input = "descrip"
extension = "tsv"

all_details = generator.extract_data(vendor, input, extension)
# details1 = ["VICTORIA-KB", "gabe-bed", "oak", "rubber", "n/a", "91", "80", "56"]
# details2 = ["VICTORIA-QB", "gabe-bed", "oak", "rubber", "n/a", "91", "64", "56"]
# details3 = ["VICTORIA-CH", "gabe-chest", "oak", "rubber", "n/a", "38", "18", "50"]
# details4 = ["LINDA-BL-FB (M)", "gabriel-bed", "black", "n/a", "MDF", "87", "57", "56"]
# details5 = ["LINDA-BL-KB (M)", "gabriel-bed", "black", "n/a", "MDF", "93", "78", "56"]
# details6 = ["LINDA-BL-QB (M)", "gabriel-bed", "black", "n/a", "MDF", "93", "63", "56"]
# all_details = [details1, details2, details3, details4, details5, details6]

products = generator.isolate_products(all_details)

for product in products:
	intro_fmla = generator.generate_intro_fmla(product)

	colors_fmla = generator.generate_colors_fmla(product)

	materials_fmla = generator.generate_materials_fmla(product)

	finishes_fmla = generator.generate_finishes_fmla(product)

	dimensions_fmla = generator.generate_dimensions_fmla(product)

	features_fmla = generator.generate_features_fmla(product)
	
	#arrival_fmla = generator.generate_arrival_fmla(product) # arrival time, such as Arrives: 3-4 weeks from Date of Purchase (eventually update dynamically based on date of purchase)

	descrip_fmla = "=CONCATENATE(" + intro_fmla  + ",CHAR(10)," + colors_fmla  + ",CHAR(10)," + materials_fmla  + ",CHAR(10)," + finishes_fmla  + ",CHAR(10)," + dimensions_fmla + ",CHAR(10)," + features_fmla + ")"

	# all variants of the product get the same description
	# the variants must be ordered by options, based on knowledge of desired option order and available options
	for variant in product:
		print(descrip_fmla)
	#print()
