# compute overall bed dimensions from part dimensions

import re

# headboard
headboard_dims = " 	41.93\" W x 3.74\" D x 60.67\" H"
print("headboard_dims: " + headboard_dims)
headboard_width = re.search("(\S+)\"\sW", headboard_dims).group(1)
print("headboard_width: " + headboard_width)
headboard_depth = re.search("(\S+)\"\sD", headboard_dims).group(1)
print("headboard_depth: " + headboard_depth)
headboard_height = re.search("(\S+)\"\sH", headboard_dims).group(1)
print("headboard_height: " + headboard_height)

# footboard
footboard_dims = " 	42.09\" W x 0.63\" D x 14.84\" H"
footboard_width = re.search("(\S+)\"\sW", footboard_dims).group(1)
footboard_depth = re.search("(\S+)\"\sW", footboard_dims).group(1)
footboard_height = re.search("(\S+)\"\sW", footboard_dims).group(1)

# rails
rail_dims = " 	40\" W x 76.77\" D x 7.17\" H"
rail_width = re.search("(\S+)\"\sW", rail_dims).group(1)
rail_depth = re.search("(\S+)\"\sW", rail_dims).group(1)
rail_height = re.search("(\S+)\"\sW", rail_dims).group(1)

bed_width = headboard_width
bed_depth = str(round(float(headboard_depth) + float(rail_depth) + float(footboard_depth),2))
bed_height = headboard_height

bed_dims = bed_width + "\" W x " + bed_depth + "\" D x " + bed_height + "\" H"
print("bed_dims: " + bed_dims)
