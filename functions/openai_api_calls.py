from openai import OpenAI
import base64
import json
import re
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash



### openai key
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("API_KEY")
# Set the environment variable
os.environ["OPENAI_API_KEY"] = api_key
####

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def openai_vision_call(image, textprompt=None):

    prompt = """Lets play a game: If there is a food item in this picture: lets try to estimate the serving size together and lets see if we can estimate or look up the nutritional values (in grams or kcal) of the food (serving size in picture; 
        {'name item': ,
        'grams in picture': ,
        'total calories (kcal)': , 
        'carbohydrates (g): , 
        'of which sugar (g)': ,
        'fiber (g)': ,
        'protein (g)':  , 
        'saturated fat (g)': 
        'unsaturated fat (g)': ,
        'cholesterol (g): ,
        } Only output a single value per property, no ranges. And format output in a json."""
    if textprompt is not None:
        print('ADDING ADDITIONAL INSTRUCTIONS:::::::', textprompt)
        prompt = prompt + f""" Some additional information about this image is that it contains: {textprompt}"""


    # Check if the input is likely a file path
    if len(image) < 500:  # Assuming file paths will be shorter than 500 characters
        image = encode_image(image)

    api_key = os.getenv("API_KEY")
    print(api_key)
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

    print('print api output:', response)

    text = response.choices[0].message.content
    print(text)

    return text
    # return None