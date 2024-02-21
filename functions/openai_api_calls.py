from openai import OpenAI
import base64
import json
import re
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash

from functions.nutrition_processing import *

### openai key
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# Set the environment variable
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
####

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def openai_vision_call(image, textprompt=None, prompt_type='macros', weight=None, protein=None):

    if prompt_type == 'macros':
        prompt = """Lets play a game: If there is a food item in this picture: lets try to estimate the serving size together and lets see if we can estimate or look up the nutritional values (in grams or kcal) of the food (serving size in picture; 
            {'name item': ,
            'grams in picture': ,
            'total calories (kcal)': , 
            'carbohydrates (g): , 
            'of which sugar (g)': ,
            'fiber (g)': ,
            'protein (g)':  ,
            'total fat (g)': , 
            'saturated fat (g)': 
            'unsaturated fat (g)': ,
            'cholesterol (g): ,
            'glycemic index (GI)': ,
            } Only output a single value per property, no ranges. And format output in a json."""
        
        if textprompt is not None:
            prompt = prompt + f""" Some additional information about this image is that it contains: {textprompt}"""

    elif prompt_type == 'amino_acids':

        prompt = (f"Lets play a game: If there is a food item in this picture f{textprompt}: lets try to estimate the amount of amino acids this this food contains. We estimate it weighs {weight}g and contains {protein}g of protein. I know this is difficult but you it is critical you estimate a miligram value per amino acid. Only respond with  miligram values in this following json format table:"+
            """{"essential amino acids":{
                    "histidine": , 
                    "isoleucine" , 
                    "leucine", 
                    "lysine", 
                    "methionine", 
                    "phenylalanine", 
                    "threonine", 
                    "tryptophan", 
                    "valine" },
            "non essential amino acids":{
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
            "tyrosine",
                }
                } 
            """)
    

    # Check if the input is likely a file path and not an image. 
    if len(image) < 500:  # Assuming file paths will be shorter than 500 characters
        image = encode_image(image)

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) 

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",  # Assuming stored_image is just the base64 string
                        "detail": "low"

                }
                }
            ]
            }
        ],
        max_tokens=360,
    )


    text = response.choices[0].message.content
    message = text.split('```'[0]) # llm output
    json_data = preprocess_and_load_json(text)

    json_grams = convert_to_grams(json_data)
    # extract nutritional data in standardised format
    json_nutrition = extract_nutrition(json_grams)
    

    return json_nutrition, message
    # return None