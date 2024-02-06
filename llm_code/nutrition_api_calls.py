import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
# Set the environment variable
os.environ["OPENAI_API_KEY"] = api_key


class NutritionExtraction:
    def __init__(self, detail: str = 'core'):
        """
        Initialise the class with a dictionary containing nutritional information
        and a detail level to define the scope of nutritional data of interest.

        Parameters:
        - detail: A string to specify the level of detail ('core', 'high', or 'all') for nutritional information.
        """
        self.detail = detail
        self.nutrition_vars = self.define_nutrition_detail()
        self.json_nutrition = None        


    def define_nutrition_detail(self) -> list:
        """
        Defines the nutritional indices required based on the specified detail level.

        Returns:
        - A list of nutritional variables of interest.
        """
        # Dictionary mapping detail levels to nutritional components
        full_nutr_dict = {
            'macros': ['protein', 'fat', 'carbohydrates'],
            'macros_detailed': ['fiber', 'saturated fat', 'unsaturated fat', 'sugar', 'essential amino acids', 'nonessential amino acids'],
            'sugar_types': ['glucose', 'fructose', 'galactose', 'lactose'],
            'fiber_types': ['soluble fiber', 'insoluble fiber'],
            'fat_types': ['cholesterol'],
            'minerals': ['iron', 'magnesium', 'zinc', 'calcium', 'potassium', 'sodium'],
            'minerals_detailed': ['phosphorus', 'copper', 'manganese', 'selenium', 'chromium', 'molybdenum', 'iodine'],
            'essential_amino_acids': ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine'],
            'conditionally_essential_amino_acids': ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine'],
            'nonessential_amino_acids': ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine'],
            'vitamins': ['vitamin a', 'vitamin c', 'vitamin d', 'vitamin e', 'vitamin k', 'vitamin b'],
            'vitamins_detailed': ['thiamin (b1)', 'riboflavin (b2)', 'niacin (b3)', 'vitamin b6', 'folate (b9)', 'vitamin b12', 'biotin', 'pantothenic acid (b5)'],
            'indices': ['glycemic index', 'calories'],
        }

        if self.detail == 'core':
            return (full_nutr_dict['indices'] + 
                    full_nutr_dict['macros'] + 
                    full_nutr_dict['macros_detailed'] +  
                    full_nutr_dict['essential_amino_acids'])
        elif self.detail == 'high':
            return (full_nutr_dict['indices'] + 
                    full_nutr_dict['macros'] + 
                    full_nutr_dict['macros_detailed'] +  
                    full_nutr_dict['sugar_types'] + 
                    full_nutr_dict['essential_amino_acids'] +
                    full_nutr_dict['fiber_types'])
        elif self.detail == 'all':
            return [item for sublist in full_nutr_dict.values() for item in sublist]
        else:
            return (full_nutr_dict['indices'] + 
                    full_nutr_dict['macros'] + 
                    full_nutr_dict['macros_detailed'])



    def openai_api(self, prompt: str, model: str = "gpt-3.5-turbo-1106", n: int = 1, temperature: float = 1) -> dict:
        """
        Placeholder method for calling the OpenAI API to process a text prompt.

        Parameters:
        - prompt: The text prompt to process.
        - model: The model identifier.
        - n: The number of responses to generate.
        - temperature: Controls randomness.

        Returns:
        - A dictionary representing the response.
        """
        api_key = os.getenv("API_KEY")
        client = OpenAI(api_key=api_key) 
        response = client.chat.completions.create(
            model=model, #gpt-3.5-turbo-1106 "gpt-4" gpt-4-0613
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=512,
            top_p=1,
            n=n,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={ "type": "json_object"},
            )
        return response
        

    def openai_api_image(self, prompt: str, image: str, model: str = "gpt-4-vision-preview", n: int = 1, temperature: float = 1) -> dict:
        """
        Placeholder method for calling the OpenAI API with both text and image input.

        Parameters:
        - prompt: The text prompt to process alongside the image.
        - image: Base64 encoded string of the image.
        - model: The model identifier.
        - n: The number of responses to generate.
        - temperature: Controls randomness.

        Returns:
        - A dictionary representing the response.
        """
        # define input
        api_key = os.getenv("API_KEY")
        client = OpenAI(api_key=api_key) 
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                    "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",  # Assuming stored_image is just the base64 string
                            "detail": "low"}}
                ]
                }
            ], max_tokens=360,
        )
        
        return response
