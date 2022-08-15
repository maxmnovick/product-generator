# color-arranger.py
# like dimension arranger but for colors

import reader, generator

details1 = ["VICTORIA-KB", "gabe-bed", "oak", "rubber", "n/a", "91", "80", "56"]
details2 = ["VICTORIA-QB", "gabe-bed", "red", "rubber", "n/a", "91", "64", "56"]
details3 = ["VICTORIA-CH", "gabe-chest", "oak", "rubber", "n/a", "38", "18", "50"]
details4 = ["LINDA-BL-FB (M)", "gabriel-bed", "green", "MDF", "n/a", "87", "57", "56"]
details5 = ["LINDA-BL-KB (M)", "gabriel-bed", "black", "MDF", "n/a", "93", "78", "56"]
details6 = ["LINDA-BL-QB (M)", "gabriel-bed", "gold", "MDF", "n/a", "93", "63", "56"]
all_details = [details1, details2, details3, details4, details5, details6]

colors = reader.read_standards("colors")

products = generator.isolate_products(all_details)

for product in products:
	# isolated product
	
	color_opt = False
	
	for variant in product:
		variant_colors = variant[2]

		option_data = generator.generate_options(variant)
		option_names = []
		option_values = []
		if len(option_data) > 0:
			option_names = option_data[0]
			option_values = option_data[1]

		# get the value of the color option, if there is one
		opt_idx = 0
		for opt_name in option_names:
			if opt_name == 'Color':
				color_opt = True
				break
			opt_idx += 1

		if color_opt:
			color_value = option_values[opt_idx]

			colors[color_value] = variant_colors

	print("Colors: " + str(colors) + "\n")