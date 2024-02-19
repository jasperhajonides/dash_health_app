import pandas as pd
import json
from functions.nutrition_processing import preprocess_and_load_json




def average_df_to_dict(main_df):
    """ 
    Take the df and average all columns and shove them into a dict. If the column
    contains string values we can't average so we take the first value from that column that isn't a nan or None. 

    Input:
    main_df (pandas): A dataframe containing nutrients as columns and different api calls as rows. 

    Return:
    dict_output (dict): a dict with the the columns from main_df as keys and values are averages of the columns. 

    """
    # Initialize an empty dictionary to store the final processed values
    dict_output = {}

    # Loop through each column in the DataFrame
    for col in main_df.columns:
        # Check if the column is numeric
        if pd.api.types.is_numeric_dtype(main_df[col]):
            # Calculate the mean, ignoring NaN values
            dict_output[col] = main_df[col].mean(skipna=True)
        else:
            # For non-numeric columns, take the first non-NaN entry
            first_non_nan = main_df[col].dropna().iloc[0] if not main_df[col].dropna().empty else None
            dict_output[col] = first_non_nan

    return dict_output

def update_json_with_amino_acids(json_avg, full_nutr_dict):
    """
    Updates a JSON dictionary with summed values of amino acids categorized into
    essential, conditionally essential, and nonessential groups.

    This function checks if `json_avg` contains any of the amino acids listed in
    `full_nutr_dict` under specific categories. If so, it sums the values of these amino acids
    and adds the sum to `json_avg` under a new key corresponding to the category name. This operation
    is performed only if `json_avg` does not already contain a key for the category.

    Parameters:
    - json_avg (dict): A dictionary containing nutritional information, including amino acids and their quantities.
                       The keys are names of nutrients (e.g., amino acids), and the values are their quantities.
    - full_nutr_dict (dict): A dictionary defining categories of amino acids as keys and lists of amino acid names as values.
                             Expected keys are 'essential amino acids', 'conditionally essential amino acids',
                             and 'nonessential_amino_acids'.

    Returns:
    - dict: The updated `json_avg` dictionary with added keys for amino acid categories if applicable, each representing
            the sum of quantities of amino acids in that category found in `json_avg`.

    Note:
    - The function adds new keys to `json_avg` for categories of amino acids only if the summed value is greater than 0
      and if `json_avg` does not already have a key for that category.
    - The function modifies `json_avg` in place but also returns it for convenience.
    """
    # Define the categories of amino acids to check and sum
    amino_acid_categories = ['essential amino acids', 'conditionally essential amino acids', 'nonessential amino acids']
    for category in amino_acid_categories:
        # Proceed only if the category key doesn't already exist in json_avg
        if category not in json_avg:
            # Initialize the sum for the current category
            sum_amino_acids = 0
            # Loop through each amino acid in the current category
            for amino_acid in full_nutr_dict[category]:
                # If the amino acid is present in json_avg, add its value to the sum
                if amino_acid in json_avg:
                    sum_amino_acids += json_avg[amino_acid]
            # Add the sum to json_avg under the current category, but only if we found any to sum
            if sum_amino_acids > 0:
                json_avg[category] = sum_amino_acids

    return json_avg



def multiple_api_outputs_to_df(response, full_nutr_dict):
    """ 
    this function processes the nutritional details from the api output into a dictionary and a df. It also handles cases where n calls is >1. 

    Input:
    response (openai chatgpt api output): chat output 
    json_outputted

    """
    
    # Create an empty list to store the flattened DataFrames
    dfs = []

    # Loop over each JSON object in the list
    for i, api_response in enumerate(response.choices):

        try:
            # Try to directly load the content as JSON
            json_obj = json.loads(response.choices[i].message.content)
        except ValueError:
            # If it fails, preprocess the content and then load as JSON
            json_obj = preprocess_and_load_json(response.choices[i].message.content)
        flattened = pd.json_normalize(json_obj)

        # print('flattened',flattened)

        # Attempt to convert columns to numeric where possible
        for col in flattened.columns:
            try:
                # This checks if the entire column can be converted to numeric
                flattened[col] = pd.to_numeric(flattened[col], errors='raise')
            except ValueError:
                # If conversion fails (ValueError), leave the column as-is
                pass

        flattened.columns = [col.split('.')[-1] for col in flattened.columns]
        flattened.columns = flattened.columns.str.lower() #lowercase

        # Add the flattened DataFrame to the list
        dfs.append(flattened)

    # Concatenate all DataFrames in the list
    main_df = pd.concat(dfs, ignore_index=True)

    # create a single json with averaged values
    json_avg = average_df_to_dict(main_df)

    # check if the totals of amino acids groups ((conditionally/non)essential ) are present if not sum amino acids up and create these groups.
    json_avg = update_json_with_amino_acids(json_avg, full_nutr_dict)

    return main_df, json_avg

