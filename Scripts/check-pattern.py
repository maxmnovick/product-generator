# check-pattern.py

import re

text = 'H/B    K.S'
text = text.lower()

pattern = 'h/b[\s*k\.s]'

print('Looking for "%s" in "%s" ->' % (pattern, text), end=' ')

if re.search(pattern, text):
	print("pattern found in string")
else:
	print('no match')
