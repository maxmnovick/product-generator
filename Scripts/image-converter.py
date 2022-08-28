# image-converter.py
# convert image format from webp to jpg so it can be resized

from PIL import Image, ImageOps

from resizeimage import resizeimage

im = Image.open("../Data/product-images/example.webp")

# get image dimensions so we can see if size needs to increase or decrease
init_width, init_height = im.size
print("init_width: " + str(init_width))
print("init_height: " + str(init_height))

final_width = init_width
final_height = init_height

set_side_length = 2048

contain_img = False # contain img if larger than set side length

# if image square then we do not need border
if init_width == init_height:
    final_width = final_height = set_side_length

elif init_width > init_height:
    final_width = set_side_length
    size_change_factor = init_width / final_width
    final_height = round(init_height / size_change_factor)

    if init_width > set_side_length:
        contain_img = True

elif init_width < init_height:
    final_height = set_side_length
    size_change_factor = init_height / final_height
    final_width = round(init_width / size_change_factor)

    if init_height > set_side_length:
        contain_img = True

# if image width below 2048px, we do not necessarily want to increase width directly to 2048px,
# because the height could then go above 2048px, which is not allowed
# so if the height would increase above 2048px, then we need to check height before changing width
# if the height would not go above 2048px by increasing width to 2048, then we still want to make width 2048 and fill space above and below image with fill color

print("final_width no border: " + str(final_width))
print("final_height no border: " + str(final_height))

im_with_border = im
# if longer side is greater than set side length, contain img
# example: PIL.ImageOps.contain(image, size, method=Resampling.BICUBIC)
if contain_img:
    print("\n===Contain Image===\n")
    im_with_border = ImageOps.contain(im, (set_side_length, set_side_length), Image.Resampling.LANCZOS)
# else if larger side is less than set side length, expand img

#im.resize((final_width, final_height), Image.Resampling.LANCZOS)

# either one or both of these borders will be 0 bc the larger side will be equal to set side length
width_border = round(abs(final_width - set_side_length) / 2)
height_border = round(abs(final_height - set_side_length) / 2)
print("width_border: " + str(width_border))
print("height_border: " + str(height_border))

#im_with_border = resizeimage.resize_contain(im, [set_side_length, set_side_length], True, (255, 0, 0, 1))

#im_with_border = ImageOps.expand(im, border=300, fill='black')

im_with_border = ImageOps.expand(im_with_border, border=(width_border, height_border), fill='black')
#im_with_border.resize((set_side_length, set_side_length))
#im.show() # for testing purposes
im_with_border.show()

print("final_width: " + str(final_width+2*width_border))
print("final_height: " + str(final_height+2*height_border))

# save the converted and resized image
im_with_border.save("../Data/product-images/example.jpg", im_with_border.format) # see if we can resize in webp format then we do not need to convert