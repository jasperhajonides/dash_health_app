
from datetime import datetime
import numpy as np

from functions.nutrition_processing import *

def search_item_database(selected_row):

    # Search for the input text in the dataframe
    if not selected_row.empty:                # Process the match to get nutritional values
        # try:
        today_str = datetime.now().strftime('%Y%m%d_%HH:%MM')

        # we'd like to convert all nutritional entries from the csv to floats. If not possible we put None. Later on we remove all keys with value none. 
        convert_or_none = lambda x: try_convert_to_float(x)

        def try_convert_to_float(x):
            if isinstance(x, str):
                try:
                    return float(x)
                except ValueError:
                    return None
            return None
        

        match = selected_row.iloc[0]
        json_entry = {
            'protein': convert_or_none(match['Protein (g)']),
            'fat': convert_or_none(match['Fat (g)']),
            'carbohydrates': convert_or_none(match['Carbohydrate (g)']),
            'sugar': convert_or_none(match['Total sugars (g)']),
            'fiber': convert_or_none(match['AOAC fibre (g)']),
            'calories': convert_or_none(match['Energy (kcal) (kcal)']),
            'weight': 100,
            'saturated fat': convert_or_none(match['Satd FA /100g fd (g)']),
            'unsaturated fat': convert_or_none(match['Mono FA /100g food (g)']), #+ float(match['Poly FA /100g food (g)']),
            'name': match['Food Name'],
        }

        # Remove entries with value None
        json_entry = {k: v for k, v in json_entry.items() if v is not None}


    else:
        json_entry = {'message': 'No matches found'}

    print('JSON ENTRY FROM SAMPLE FOOD ITEM')
    return json_entry

