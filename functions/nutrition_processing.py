import json
import re

import re
import json
import pandas as pd
import plotly.graph_objs as go


def extract_json_string(text):
    # Use regular expression to match content within '```'
    match = re.search(r'```(.*?)```', text, re.DOTALL)
    match_2 = re.search(r'{(.*?)}', text, re.DOTALL)

    if match:
        # Extract the content between the backticks
        json_string = match.group(1)
        return json_string
    elif match_2:
        # Extract the content between the backticks
        json_string = match_2.group(1)
        return json_string
    else:
        # If there's no match, return an empty string
        return ""


def preprocess_and_load_json(response_text):
    """Extract valid JSON key-value pairs from the section of the response text following '```json'."""
    # Remove comments, keeping '//' but removing the rest of the comment
    response_text = re.sub(r'(?<=//).*?(?=\n)', '', response_text)
    response_text = re.sub(r'//', '', response_text)

    # Isolate the portion of the text following '```json'
    json_section = extract_json_string(response_text)
    # Find all matches of key-value pairs in JSON format
    key_value_pairs = re.findall(r'"([^"]+)"\s*:\s*("[^"]+"|\d+\.\d+|\d+)', json_section)
    # Build a dictionary from these key-value pairs
    json_data = {}
    json_data['llm_output'] = response_text
    for key, value in key_value_pairs:
        # Convert numeric values from strings to numbers
        if value.replace('.', '', 1).isdigit():
            value = float(value) #if '.' in value else int(value)
        else:
            value = value.strip('"')

        json_data[key] = value
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

        elif  isinstance(value, (int, float)):
            converted_data[key] = value
        elif isinstance(value, str):

            # if the key is the file name we save the string, otherwise we convert to float.
            if ("name" in key) or ('llm_output' in key) or ('description' in key):
                converted_data[key] = value
            elif  isinstance(value, (int, float)):
                converted_data[key] = value
            else:
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
    glycemic_index_pattern = re.compile(r'\b(glycemic|GI)\b', re.IGNORECASE)
    name_pattern = re.compile(r'\b(name|product|file)\b', re.IGNORECASE)
    description_pattern = re.compile(r'\b(name|product|file)\b', re.IGNORECASE)


    # Initialize values
    
    # nutrients = {
    #     'name':'','weight': 0, 'calories': 0, 'carbohydrates': 0, 'protein': 0, 'fat': 0, 'saturated fat': 0, 
    #     'unsaturated fat': 0, 'sugar': 0, 'fiber': 0, 'cholesterol': 0, 'GI': 0, 'units': 1,
    #     'essential_amino_acids': {}, 'nonessential_amino_acids': {},
    # }
    nutrients={}

    essential_amino_acids = [
    "histidine",
    "isoleucine",
    "leucine",
    "lysine",
    "methionine",
    "phenylalanine",
    "threonine",
    "tryptophan",
    "valine"
]


    nonessential_amino_acids = [
        "alanine",
        "arginine",
        "asparagine",
        "aspartic acid",
        "cysteine",
        "glutamic acid",
        "glutamine",
        "glycine",
        "proline",
        "serine",
        "tyrosine"
    ]


    # Search and aggregate values
    for key, value in json_data.items():
        if carb_pattern.search(key):
            nutrients['carbohydrates'] = value
        if protein_pattern.search(key):
            nutrients['protein'] = value
        if unsat_fat_pattern.search(key):
            nutrients['unsaturated fat'] = value
        elif sat_fat_pattern.search(key):
            nutrients['saturated fat'] = value
        elif fat_pattern.search(key): # and not sat_fat_pattern.search(key) and not unsat_fat_pattern.search(key):
            nutrients['fat'] = value
        if sugar_pattern.search(key):
            nutrients['sugar'] = value
        if fiber_pattern.search(key):
            nutrients['fiber'] = value
        if cholesterol_pattern.search(key):
            nutrients['cholesterol'] = value
        if calorie_pattern.search(key):
            nutrients['calories'] = value
        if weight_pattern.search(key):
            nutrients['weight'] = value
        if glycemic_index_pattern.search(key):
            nutrients['glycemic index'] = value
        if "name" in key:
            nutrients['name'] = value
        if "description" in key:
            nutrients['description'] = value
        if "llm_output" in key:
            nutrients['llm_output'] = value

        # add the amino acids if detected
        if key in essential_amino_acids:
            nutrients[key] = value
        if key in nonessential_amino_acids:
            nutrients[key] = value


    return nutrients



# def extract_amino_acids(json_data):
#     # Define patterns for each category
#     carb_pattern = re.compile(r'\b(carb(s|ohydrates?)?)\b', re.IGNORECASE)
#     protein_pattern = re.compile(r'\b(protein)\b', re.IGNORECASE)


#     # Initialize values
#     nutrients = {
#         'name':'','weight': 0, 'calories': 0, 'carbohydrates': 0, 'protein': 0, 'fat': 0, 'saturated fat': 0, 
#         'unsaturated fat': 0, 'sugar': 0, 'fiber': 0, 'cholesterol': 0, 'GI': 0, 'units': 1
#     }

#     # Search and aggregate values
#     for key, value in json_data.items():
#         if carb_pattern.search(key) and not sugar_pattern.search(key):
#             nutrients['carbohydrates'] = value
#         if protein_pattern.search(key):
#             nutrients['protein'] = value
#         if fat_pattern.search(key):
#             nutrients['fat'] = value
#         if sat_fat_pattern.search(key):
#             nutrients['saturated fat'] = value
#         if unsat_fat_pattern.search(key):
#             nutrients['unsaturated fat'] = value
#         if sugar_pattern.search(key):
#             nutrients['sugar'] += value
#         if fiber_pattern.search(key):
#             nutrients['fiber'] += value
#         if cholesterol_pattern.search(key):
#             nutrients['cholesterol'] += value
#         if calorie_pattern.search(key):
#             nutrients['calories'] += value
#         if weight_pattern.search(key):
#             nutrients['weight'] += value
#             print('weight', value)
#         if glycemic_index_pattern.search(key):
#             nutrients['GI'] += value
#         if "name" in key:
#             nutrients['name'] = value
#         if "llm_output" in key:
#             nutrients['llm_output'] = value


#     return nutrients



def plot_pie_chart(nutrients):
    labels = []
    values = []

    for key, value in nutrients.items():
        labels.append(key.capitalize())
        values.append(value)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text='Nutritional Composition')
    
    fig.show()


def scale_row(row):
    """
    Scales the numerical values in a DataFrame row based on the 'units' value,
    except for columns with string values or columns listed in exempted_variables.

    :param row: A row from a pandas DataFrame.
    :param exempted_variables: A list of column names to be exempted from scaling.
    :return: The modified row with scaled values.
    """

    scaled_row = row.copy()  # Make a copy of the row to avoid modifying the original data

    exempted_variables = ['glycemic index', 'units']

    # Iterate through each column in the row
    for column, value in row.items():
        # Check if the column is not exempted and if the value is int or float
        if column not in exempted_variables and isinstance(value, (int, float)):
            # Scale the value by 'units'
            scaled_row[column] = value * row['units']

    return scaled_row