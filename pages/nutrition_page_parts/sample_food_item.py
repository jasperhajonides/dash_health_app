
from datetime import datetime

def search_item_database(selected_row):

    # Search for the input text in the dataframe
    if not selected_row.empty:                # Process the match to get nutritional values
        # try:
        today_str = datetime.now().strftime('%Y%m%d_%HH:%MM')

        match = selected_row.iloc[0]
        json_entry = {
            'protein': match['Protein (g)'],
            'fat': match['Fat (g)'],
            'carbohydrates': match['Carbohydrate (g)'],
            'sugar (g)': match['Total sugars (g)'],
            'fiber (g)': match['AOAC fibre (g)'],
            'calories': match['Energy (kcal) (kcal)'],
            'weight': '100',
            'saturated fat': match['Satd FA /100g fd (g)'],
            'unsaturated fat': match['Mono FA /100g food (g)'], #+ float(match['Poly FA /100g food (g)']),
            'name':  match['Food Name'],
        }
    else:
        json_entry = {'message': 'No matches found'}

    return json_entry

