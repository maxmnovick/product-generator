# intro-generator.py
# create generic templates based on a few different templates for the given product type
# and use lists of interchangeable widely applicable adjectives
# 
# Example intro:
# Original: Got a design emergency? Good news: Spencer is on the job. Available in two of our most popular fabrics for speedier delivery, this track-arm sofa is still sleek, still modern, and still tailored by hand, just the way you'd expect an Ethan Allen sofa to be.
# Generic: <Product Name> is here to help with your design problem. Available in our most popular materials for speedier delivery, this comfortable <product type> is elegant, traditional, and crafted by hand, just the way you would expect a Highly Favored <product type> to be.
#
# Original: Elegant dining is Colette's spécialité—so much so that you'll want to stay en place for hours. From the front, you see a graceful tulip-leaf shape that connects each post. From the side, you see its gently arched back that says "get comfortable." Finish your chair with your choice of hundreds of fabric styles for a look that's exactly what you want.
# Generic: Elegant <room activity> is <Product Name>'s speciality-so much so that you'll want to stay there for hours. From the front, you see a graceful shape that connects each post. From the side, you see its gentle back that is designed for maximum comfort. 
import random

intro = ''

product_type = 'sofa'

pronoun = 'your'

room_type = 'room'

product_name = 'this product'

#seller_name = 'Highly Favored'

room_activity = 'living'

# make map matching product type to room type
if product_type == 'sofa':
    room_type = 'living room'

if room_type == 'room':
    pronoun = 'its'

if product_type == '':
    product_type = 'piece'

intro1 = 'This exceptional ' + product_type + ' will make ' + pronoun + ' ' + room_type + ' the most delightful room in your home. '

intro2 = str.capitalize(product_name) + ' is here to help with your design problem. Available in our most popular materials for speedier delivery, this comfortable ' + product_type + ' is elegant, traditional, and crafted by hand, just the way you would expect our ' + product_type + ' to be.'

intro3 = 'Elegant ' + room_activity + ' is ' + product_name + '\'s speciality—so much so that you\'ll want to stay there for hours. From all sides, you see a graceful shape that is perfectly balanced and sturdy while staying lightweight. '

intro_templates = [intro1, intro2, intro3]

intro = random.choice(intro_templates)

print(intro)