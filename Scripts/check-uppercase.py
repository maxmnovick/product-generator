# check-uppercase.py

import re, string

# return true if the word is all uppercase

word = "UPPER.11"

print("word:" + word)

# only need first series of letters
stripped_word = re.sub('[\W_]+', '', word)

print("stripped_word:" + stripped_word)

if stripped_word.isupper():
	print("upper")
else:
	print("lower")
