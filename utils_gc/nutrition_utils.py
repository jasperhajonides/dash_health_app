# utils/nutrition_utils.py
import json
import dash
from dash import html
import base64
# Import your nutrition module (ensure it's in your PYTHONPATH or same directory)
# Adjust the import statements based on your actual module names and structure
import sys
sys.path.append('/Users/jasperhajonides/Documents/Projects/website/dash_health_app/llm_code')
from llm_code.nutrition_api_calls import NutritionExtraction
from llm_code.prompt_generation import PromptGenerator



def get_nutritional_info(base64_image, description='', detail='core'):

    # Initialize nutrition class
    nutrition = NutritionExtraction(detail=detail)

    # Prepare the prompt for the nutritional analysis
    pg = PromptGenerator(nutrition_class=nutrition)
    prompts = pg.generate_prompts(name_input='food', weight_input=100)

    if description:
        prompts['image_text_prompt'] += f' The item in the picture is a {description}'


    # Call your nutritional analysis function
    try:
        stored_image_data = base64_image  # Base64 image data
                

        json_nutrition_std, missing_keys = nutrition.openai_api_image(
            prompt=prompts['image_text_prompt'],
            image=stored_image_data,
            n=1
        )

        # post process json
        json_nutrition_std = post_process_nutritional_info(json_nutrition_std, prompts['image_text_prompt'])

        return json_nutrition_std
    except Exception as e:
        print(f"Error in nutritional analysis: {str(e)}")
        return None

def adjust_nutritional_weight_values(json_entry, weight_input):
    # Define keys to exclude from adjustments
    EXCLUDED_KEYS = ['glycemic_index', 'glycemic index','name', 'description', 'meal_type', 'units', 'weight_original']

    # Extract and validate weight from json_entry
    json_weight = max(json_entry.get('weight', 100), 1)  # Ensure weight is at least 1

    # Calculate adjustment factor based on weight input
    factor = weight_input / json_weight

    # Dynamically adjust values based on factor, excluding specified keys
    for key, value in json_entry.items():
        if key not in EXCLUDED_KEYS and isinstance(value, (int, float)):
            json_entry[key] = round(value * factor,3)

    # Update the weight in the json_entry
    json_entry['weight'] = weight_input

    return json_entry

def display_nutritional_info(json_entry):
    if not json_entry:
        return html.Div("No nutritional data available.")

    # Format the nutritional information for display
    nutrition_info = json.dumps(json_entry, indent=2)
    return html.Pre(nutrition_info)

def post_process_nutritional_info(json_entry, prompt):
    """
    Add details to the json, after the initial calculation. 
    
    This includes combining values together or re-writing columns into new names.
    
    Input:
    json_entry (json): json with all nutritional values
    prompt (str): prompt string

    Output:
    json with same variables but others added.
    """

    json_entry['weight_original'] = json_entry['weight']
    json_entry['prompt'] = prompt
    if 'saturated fat' in json_entry and 'unsaturated fat' in json_entry:
        json_entry['triglycerides'] = json_entry['saturated fat'] + json_entry['unsaturated fat']

    return json_entry