import json
import os
import pandas as pd

from ..functions.nutrition_processing import preprocess_and_load_json




def format_llm_output_to_pd(response, json_outputted=False):
    """
    Compares JSON objects from API responses and consolidates them into a single DataFrame.

    Parameters:
    - response: The API response containing multiple JSON objects.
    - json_outputted: Boolean flag indicating if the JSON is directly outputted or needs preprocessing.

    Returns:
    - A Pandas DataFrame consolidating all JSON objects.
    """
    # List to hold flattened DataFrames
    dfs = []

    for api_response in response.choices:
        # Process each JSON object based on `json_outputted` flag
        if json_outputted:
            json_obj = json.loads(api_response.message.content)
        else:
            json_obj = preprocess_and_load_json(api_response.message.content)

        # Flatten JSON object and process DataFrame
        flattened = pd.json_normalize(json_obj)
        flattened = flattened.apply(pd.to_numeric, errors='coerce')  # Convert all columns to numeric, coerce errors
        flattened.columns = [col.split('.')[-1].lower() for col in flattened.columns]  # Simplify and lowercase column names

        # Append processed DataFrame to list
        dfs.append(flattened)

    # Concatenate all DataFrames into a single main DataFrame
    main_df = pd.concat(dfs, ignore_index=True)

    return main_df

