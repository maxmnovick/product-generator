# unit-converter.py
# change units of ft-in to in and back
# for rugs and other items that need to be sorted by size

import math, re, generator

vendor = "Kalaty"
input = 'descrips'
extension = "tsv"

#init_dim = 10 # assume units of inches
#print("Init Dim: " + str(init_dim) + "\"")

# if given in only inches, convert to ft-in
def convert_to_ft_in(inches):
	#print("Init In: " + str(inches))
	dim_ft = inches / 12
	dim_ft = math.floor(dim_ft)
	#print("Dim Ft: " + str(dim_ft))
	dim_in = inches % 12
	#print("Dim In: " + str(dim_in))

	dim_ft_string = dim_in_string = ''
	if dim_ft > 0:
		dim_ft_string = str(dim_ft) + "\'"
	if dim_in > 0:
		dim_in_string = str(dim_in) + "\""

	ft_in = dim_ft_string + dim_in_string
	#print("Dim Ft-In: " + ft_in)
	return ft_in

def determine_ht_dim(init_opt_string):
	ht_dim = False
	if re.search("\"\sH",init_opt_string):
		ht_dim = True
	return ht_dim

def convert_dim_opts(init_opt_strings):
	final_opt_strings = []
	for opt_string in init_opt_strings:
		init_opt_string = opt_string #"100\" Diameter" #"100\" x 200\""
		#print("Init Opt String: " + init_opt_string)
		init_opt_data = []
		init_opt_width = init_opt_depth = final_opt_string = ''
		if not determine_ht_dim(init_opt_string):
			if re.search("Diam",init_opt_string):
				init_opt_data = init_opt_string.split("\"")
				init_opt_diam = init_opt_data[0].strip()
				init_opt_diam = re.sub('\"','',init_opt_diam)
				if re.search("\d",init_opt_diam[0]):
					opt_diam_int = int(init_opt_diam)
					diam_ft_in = convert_to_ft_in(opt_diam_int)
					final_opt_string = diam_ft_in + " Diameter"
			elif re.search("x",init_opt_string):
				init_opt_data = init_opt_string.split("x")

				init_opt_width = init_opt_data[0].strip()
				init_opt_width = re.sub('\"','',init_opt_width)
				if re.search("\d",init_opt_width[0]):
					opt_width_int = int(init_opt_width)
					init_opt_depth = init_opt_data[1].strip()
					init_opt_depth = re.sub('\"','',init_opt_depth)
					opt_depth_int = int(init_opt_depth)
					width_ft_in = convert_to_ft_in(opt_width_int)
					depth_ft_in = convert_to_ft_in(opt_depth_int)
					final_opt_string = width_ft_in + " x " + depth_ft_in


		else: # there is height dim included


			if re.search("Diam",init_opt_string): # "a\" Diameter x b\" H"
				init_opt_data = init_opt_string.split("x")
				init_opt_diam = init_opt_data[0].strip()
				init_opt_diam = re.sub('Diameter','',init_opt_diam)
				init_opt_diam = init_opt_diam.strip()
				init_opt_diam = re.sub('\"|[a-zA-Z]|\s+|\.H?','',init_opt_diam)
				opt_diam_int = int(init_opt_diam)
				init_opt_ht = init_opt_data[1].strip()
				init_opt_ht = re.sub('\"|[a-zA-Z]|\s+|\.H?','',init_opt_ht)
				opt_ht_float = float(init_opt_ht)

				diam_ft_in = convert_to_ft_in(opt_diam_int)
				#ht_ft_in = convert_to_ft_in(opt_ht_float)

				final_opt_string = diam_ft_in + " Diameter"
				# final_opt_string = diam_ft_in + " Diameter x " + ht_ft_in
				# if input == 'descrips':
				# 	final_opt_string += " H. "

			elif re.search("x",init_opt_string):
				init_opt_data = init_opt_string.split("x")

				init_opt_width = init_opt_data[0].strip()
				init_opt_width = re.sub('\"|[a-zA-Z]|\s+|\.H?','',init_opt_width)
				opt_width_int = int(init_opt_width)
				init_opt_depth = init_opt_data[1].strip()
				init_opt_depth = re.sub('\"|[a-zA-Z]|\s+|\.H?','',init_opt_depth)
				opt_depth_int = int(init_opt_depth)
				# init_opt_ht = init_opt_data[2].strip()
				# init_opt_ht = re.sub('\"|[a-zA-Z]|\s+|\.H?','',init_opt_ht)
				# opt_ht_float = float(init_opt_ht)

				width_ft_in = convert_to_ft_in(opt_width_int)
				depth_ft_in = convert_to_ft_in(opt_depth_int)
				#ht_ft_in = convert_to_ft_in(opt_ht_float)

				final_opt_string = width_ft_in + " x " + depth_ft_in
				# final_opt_string = width_ft_in + " x " + depth_ft_in + " x " + ht_ft_in
				# if input == 'descrips':
				# 	final_opt_string += " H. "

		#print("Output: " + final_opt_string)
		#print(final_opt_string)
		final_opt_strings.append(final_opt_string)

	return final_opt_strings

if input == 'options':
	# format is a" x b"
	#print("Input: Option in format a\" x b\" or a\" Diameter")
	init_opts = generator.extract_data(vendor, input, extension)
	#init_opts = ["100\" Diameter", "100\" x 200\""]
	#print("Init Opts: " + str(init_opts))

	init_opt_strings = []
	for opt in init_opts:
		init_opt_string = opt[0] #"100\" Diameter" #"100\" x 200\""
		init_opt_strings.append(init_opt_string)

	final_opt_strings = convert_dim_opts(init_opt_strings)
	for opt in final_opt_strings:
		print(opt)

elif input == 'descrips':
	# format is Dimension (in): a" x b"
	#print("Input: Description in format ...Dimensions (in): a\" x b\"....")
	init_descrips = generator.extract_data(vendor, input, extension)

	#init_descrip1 = "Color: red. Dimensions (in): 100\" W x 200\" D x 0.5\" H. 300\" W x 400\" D x 0.75\" H. Handcrafted rug."
	#init_descrip2 = "Color: red. Dimensions (in): 100\" Diameter x 0.5\" H. 300\" W x 400\" D x 0.75\" H. Handcrafted rug."
	#init_descrips = [init_descrip1,init_descrip2]

	init_descrip_strings = []
	for descrip in init_descrips:
		init_descrip_string = descrip[0] #"100\" Diameter" #"100\" x 200\""
		init_descrip_strings.append(init_descrip_string)

	for init_descrip in init_descrip_strings:
		#print("Initial Description: " + init_descrip)
		init_dims = final_dims = intro = ''
		if re.search("Dimensions \(in\):",init_descrip):
			#print("Found Dimensions in Description")
			descrip_data = init_descrip.split("Dimensions (in): ",1)
			intro = descrip_data[0]
			dim_features = descrip_data[1]
			dim_features_data = re.split("(?:H)\.\s*(?:[a-zA-Z])",dim_features,1)
			dims = dim_features_data[0] + "H. "
			#print("Dims: \"" + dims + "\"")

			init_opt_strings = []
			all_dims_data = re.split("(?:H)\.\s",dims)
			num_dims = len(all_dims_data)
			for dim_idx in range(num_dims):
				dim = all_dims_data[dim_idx]
				if dim != '':
					if dim_idx != num_dims - 1:
						dim = dim + "H"

					#print("Dim: \'" + dim + "\'")
					init_opt_string = dim
					init_opt_strings.append(init_opt_string)
			final_opt_strings = convert_dim_opts(init_opt_strings)

		for opt_idx in range(len(final_opt_strings)):
			opt = final_opt_strings[opt_idx]
			#print("Option: " + opt)
			opt = re.sub("\"","\",CHAR(34),\"",opt)
			if opt_idx == 0:
				final_dims += opt
			else:
				final_dims += "\",CHAR(10),\"" + opt
			#print(final_dims)

		# intro_data = re.split("Materials: |Finishes: ",intro)
		# print("Intro Data: " + str(intro_data))
		# colors = intro_data[0] + "\""
		# print("Colors: " + colors)
		# materials = ",CHAR(10),Materials: " + intro_data[1] + "\""
		# print("Materials: " + materials)
		# finishes = ",CHAR(10),Finishes: " + intro_data[2]
		# print("Finishes: " + finishes)
		# intro = colors + materials + finishes

		init_intro_data = intro.split(". ")
		final_intro_data = []
		#print("Init Intro Data: " + str(init_intro_data))
		for datum in init_intro_data:
			intro_datum = datum.strip()
			if intro_datum != '':
				final_intro_data.append(intro_datum)
		#print("Final Intro Data: " + str(final_intro_data))

		final_intro = ''
		for datum in final_intro_data:
			final_intro += datum + ".\",CHAR(10),\""
		#print("Final Intro Fmla: " + final_intro)

		final_descrip_fmla = "=CONCATENATE(\"" + final_intro + "Dimensions (in): \",CHAR(10),\"" + final_dims + "\")"
		#print("Final Descrip: " + final_descrip_fmla)
		print(final_descrip_fmla)

# final dim 100/12=8 R4 so 8'4"
