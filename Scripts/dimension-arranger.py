# dimension-arranger.py

import generator

# all details given together so need to isolate products
details1 = ["VICTORIA-KB", "gabe-bed", "oak", "rubber", "n/a", "91", "80", "56"]
details2 = ["VICTORIA-QB", "gabe-bed", "oak", "rubber", "n/a", "91", "64", "56"]
details3 = ["LINDA-BL-FB (M)", "gabriel-bed", "black", "MDF", "n/a", "87", "57", "56"]
details4 = ["LINDA-BL-KB (M)", "gabriel-bed", "black", "MDF", "n/a", "93", "78", "56"]
details5 = ["LINDA-BL-QB (M)", "gabriel-bed", "black", "MDF", "n/a", "93", "63", "56"]

all_details = [details1, details2, details3, details4, details5]

isolated_products = generator.isolate_products(all_details)

sizes = {
	"King":'',
	"Queen":'',
	"Full":''
}

for product in isolated_products:
	# isolated product
	for variant in product:
		width = variant[5]
		depth = variant[6]
		height = variant[7]
		dims = width + " " + depth + " " + height

		option_data = generator.generate_options(variant)
		option_values = option_data[1]
		size_value = option_values[0]

		sizes[size_value] = dims

	print("Sizes: " + str(sizes))
