# variant-analyzer.py
# given option names and values, find option name-value pairs

# test with bedroom set b/c already started and nightstand set only has 1 option name
option_names = [ "size", "room configuration" ]
option1_values = [ "king", "queen", "twin" ]
option2_values = [ "bed + nightstand", "bed + 2 nightstands", "bed + nightstand + dresser + mirror" ]
option_values = [ option1_values, option2_values ]

for value_set_idx in range(len(option_values)):

	current_opt_values = option_values[value_set_idx]

	for current_value_idx in range(len(current_opt_values)):

		print("Name: " + option_names[value_set_idx] + ", Value: " + current_opt_values[current_value_idx] + "\n")
	
		#print("Current value index: " + str(current_value_idx))
		current_value_num = current_value_idx + 1
		print("Current value number: " + str(current_value_num))
		print("Number of values: " + str(len(current_opt_values)))
		
		print()