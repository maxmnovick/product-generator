# measurement-interpreter.py
# could also be simply measurement reader but interpret is more fitting
# because we need to read and then actually fill in the blanks
# based on width, depth, height fields, and possibly other fields if needed
# sample inputs
# wdh \d+
# wxd
# w x d
# w' x d' h'
# w' x d" x h'
# w_ft'w_in"d_ft'd_in"
# w_ft'w_in"d_ft'd_in'



#input
meas_samples = ["1\' 1\'","1\" 1\"","1\'2\" 1'2\""]

init_width = meas_samples[0]
init_depth = meas_samples[0]
init_height = meas_samples[0]

# determine if we should accept the given measurement or we see possible typo
# measurement is valid if it is given in a format in our dictionary of known formats
# if we have to check dictionary then it maybe more efficient to simply
# use list of known formats to extract valid measurements and consider all others invalid
if determine_valid_meas(measurement):
	# interpret measurement
	print("Measurement is valid: \"" + measurement + "\"")
else:
	print("Warning: invalid measurement: \"" + measurement + "\"!")
