# acme-catalog-generator.py
# input: acme spec sheet and price sheet separately
# output: acme catalog with standard catalog headers, ready to go to product generator

#from re import A
import reader, writer, pandas

# to generalize this generator process
# ask for input sheets (loop until user says done bc could have multiple sheets), 
# details to find each sheet, and fields in each sheet
# then ask desired output fields
vendor = "acme" # tells us they have x no. sheets and what is in each sheet (data_type)

# init index variables to be used to get field values for calculations
# how do we decide which vars to init before considering vendor? do we need to init all possible and leave some blank if not used by vendor?
price_sheet_catalog_yr_idx = 0
price_sheet_catalog_page_idx = 1
price_sheet_sku_idx = 2
price_sheet_descrip_idx = 3
price_sheet_price_idx = 4
price_sheet_one_set_ctn_idx = 5
price_sheet_pc_ctn_idx = 6
price_sheet_ct_lb_idx = 7
price_sheet_ct_cuft_idx = 8
price_sheet_coll_name_idx = 9

# spec sheet indexes
spec_sheet_name_idx = 0
spec_sheet_sku_idx = 1
spec_sheet_product_wt_idx = 2
spec_sheet_product_length_idx = 3
spec_sheet_product_width_idx = 4
spec_sheet_product_height_idx = 5
spec_sheet_package_length_idx = 6
spec_sheet_pacakge_width_idx = 7
spec_sheet_package_height_idx = 8
spec_sheet_package_weight_idx = 9
spec_sheet_coll_name_idx = 12
spec_sheet_product_type_idx = 14
spec_sheet_features_idx = 15
spec_sheet_descrip_idx = 16
spec_sheet_finish_idx = 17
spec_sheet_material_idx = 18

# image sheet indexes
img_sheet_sku_idx = 0
img_sheet_links_idx = 1

# price sheet indexes, order of fields
if vendor == 'acme':
    #sample_price_sheet = [[catalog_yr, catalog_page, item_num, descrip, price, one_set_ctn, pc_ctn, ctn_lb, carton_cuft, collection_name]]
    price_sheet_catalog_yr_idx = 0
    price_sheet_catalog_page_idx = 1
    price_sheet_sku_idx = 2
    price_sheet_descrip_idx = 3
    price_sheet_price_idx = 4
    price_sheet_one_set_ctn_idx = 5
    price_sheet_pc_ctn_idx = 6
    price_sheet_ct_lb_idx = 7
    price_sheet_ct_cuft_idx = 8
    price_sheet_coll_name_idx = 9

    # spec sheet indexes
    spec_sheet_name_idx = 0
    spec_sheet_sku_idx = 1
    spec_sheet_product_wt_idx = 2
    spec_sheet_product_length_idx = 3
    spec_sheet_product_width_idx = 4
    spec_sheet_product_height_idx = 5
    spec_sheet_package_length_idx = 6
    spec_sheet_pacakge_width_idx = 7
    spec_sheet_package_height_idx = 8
    spec_sheet_package_weight_idx = 9
    spec_sheet_coll_name_idx = 12
    spec_sheet_product_type_idx = 14
    spec_sheet_features_idx = 15
    spec_sheet_descrip_idx = 16
    spec_sheet_finish_idx = 17
    spec_sheet_material_idx = 18

    # image sheet indexes
    img_sheet_sku_idx = 0
    img_sheet_links_idx = 1

ext = "tsv"

# read and extract data for each given data sheet, such as price sheet, spec sheet, and img sheet which may be given in separate files, relational tables (related by sku)

# General Info from price table
print("\n====== Read Price Sheet ======\n")

data_type = "price sheet"

# remove leading zeros from sku in price list to match sku in spec sheet
price_sheet = reader.extract_data(vendor, ext, data_type)
#price_sheet = sample_price_sheet
filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
print("filepath: " + filepath)
price_sheet_df = pandas.read_table(filepath).fillna('n/a')
print("price_sheet_df:\n" + str(price_sheet_df))
price_sheet_df.columns = price_sheet_df.columns.str.strip() # remove excess spaces
print(price_sheet_df.columns.values)



# OPTION 1: loop thru with field idx
all_price_sheet_skus = []
all_price_sheet_prices = []
for price_sheet_item in price_sheet: 
    
    sku = price_sheet_item[price_sheet_sku_idx].strip().lstrip("0")
    print("sku: " + sku)
    price = price_sheet_item[price_sheet_price_idx].replace("$","").replace(",","").strip() # double strip bc comes in format with space bt dollar sign and number
    print("price: " + price)

    all_price_sheet_skus.append(sku)
    all_price_sheet_prices.append(price)

# header names given by vendor, rather than determining index
price_sheet_sku_name = "sku"
price_sheet_price_name = "price"
if vendor == 'acme':
    price_sheet_sku_name = 'Item#'
    price_sheet_price_name = '2022   EAST PETE PRICE'

# OPTION 2: use pandas dataframe series to list
all_price_sheet_skus = price_sheet_df[price_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
print("all_price_sheet_skus: " + str(all_price_sheet_skus))
all_price_sheet_prices = price_sheet_df[price_sheet_price_name].astype('string').str.replace("$","").str.replace(",","").str.strip().tolist()
print("all_price_sheet_prices: " + str(all_price_sheet_prices))

# look for file in Data folder called acme-spec-sheet.tsv
print("\n====== Read Spec Sheet ======\n")
data_type = "spec sheet"
spec_sheet = reader.extract_data(vendor, ext, data_type)
#sample_spec_sheet = [name, sku, product_weight, product_length, product_width, product_height, package_length, package_width, package_height, package_weight, ship_type, package_type, collection_name, catalog, product_type, description, short_description, catalog_finish, material_detail, fl_qty, ga_qty, nj_qty, ny_qty, tx_qty, la_qty, sf_qty, msrp, eta_la_warehouse, group, video] # acme provides values with these keynames so look for these words or just assume they come in this order but that may cause future errors
#spec_sheet = sample_spec_sheet
filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
print("filepath: " + filepath)
spec_sheet_df = pandas.read_table(filepath).fillna('n/a')
print("spec_sheet_df:\n" + str(spec_sheet_df))
spec_sheet_df.columns = spec_sheet_df.columns.str.strip() # remove excess spaces
print(spec_sheet_df.columns.values)

all_spec_sheet_skus = []
all_spec_sheet_weights = []
all_spec_sheet_lengths = []
all_spec_sheet_widths = []
all_spec_sheet_heights = []
all_spec_sheet_coll_names = []
all_spec_sheet_product_types = []
all_spec_sheet_features = []
all_spec_sheet_descrips = []
all_spec_sheet_finishes = []
all_spec_sheet_materials = []

for spec_sheet_item in spec_sheet:

    sku = spec_sheet_item[spec_sheet_sku_idx].strip()
    weight = spec_sheet_item[spec_sheet_product_wt_idx].strip()
    length = spec_sheet_item[spec_sheet_product_length_idx].strip()
    width = spec_sheet_item[spec_sheet_product_width_idx].strip()
    height = spec_sheet_item[spec_sheet_product_height_idx].strip()
    coll_name = spec_sheet_item[spec_sheet_coll_name_idx].strip()
    product_type = spec_sheet_item[spec_sheet_product_type_idx].strip()
    features = spec_sheet_item[spec_sheet_features_idx].strip().replace(";",".")
    descrip = spec_sheet_item[spec_sheet_descrip_idx].strip()
    finish = spec_sheet_item[spec_sheet_finish_idx].strip()
    material = spec_sheet_item[spec_sheet_material_idx].strip()

    all_spec_sheet_skus.append(sku)
    all_spec_sheet_weights.append(weight)
    all_spec_sheet_lengths.append(length)
    all_spec_sheet_widths.append(width)
    all_spec_sheet_heights.append(height)
    all_spec_sheet_coll_names.append(coll_name)
    all_spec_sheet_product_types.append(product_type)
    all_spec_sheet_features.append(features)
    all_spec_sheet_descrips.append(descrip)
    all_spec_sheet_finishes.append(finish)
    all_spec_sheet_materials.append(material)

# header names given by vendor, rather than determining index
spec_sheet_sku_name = "sku"
spec_sheet_weight_name = 'weight'
spec_sheet_length_name = 'length'
spec_sheet_width_name = 'width'
spec_sheet_height_name = 'height'
spec_sheet_coll_name = 'collection name'
spec_sheet_type_name = 'type'
spec_sheet_features_name = 'features'
spec_sheet_descrip_name = 'description'
spec_sheet_finish_name = 'finish'
spec_sheet_material_name = 'material'
if vendor == 'acme':
    spec_sheet_sku_name = 'acme.sku'
    spec_sheet_weight_name = 'acme.product_weight'
    spec_sheet_length_name = 'acme.product_length'
    spec_sheet_width_name = 'acme.product_width'
    spec_sheet_height_name = 'acme.product_height'
    spec_sheet_coll_name = 'acme.collection_name'
    spec_sheet_type_name = 'acme.product_type'
    spec_sheet_features_name = 'acme.description'
    spec_sheet_descrip_name = 'acme.short_description'
    spec_sheet_finish_name = 'acme.catalog_finish'
    spec_sheet_material_name = 'acme.material_detail'

# OPTION 2: use pandas dataframe series to list
all_spec_sheet_skus = spec_sheet_df[spec_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
print("all_spec_sheet_skus: " + str(all_spec_sheet_skus))
all_spec_sheet_weights = spec_sheet_df[spec_sheet_weight_name].astype('string').str.strip().tolist()
print("all_spec_sheet_weights: " + str(all_spec_sheet_weights))
all_spec_sheet_lengths = spec_sheet_df[spec_sheet_length_name].astype('string').str.strip().tolist()
print("all_spec_sheet_lengths: " + str(all_spec_sheet_lengths))
all_spec_sheet_widths = spec_sheet_df[spec_sheet_width_name].astype('string').str.strip().tolist()
print("all_spec_sheet_widths: " + str(all_spec_sheet_widths))
all_spec_sheet_heights = spec_sheet_df[spec_sheet_height_name].astype('string').str.strip().tolist()
print("all_spec_sheet_heights: " + str(all_spec_sheet_heights))
all_spec_sheet_coll_names = spec_sheet_df[spec_sheet_coll_name].astype('string').str.strip().tolist()
print("all_spec_sheet_coll_names: " + str(all_spec_sheet_coll_names))
all_spec_sheet_types = spec_sheet_df[spec_sheet_type_name].astype('string').str.strip().tolist()
print("all_spec_sheet_types: " + str(all_spec_sheet_types))
all_spec_sheet_features = spec_sheet_df[spec_sheet_features_name].astype('string').str.strip().str.replace(";",".").tolist()
print("all_spec_sheet_features: " + str(all_spec_sheet_features))
all_spec_sheet_descrips = spec_sheet_df[spec_sheet_descrip_name].astype('string').str.strip().tolist()
print("all_spec_sheet_descrips: " + str(all_spec_sheet_descrips))
all_spec_sheet_finishes = spec_sheet_df[spec_sheet_finish_name].astype('string').str.strip().tolist()
print("all_spec_sheet_finishes: " + str(all_spec_sheet_finishes))
all_spec_sheet_materials = spec_sheet_df[spec_sheet_material_name].astype('string').str.strip().tolist()
print("all_spec_sheet_materials: " + str(all_spec_sheet_materials))

# look for file in Data folder called acme-image-links.tsv
print("\n====== Read Image Sheet ======\n")
data_type = "image links"
img_sheet = reader.extract_data(vendor, ext, data_type)
#sample_spec_sheet = [name, sku, product_weight, product_length, product_width, product_height, package_length, package_width, package_height, package_weight, ship_type, package_type, collection_name, catalog, product_type, description, short_description, catalog_finish, material_detail, fl_qty, ga_qty, nj_qty, ny_qty, tx_qty, la_qty, sf_qty, msrp, eta_la_warehouse, group, video] # acme provides values with these keynames so look for these words or just assume they come in this order but that may cause future errors
#spec_sheet = sample_spec_sheet
filepath = "../Data/" + vendor + "-" + data_type.replace(" ","-") + "." + ext
print("filepath: " + filepath)
img_sheet_df = pandas.read_table(filepath).fillna('n/a')
print("img_sheet_df:\n" + str(img_sheet_df))
img_sheet_df.columns = img_sheet_df.columns.str.strip() # remove excess spaces
print(img_sheet_df.columns.values)

all_img_sheet_skus = []
all_img_sheet_links = []

for item in img_sheet:

    sku = item[img_sheet_sku_idx].strip()
    image_links = item[img_sheet_links_idx].strip().lstrip("[").rstrip("]")

    all_img_sheet_skus.append(sku)
    all_img_sheet_links.append(image_links)


# header names given by vendor, rather than determining index
img_sheet_sku_name = "sku"
img_sheet_links_name = "image links"
if vendor == 'acme':
    img_sheet_sku_name = 'acme.sku'
    img_sheet_links_name = 'Image Array'

# OPTION 2: use pandas dataframe series to list
all_img_sheet_skus = img_sheet_df[img_sheet_sku_name].astype('string').str.strip().str.lstrip("0").tolist()
print("all_img_sheet_skus: " + str(all_img_sheet_skus))
all_img_sheet_links = img_sheet_df[img_sheet_links_name].astype('string').str.strip().str.lstrip("[").str.rstrip("]").tolist()
print("all_img_sheet_links: " + str(all_img_sheet_links))

# ====== Generate Vendor Catalog ======
print("\n====== Generate Vendor Catalog ======\n")

# for each item in spec sheet, see if there is a price.
# if there is a price, then proceed.
# if there is no price, then skip the product and flag it with warning
# OR
# for each item in price list get specs, bc there are less items in price list so less loops so more efficient potentially

def display_all_catalog_info():

    print("\n === Display Catalog Info === \n")

    all_catalog_info = []

    for product_idx in range(len(price_sheet)):
        product = price_sheet[product_idx]

        price_sheet_sku = all_price_sheet_skus[product_idx] # use this to match with spec and image sheets
        cost = all_price_sheet_prices[product_idx]

        # init vars from spec sheet 
        coll_name = ""
        product_type = ""
        intro = ""
        color = ""
        material = ""
        finish = "" 
        length = ""
        width = ""
        height = ""
        weight = ""
        features = ""
        barcode = ""
        # and img sheet
        img_links = ""

        for spec_sheet_item_idx in range(len(all_spec_sheet_skus)):
            spec_sheet_sku = all_spec_sheet_skus[spec_sheet_item_idx]
            print("spec_sheet_sku: " + spec_sheet_sku)

            if price_sheet_sku == spec_sheet_sku:
                # get specs for this product
                coll_name = all_spec_sheet_coll_names[spec_sheet_item_idx]
                print("coll_name: " + coll_name)
                product_type = all_spec_sheet_product_types[spec_sheet_item_idx]
                print("product_type: " + product_type)
                intro = all_spec_sheet_descrips[spec_sheet_item_idx]
                print("intro: " + intro)
                color = all_spec_sheet_finishes[spec_sheet_item_idx] 
                print("color: " + color)
                material = all_spec_sheet_materials[spec_sheet_item_idx] 
                print("material: " + material)
                finish = "" # todo: acme gives finish and color together so separate them
                length = all_spec_sheet_lengths[spec_sheet_item_idx] 
                print("length: " + length)
                width = all_spec_sheet_widths[spec_sheet_item_idx]
                print("width: " + width)
                height = all_spec_sheet_heights[spec_sheet_item_idx]
                print("height: " + height)
                weight = all_spec_sheet_weights[spec_sheet_item_idx]
                print("weight: " + weight)
                features = all_spec_sheet_features[spec_sheet_item_idx] 
                print("features: " + features)
                barcode = ""

                break

        image_given = False
        for img_sheet_item_idx in range(len(all_img_sheet_skus)):
            img_sheet_sku = all_img_sheet_skus[img_sheet_item_idx]

            if price_sheet_sku == img_sheet_sku:
                # get imgs for this product
                img_links = all_img_sheet_links[img_sheet_item_idx]
                print("img_links: " + img_links)
                if img_links != '' and img_links.lower() != 'n/a':
                    image_given = True
                break

        # only add product with image
        if image_given:

            catalog_info = price_sheet_sku + ";" + coll_name + ";" + product_type + ";" + intro + ";" + color + ";" + material + ";" + finish + ";" + length + ";" + width + ";" + height + ";" + weight + ";" + features + ";" + cost + ";" + img_links + ";" + barcode

            all_catalog_info.append(catalog_info)

        else:
            print("Warning: No image given so product not uploaded!")
        
    writer.display_catalog_headers()
    for item_info in all_catalog_info:
        print(item_info)

    return all_catalog_info


all_final_catalog_info = display_all_catalog_info()

#writer.write_data(all_catalog_info, vendor, output, extension)