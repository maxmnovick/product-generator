# dimension-formatter.py
# process dimensions given in special format

import generator, re

vendor = "Kalaty"
input = "dims"
extension = "tsv"

# format given a'b" x c'd"

all_details = generator.extract_data(vendor, input, extension)

for item_details in all_details:

	init_dim_string = '9\" x 3\"' #item_details[0] # eg "9\' x 2\'"
	#print("Init Dim String: " + init_dim_string)

	width_and_depth = init_dim_string.split(" x ")
	width = width_and_depth[0]
	#print("Width: " + width)
	depth = width_and_depth[1]
	#print("Depth: " + depth)

	width_ft_value = width_in_value = depth_ft_value = depth_in_value = 0.0

	# if measured in feet
	if re.search("\'",width):
		width_ft_and_in = width.split("\'")
		print("Width Feet and Inches: " + str(width_ft_and_in))
		width_ft = width_ft_and_in[0]
		if width_ft != '':
			width_ft_value = float(width_ft)
		print("Width Feet: " + width_ft)
		print("Width Feet Value: " + str(width_ft_value))
	
		width_in = width_ft_and_in[1].rstrip("\"")
		if width_in != '':
			width_in_value = float(width_in)
		print("Width Inches: " + width_in)
		print("Width Inches Value: " + str(width_in_value))
	# if measured in inches
	elif re.search("\"",width):
		width_in = width.rstrip("\"")
		if width_in != '':
			width_in_value = float(width_in)
		print("Width Inches: " + width_in)
		print("Width Inches Value: " + str(width_in_value))
	
	if re.search("\'",depth):
		depth_ft_and_in = depth.split("\'")
		depth_ft = depth_ft_and_in[0]
		if depth_ft != '':
			depth_ft_value = float(depth_ft)
		print("Depth Feet: " + depth_ft)
		depth_in = depth_ft_and_in[1].rstrip("\"")
		if depth_in != '':
			depth_in_value = float(depth_in)
		print("Depth Inches: " + depth_in)
	# if measured in inches
	elif re.search("\"",depth):
		depth_in = depth.rstrip("\"")
		if depth_in != '':
			depth_in_value = float(depth_in)
		print("Depth Inches: " + depth_in)
		print("Depth Inches Value: " + str(depth_in_value))

	total_width = int(round(width_ft_value * 12.0 + width_in_value))
	#print("Total Width (in): " + str(total_width))
	total_depth = int(round(depth_ft_value * 12.0 + depth_in_value))
	#print("Total Depth (in): " + str(total_depth))

	print(str(total_width) + "," + str(total_depth))