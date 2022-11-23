# converter.py
# convert from one type to another, one unit to another, etc

import determiner # to determine a standard key from an arbitrary key given by the user
import reader # to format vendor product data


def convert_all_weights_to_grams(all_init_weights, init_unit='lb'):
    all_weights_in_grams = [] # shopify requires grams
    #print("\n===Convert Weights to Grams===\n")
    for item_idx in range(len(all_init_weights)):
        #item_details = all_details[item_idx]
        #print("item_details: " + str(item_details))
        item_weight = all_init_weights[item_idx]
        #print("item_weight: " + item_weight)
        weight_in_grams = '' # rather be nothing than wrong
        if item_weight != '' and item_weight != 'n/a':
            if init_unit=='lb':
                weight_in_grams = str(float(item_weight) * 453.59237)
            else:
                print("WARNING: Invalid Unit \'" + init_unit + "\'!")
            

        all_weights_in_grams.append(weight_in_grams)

    return all_weights_in_grams


# convert from ['1;2;3','4,5,6']
# to [{'1':'1','2':'2','3':'3'},{'1':'4','2':'5','3':'6'}]
def convert_all_final_item_info_to_json(all_info):
	print("\n===Convert All Final Item Info to JSON===\n")
	print("all_info: " + str(all_info))
	all_json = []

	# Handle;Title;Body (HTML);Vendor;Standardized Product Type;Custom Product Type;Tags;Published;Option1 Name;Option1 Value;Option2 Name;Option2 Value;Option3 Name;Option3 Value;Variant SKU;Variant Grams;Variant Inventory Tracker;Variant Inventory Qty;Variant Inventory Policy;Variant Fulfillment Service;Variant Price;Variant Compare At Price;Variant Requires Shipping;Variant Taxable;Variant Barcode;Image Src;Image Position;Image Alt Text;Variant Image;Variant Weight Unit;Variant Tax Code;Cost per item;Status
	# ['handle','title','body_html','vendor','standard_product_type','product_type','product_tags','published','option1_name', 'option1_value', 'option2_name', 'option2_value', 'option3_name', 'option3_value', 'sku','item_weight_in_grams','vrnt_inv_tracker','vrnt_inv_qty','vrnt_inv_policy','vrnt_fulfill_service','vrnt_price','vrnt_compare_price','vrnt_req_ship','vrnt_taxable','barcode','product_img_src','img_position','img_alt','vrnt_img','vrnt_weight_unit','vrnt_tax_code','item_cost','product_status']
	desired_import_fields = ['handle','title','body_html','vendor','standard_product_type','product_type','product_tags','published','option1_name', 'option1_value', 'option2_name', 'option2_value', 'option3_name', 'option3_value', 'sku','item_weight_in_grams','vrnt_inv_tracker','vrnt_inv_qty','vrnt_inv_policy','vrnt_fulfill_service','vrnt_price','vrnt_compare_price','vrnt_req_ship','vrnt_taxable','barcode','product_img_src','img_position','img_alt','vrnt_img','vrnt_weight_unit','vrnt_tax_code','item_cost','product_status']
	num_fields = len(desired_import_fields)
	print("num_fields in desired_import_fields: " + str(num_fields))

	for item_info in all_info:
		print("item_info: " + str(item_info))
		# 1;2;3
		item_info_list = item_info.split(';') # this always comes in standard format corresponding to desired import fields
		print("item_info_list: " + str(item_info_list))
		num_features = len(item_info_list)
		print("num_features in item_info_list: " + str(num_features))
		item_json = {}
		for field_idx in range(len(desired_import_fields)):
			field = desired_import_fields[field_idx]
			print("field: " + str(field))
			value = item_info_list[field_idx]
			print("value: " + str(value))
			# handle
			item_json[field] = value

		all_json.append(item_json)

	print("all_json: " + str(all_json))

	return all_json


	# convert from all_items_json = [[{'sku':'sku1','collection':'col1'}]]
# to [{'sku':['sku1'],'collection':['col1']}]
def convert_list_of_items_to_fields(all_items_json):

	list_of_fields = []
	all_fields_dict = {}
	
	for sheet in all_items_json:
		print("sheet: " + str(sheet))
		# all_skus = []
		# all_collections = []
		# all_values = []
		for item_json in sheet:
			print("item_json: " + str(item_json))
			# all_skus.append(item_json['sku'])
			# all_collections.append(item_json['collection'])
			for key in item_json:
				standard_key = determiner.determine_standard_key(key)
				formatted_input = reader.format_vendor_product_data(item_json[key], standard_key) # passing in a single value corresponding to key. also need key to determine format.
				if standard_key != '' and formatted_input != '':
					if key in all_fields_dict.keys():
						print("add to existing key")
						all_fields_dict[standard_key].append(formatted_input)
					else:
						print("add new key")
						all_fields_dict[standard_key] = [formatted_input]
		# all_fields_dict['sku'] = all_skus
		# all_fields_dict['collection'] = all_collections
		print("all_fields_dict: " + str(all_fields_dict))
			
		list_of_fields.append(all_fields_dict)

	print("list_of_fields: " + str(list_of_fields))
	return list_of_fields