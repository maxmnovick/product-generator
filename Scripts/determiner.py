# determiner.py
# determine choices with complicated conditions

import re

def determine_matching_field(desired_field_name, current_field_name):
    print("desired_field_name: " + desired_field_name)
    print("current_field_name: " + current_field_name)

def determine_standard_key(raw_key):
    standard_key = ''

    all_field_keywords = { 
        'sku':['sku','item#'], 
        'collection':['collection'],
        'features':['features','acme.description'],
        'type':['product type','description'],
        'intro':['intro','short description'],
        'color':['color'],
        'material':['material'],
        'finish':['finish'],
        'width':['width'],
        'depth':['depth','length'],
        'height':['height'],
        'weight':['weight'],
        'cost':['cost','price'],
        'images':['image'],
        'barcode':['barcode']
    }

    for field_key, field_keywords in all_field_keywords.items():
        print("field_key, field_keywords: " + field_key + ", " + str(field_keywords))
        for keyword in field_keywords:
            if re.search(keyword, raw_key):
                print("keyword " + keyword + " in raw_key " + raw_key)
                standard_key = field_key
                break
        if standard_key != '':
            break

    print("standard_key: " + standard_key)
    return standard_key

def determine_field_name(field, sheet_df):
    print("\n===Determine Field Name: " + field + "===\n")
    sheet_headers = sheet_df.columns.values

    field_keywords = { 
        'sku':['sku','item#'], 
        'collection':['collection'],
        'features':['features','acme.description'],
        'type':['product type','description'],
        'intro':['intro','short description'],
        'color':['color'],
        'material':['material'],
        'finish':['finish'],
        'width':['width'],
        'depth':['depth','length'],
        'height':['height'],
        'weight':['weight'],
        'cost':['cost','price'],
        'images':['image'],
        'barcode':['barcode']
    }
    keywords = field_keywords[field]
    matching_field = False
    field_name = ''
    for keyword in keywords:
        for header in sheet_headers:
            header_no_space = re.sub('(\s+|_)','',header.lower()) # unpredictable typos OR format in headers given by vendor such as 'D E S C R I P T I O N'
            keyword_no_space = re.sub('\s', '', keyword)
            if re.search(keyword_no_space, header_no_space):
                field_name = header
                print("field_name: " + field_name)
                matching_field = True
                break
        if matching_field:
            break
    return field_name