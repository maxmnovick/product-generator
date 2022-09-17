# index-determiner.py 
# determine the index of a field in a table
# using given desired keywords to search for
# so if we know we want to find the price for all vendors but the index varies by vendor, 
# but all vendors call it some variation of "price" so look at what index we see price

desired_field = "price"

acme_price_sheet_headers = ["sku", "east pete price", "collection"]

# find index of price field