import json
import re

import re
import json

def preprocess_and_load_json(response_text):
    """Extract valid JSON key-value pairs from the section of the response text following '```json'."""

    # Isolate the portion of the text following '```json'
    json_section = response_text.split('```json')[-1]

    # Find all matches of key-value pairs in JSON format
    key_value_pairs = re.findall(r'"([^"]+)"\s*:\s*("[^"]+"|\d+|\d+\.\d+)', json_section)
    print('json_section',json_section)
    # Build a dictionary from these key-value pairs
    json_data = {}
    for key, value in key_value_pairs:
        # # Convert numeric values from strings to numbers
        # if value.replace('.', '', 1).isdigit():
        #     value = float(value) if '.' in value else int(value)
        # else:
        #     value = value.strip('"')

        json_data[key] = value
    print(json_data)
    return json_data

def convert_to_grams(json_data):
    """ 
    Convert json dict to contain all numbers as values, in the right unit. 
    """
    converted_data = {}


    for key, value in json_data.items():
        if isinstance(value, dict):
            # Recursively handle nested dictionaries
            converted_value = convert_to_grams(value)
            if converted_value:  # Only add if the nested dictionary is not empty
                converted_data[key] = converted_value
        elif isinstance(value, str):
            # Extract the numerical part of the value
            try:
                num = float(''.join(filter(lambda x: x.isdigit() or x == '.', value)))
                # Check the unit and convert if necessary
                if 'mg' in value.lower():
                    num /= 1000  # Convert from mg to g
                elif any(μg_indicator in value.lower() for μg_indicator in ['μg', 'mcg', 'ug']):
                    num /= 1e6  # Convert from μg to g
                # Add the key-value pair to the converted data
                converted_data[key] = num
            except ValueError:
                # Discard the key-value pair if the conversion is not possible
                pass
    print('convert to grams output:', converted_data)

    return converted_data
      
import re

def extract_nutrition(json_data):
    # Define patterns for each category
    carb_pattern = re.compile(r'\b(carb(s|ohydrates?)?)\b', re.IGNORECASE)
    protein_pattern = re.compile(r'\b(protein)\b', re.IGNORECASE)
    fat_pattern = re.compile(r'\b(fat)\b', re.IGNORECASE)
    sat_fat_pattern = re.compile(r'\b(saturated fat)\b', re.IGNORECASE)
    unsat_fat_pattern = re.compile(r'\b(unsaturated fat)\b', re.IGNORECASE)
    sugar_pattern = re.compile(r'\b(sugar(s)?)\b', re.IGNORECASE)
    fiber_pattern = re.compile(r'\b(fiber)\b', re.IGNORECASE)
    cholesterol_pattern = re.compile(r'\b(cholesterol)\b', re.IGNORECASE)
    calorie_pattern = re.compile(r'\b(calories|kcal)\b', re.IGNORECASE)
    weight_pattern = re.compile(r'\b(weight|grams of|portion size|serving size|grams in)\b', re.IGNORECASE)

    # Initialize values
    nutrients = {
        'weight': 0, 'calories': 0, 'carbohydrates': 0, 'protein': 0, 'fat': 0, 'saturated fat': 0, 
        'unsaturated fat': 0, 'sugar': 0, 'fiber': 0, 'cholesterol': 0
    }

    # Search and aggregate values
    for key, value in json_data.items():
        if carb_pattern.search(key) and not sugar_pattern.search(key):
            nutrients['carbohydrates'] += value
        if protein_pattern.search(key):
            nutrients['protein'] += value
        if fat_pattern.search(key):
            nutrients['fat'] += value
        if sat_fat_pattern.search(key):
            nutrients['saturated fat'] += value
        if unsat_fat_pattern.search(key):
            nutrients['unsaturated fat'] += value
        if sugar_pattern.search(key):
            nutrients['sugar'] += value
        if fiber_pattern.search(key):
            nutrients['fiber'] += value
        if cholesterol_pattern.search(key):
            nutrients['cholesterol'] += value
        if calorie_pattern.search(key):
            nutrients['calories'] += value
        if weight_pattern.search(key):
            nutrients['weight'] += value

    print('in extract_nutrition function we output:', nutrients)

    return nutrients


def plot_pie_chart(nutrients):
    labels = []
    values = []

    for key, value in nutrients.items():
        labels.append(key.capitalize())
        values.append(value)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text='Nutritional Composition')
    
    fig.show()
