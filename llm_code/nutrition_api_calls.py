import os
from openai import OpenAI
from dotenv import load_dotenv

from llm_code.api_helper_functions import *

load_dotenv()

# api_key = os.getenv("API_KEY")
# # Set the environment variable
# os.environ["OPENAI_API_KEY"] = api_key
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Try to get the OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)

class NutritionExtraction:
    # Dictionary mapping detail levels to nutritional components
    full_nutr_dict = {
            'indices': ['glycemic index', 'calories', 'weight'],
            'macros': ['protein', 'fat', 'carbohydrates'],
            'macros_detailed': ['fiber', 'saturated fat', 'unsaturated fat', 'sugar'],
            'sugar_types': ['glucose', 'fructose', 'galactose', 'lactose'],
            'fiber_types': ['soluble fiber', 'insoluble fiber'],
            'fat_types': ['cholesterol'],
            'essential amino acids': ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine'],
            'conditionally essential amino acids': ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine'],
            'nonessential amino acids': ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine'],
            'minerals': ['iron', 'magnesium', 'zinc', 'calcium', 'potassium', 'sodium'],
            'minerals_detailed': ['phosphorus', 'copper', 'manganese', 'selenium', 'chromium', 'molybdenum', 'iodine'],
            'vitamins': ['vitamin a', 'vitamin c', 'vitamin d', 'vitamin e', 'vitamin k', 'vitamin b'],
            'vitamins_detailed': ['thiamin (b1)', 'riboflavin (b2)', 'niacin (b3)', 'vitamin b6', 'folate (b9)', 'vitamin b12', 'biotin', 'pantothenic acid (b5)'],
        }
    
    def __init__(self, detail: str = 'core'):
        """
        Initialise the class with a dictionary containing nutritional information
        and a detail level to define the scope of nutritional data of interest.

        Parameters:
        - detail: A string to specify the level of detail ('core', 'high', or 'all') for nutritional information.
        """
        self.detail = detail
        self.nutrition_vars = self.define_nutrition_detail()
        self.nutrition_dict = None 
        self.response = None
        self.missing_keys = None


    def define_nutrition_detail(self) -> list:
        """
        Defines the nutritional indices required based on the specified detail level.

        Returns:
        - A list of nutritional variables of interest.
        """


        if self.detail == 'core':
            return (self.full_nutr_dict['indices'] + 
                    self.full_nutr_dict['macros'] + 
                    self.full_nutr_dict['macros_detailed'] +  
                    self.full_nutr_dict['essential amino acids'])
        elif self.detail == 'high':
            return (self.full_nutr_dict['indices'] + 
                    self.full_nutr_dict['macros'] + 
                    self.full_nutr_dict['macros_detailed'] +  
                    self.full_nutr_dict['sugar_types'] + 
                    self.full_nutr_dict['essential amino acids'] +
                    self.full_nutr_dict['fiber_types'])
        elif self.detail == 'macro_detailed':
            return (self.full_nutr_dict['indices'] + 
                    self.full_nutr_dict['macros'] + 
                    self.full_nutr_dict['macros_detailed'] +  
                    self.full_nutr_dict['sugar_types'] + 
                    self.full_nutr_dict['fat_types'] + 
                    self.full_nutr_dict['essential amino acids'] +
                    self.full_nutr_dict['nonessential amino acids'] +
                    self.full_nutr_dict['conditionally essential amino acids'] +
                    self.full_nutr_dict['fiber_types'])
        
        elif self.detail == 'all':
            return [item for sublist in self.full_nutr_dict.values() for item in sublist]
        else:
            return (self.full_nutr_dict['indices'] + 
                    self.full_nutr_dict['macros'] + 
                    self.full_nutr_dict['macros_detailed'])
        
    def find_missing_values(self, nutrition_dict=None) -> list:
        """
        Identifies which nutritional variables are not yet included in the nutrition dictionary from the api call. 
        it adds the missing variables after comparing the extracted nutrition_vars to the set of expected variables.

        Input:
        nutrition_dict (dict): a dictionary with the variables names and quantities

        Output:
        missing_keys (list): list of all expected variables but not found in the dict. 
        """

        if nutrition_dict is None:
            nutritional_info = self.nutrition_dict
        else:
            nutritional_info = nutrition_dict
        keys = list(nutritional_info.keys())
        self.missing_keys = [k for k in self.nutrition_vars if k not in keys]

        return self.missing_keys 
    
    def adjust_dict_keys(self):
        """
        Detects and corrects specific key names in the nutrition_dict attribute of the class.
        
        This function iterates over the keys in nutrition_dict and corrects common key name mix-ups
        by renaming them to their intended values. For example, it renames 'name item' to 'name'.
        """
        
        # Dictionary of common key mix-ups to correct: {incorrect_key: correct_key}
        corrections = {
            'name item': 'name',
            'total calories': 'calories',
            'total fat': 'fat',
        }
        
        for incorrect_key, correct_key in corrections.items():
            # Check if the incorrect key exists in the dictionary
            if incorrect_key in self.nutrition_dict:
                print(f'Correcting {incorrect_key} to {correct_key}.')
                # Assign the value from the incorrect key to the correct key
                self.nutrition_dict[correct_key] = self.nutrition_dict[incorrect_key]
                # Delete the old incorrect key
                del self.nutrition_dict[incorrect_key]

    

    def update_nutrition_dict(self, new_nutrition_dict):
        # Update self.nutrition_dict with keys from new_nutrition_dict that aren't already present
        new_keys = {k: v for k, v in new_nutrition_dict.items() if k not in self.nutrition_dict}
        self.nutrition_dict.update(new_keys)

    def concatenate_dataframes(self, new_df):
        # Concatenate self.df with new_df, adding new rows and columns as needed
        self.df = pd.concat([self.df, new_df], ignore_index=True, sort=False)

    def openai_api(self, prompt: str, model: str = "gpt-3.5-turbo-1106", n: int = 1, temperature: float = 1) -> dict:
        """
        Placeholder method for calling the OpenAI API to process a text prompt.

        Parameters:
        - prompt: The text prompt to process.
        - model: The model identifier.
        - n: The number of responses to generate.
        - temperature: Controls randomness.

        Returns:
        - A dictionary representing the nutritional variables and quantities
        - a list of missing variables, compared against the defined nutritional detail when initialising the class.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key) 
        self.response = client.chat.completions.create(
            model=model, #gpt-3.5-turbo-1106 "gpt-4" gpt-4-0613
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=1024,
            top_p=1,
            n=n,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={ "type": "json_object"},
            )
        
        print(' self.full_nutr_dict!!!!!!!!!',  self.full_nutr_dict)
        # now extract the nutritional data from the api call
        new_df, new_nutrition_dict = multiple_api_outputs_to_df(self.response, self.full_nutr_dict)
        
        # Check if self.df and self.nutrition_dict already exist
        if hasattr(self, 'df') and hasattr(self, 'nutrition_dict'):
            # Update the existing nutrition_dict and DataFrame
            self.update_nutrition_dict(new_nutrition_dict)
            self.concatenate_dataframes(new_df)
        else:
            # If they don't exist, simply assign the new values
            self.df, self.nutrition_dict = new_df, new_nutrition_dict

        # correct mixups in formats of keys
        self.adjust_dict_keys()
        # check what variabels are missing from the extracted data. 
        self.find_missing_values()

        return self.nutrition_dict, self.missing_keys        

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
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key) 
        self.response = client.chat.completions.create(
            model=model,
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
            ], max_tokens=1024,
            n=n,
            temperature=temperature,

        )
        # now extract the nutritional data from the api call
        new_df, new_nutrition_dict = multiple_api_outputs_to_df(self.response, self.full_nutr_dict)
        
        # Check if self.df and self.nutrition_dict already exist
        if hasattr(self, 'df') and hasattr(self, 'nutrition_dict'):
            # Update the existing nutrition_dict and DataFrame
            self.update_nutrition_dict(new_nutrition_dict)
            self.concatenate_dataframes(new_df)
        else:
            # If they don't exist, simply assign the new values
            self.df, self.nutrition_dict = new_df, new_nutrition_dict

        # correct mixups in formats of keys
        self.adjust_dict_keys()

        # check what variabels are missing from the extracted data. 
        self.find_missing_values()

        return self.nutrition_dict, self.missing_keys
