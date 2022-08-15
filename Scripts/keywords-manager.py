# keywords-manager.py
# add new, update, delete keywords in bulk
# given list of colors, select unique ones and format in dictionary, so it can be copy pasted to json file

# add new standards

# order of detail fields
sku_idx = 0
handle_idx = 1
title_idx = 2
intro_idx = 3
color_idx = 4
mat_idx = 5
finish_idx = 6
width_idx = 7
depth_idx = 8
height_idx = 9
weight_idx = 10
features_idx = 11
cost_idx = 12
img_src_idx = 13
barcode_idx = 14

import generator
import numpy as np

#all_colors = ["blue", "red", "green"]

vendor = "Kalaty"
input = "details"
extension = "tsv"

all_details = generator.extract_data(vendor,input,extension)

all_colors = []
for item_details in all_details:
	item_color = item_details[color_idx]
	all_colors.append(item_color)
	
colors_array = np.array(all_colors)
new_colors = np.unique(colors_array)

# format in dictionary

print("Dict String: ")
for color in new_colors:

	if color != 'n/a':
		color = color.capitalize()

		dict_string = "\"" + color + "\":[\"" + color.lower() + "\"],"
		print(dict_string)