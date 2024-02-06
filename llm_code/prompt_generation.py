from nutrition_api_calls import NutritionExtraction

class PromptGenerator:
    # Define required keys as a class variable
    required_keys = ['name', 'description', 'weight', 'protein', 'fat', 'carbohydrates', 'calories']
    
    # Define templates as a class variable
    prompt_templates = {
    "text_prompt": """Lets play a game: Lets see if we can estomate nutrients from {weight_input}g of a standard "{name_input}". Give me the numbers for the following variables:
          'calories', 'carbohydrates','protein','fat','saturated fat','unsaturated fat','sugar','glucose','fructose','lactose',galactose, 'glycemic index', fiber,'soluble fiber','insoluble fiber','iron','histidine','isoleucine', 'leucine', 'lysine', 'methionine','phenylalanine','threonine','tryptophan','valine'.
          please give the output in json format with the quantities in grams where possible. 
          """,
    "image_text_prompt": """Lets play a game: If there is a food item in this picture: lets try to estimate the serving size together and lets see if we can estimate or look up the nutritional values (in grams or kcal) of the food (serving size in picture.
                the json should contain all of the following:
            ['name item','description of food content','grams in picture','total calories','carbohydrates','sugar','fiber','protein','total fat','saturated fat','unsaturated fat','cholesterol','glycemic index'] Only output a single value (in grams if possible) per property, no ranges. And format output in a json. """,
        # needs name, description, weight, fat, carbs, protein, calories, 
    "missing_details_text_prompt": """ We're going to play a game, we're going to estimate some nutritional contents, we have a {weight}g of a standard {name} which has a {description} with {calories} kcal, {protein}g protein, {carbohydrates}g carbs, {fat}g fat. 
        lets estimate the content of {missing_keys} in grams. return in json format.
            """,
        # requires name, weight
    "missing_details_image_prompt": """  We're going to play a game, we're going to estimate some nutritional contents of {weight}g of {name}.
            lets estimate the content of {missing_keys} in grams. return in json format.
            """
}

    def __init__(self, json_input, detail='core'):
        """
        Initialise the generator with JSON input.
        Ensures all required keys are present, adding them with None if missing.

        Parameters:
        - json_input: The dictionary containing JSON input data.
        - detail: defines the number of nutritional variables to extract. 
        """
        self.json_input = self.ensure_keys_in_json_input(json_input, self.required_keys)
        self.nutrition_extractor = NutritionExtraction(detail=detail)
        self.missing_keys = self.find_missing_values(nutrition_dict=self.json_input)

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
        missing = [k for k in self.nutrition_extractor.nutrition_vars if k not in keys]
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

        
        self.missing_keys = [key for key in required_keys if key not in json_input]
        if self.missing_keys:
            print(f"Warning: Missing keys '{self.missing_keys}' in json_input. Adding them with value None.")
            for key in self.missing_keys:
                json_input[key] = None
        return json_input

    def generate_prompts(self, name_input, weight_input):
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
                            "missing_keys": self.missing_keys}
            
            # Using str.format() with ** to unpack named arguments
            prompts[key] = template.format(**format_args)
        return prompts

