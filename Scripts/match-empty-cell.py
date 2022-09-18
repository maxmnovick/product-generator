# test pandas library match empty cell

import pandas

filepath = '../Data/acme-price-sheet-test.tsv'
table = pandas.read_table(filepath)
print(table)

row = table.loc[0]
print(row)

for value in row:
    print('value: ' + str(value)) # NaN shown as "nan" lowercase

for row in table:
    print(row)
    for value in row:
        print('value: ' + value)
        if value.lower() == 'nan':
            print('Match')