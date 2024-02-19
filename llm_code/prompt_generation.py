from llm_code.nutrition_api_calls import NutritionExtraction
from typing import Optional, Union

class PromptGenerator:
    # Define required keys as a class variable
    required_keys = ['name', 'description', 'weight', 'protein', 'fat', 'carbohydrates', 'calories']
    
    # Define templates as a class variable  #           'name','weight','description','calories', 'carbohydrates','protein','fat','saturated fat','unsaturated fat','sugar','glucose','fructose','lactose',galactose, 'glycemic index', fiber,'soluble fiber','insoluble fiber','iron','histidine','isoleucine', 'leucine', 'lysine', 'methionine','phenylalanine','threonine','tryptophan','valine'.
    prompt_templates = {
    "text_prompt": """Lets play a game: Lets see if we can estomate nutrients from {weight_input}g of a standard "{name_input}". Give me the numbers for the following variables:
          {generate_values}
          please give the output in json format with the quantities in grams where possible. 
          """,
    "image_text_prompt": """Lets play a game: If there is a food item in this picture: lets try to estimate the serving size together and lets see if we can estimate or look up the nutritional values (in grams or kcal) of the food (serving size in picture.
                the json should contain all of the following metrics (including the name of the food and a description of the food):
                 {generate_values} Only output a single value (in grams if possible) per property, no ranges. And format output in a json. """,
        # needs name, description, weight, fat, carbs, protein, calories, 
    "missing_details_text_prompt": """ We're going to play a game, we're going to estimate some nutritional contents, we have a {weight}g of a standard {name} which has a {description} with {calories} kcal, {protein}g protein, {carbohydrates}g carbs, {fat}g fat. 
        lets estimate the content of {missing_keys} in grams. return in json format.
            """,
        # requires name, weight
    "missing_details_image_prompt": """  We're going to play a game, we're going to estimate some nutritional contents of {weight}g of {name}.
            lets estimate the content of {missing_keys} in grams. return in json format.
            """
}

    def __init__(self, json_input={}, nutrition_class=None):
        """
        Initialize the generator with JSON input and optionally with a NutritionExtraction instance.

        Parameters:
        - json_input: The dictionary containing JSON input data.
        - detail: defines the level of detail for nutritional variables to extract. Optional.
        - nutritionextractor: An optional instance of NutritionExtraction to use for extracting missing keys.
        """
        
        # Check if a NutritionExtraction instance is provided
        if nutrition_class is not None:

            print('found nutrition class')
            self.nutritionextractor = nutrition_class
            # Assuming missing_keys is an attribute of NutritionExtraction containing missing keys
            self.missing_keys = self.nutritionextractor.missing_keys
            self.json_input = self.nutritionextractor.nutrition_dict
            self.generate_values = str(self.nutritionextractor.nutrition_vars)
        else:
            # If no NutritionExtraction instance is provided, default to using the detail parameter
            self.nutrition_class = nutrition_class
            # Find missing values based on the provided JSON input if no nutritionextractor is given
            self.missing_keys = []
            self.json_input = json_input
            # if no level of detail is ps
            self.generate_values = "['name','weight','description','calories', 'carbohydrates','protein','fat','saturated fat','unsaturated fat','sugar', 'glycemic index', fiber,'iron']"

        print('WE ARE GOING TO GENERATE THESE VALS', self.generate_values )
        self.json_input = self.ensure_keys_in_json_input(self.json_input, self.required_keys)



    def find_missing_values(self, nutrition_dict: dict) -> list:
        """
        Identifies which nutritional variables are not yet included in the nutrition dictionary.

        Parameters:
        - nutrition_dict: A dictionary to store nutrition data.

        Returns:
        - A list of missing nutritional variables.
        """
        self.json_nutrition = nutrition_dict
        keys = list(self.json_nutrition.keys())
        missing = [k for k in self.nutrition_class.nutrition_vars if k not in keys]
        return missing
    

    def ensure_keys_in_json_input(self, json_input, required_keys):
        """
        Ensures all required keys are present in the json_input, adding them with None if missing.

        Parameters:
        - json_input: The original dictionary containing JSON input data.
        - required_keys: A list of keys that are required to be present in json_input.

        Returns:
        - Modified json_input with all required keys present.
        """

        # Initialize json_input as an empty dictionary if it's None
        if json_input is None:
            json_input = {}


        self.missing_promptbuilding_keys = [key for key in required_keys if key not in json_input]
        if self.missing_promptbuilding_keys:
            print(f"Warning: Missing keys '{self.missing_promptbuilding_keys}' in json_input to build prompts. Adding them with value None.")
            for key in self.missing_promptbuilding_keys:
                json_input[key] = None
        return json_input

    def generate_prompts(self, name_input: Optional[str] = None, weight_input: Optional[Union[int, float]] = None):
        """
        Generates prompts based on embedded templates and input variables.

        Parameters:
        - name_input: Name to be used in prompts.
        - weight_input: Weight to be used in prompts.

        Returns:
        - A dictionary of generated prompts.
        """
        prompts = {}

        for key, template in self.prompt_templates.items():
            # Preparing additional named arguments for formatting from json_input
            format_args = {**self.json_input,
                            "name_input": name_input,
                            "weight_input": weight_input,
                            "missing_keys": self.missing_keys,
                            "generate_values": self.generate_values}
                
            if (key == 'text_prompt' or key == 'image_text_prompt') and name_input is not None and weight_input is not None:            
                # Using str.format() with ** to unpack named arguments
                prompts[key] = template.format(**format_args)
            elif (key == 'missing_details_text_prompt' or key == 'missing_details_image_prompt'):
                prompts[key] = template.format(**format_args)


        return prompts

