# nutrition.py

import base64
from PIL import Image
import io
import os
import json

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import dash_iconify as di
from dash_iconify import DashIconify

from dash import callback_context
from dash.dependencies import Input, Output, State, ALL, ClientsideFunction
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime



from icecream import ic



from functions.nutrition_processing import *
from functions.openai_api_calls import * 
from functions.nutrition_plots import *
from functions.nutrition_image import *

from llm_code.nutrition_api_calls import NutritionExtraction
from llm_code.prompt_generation import PromptGenerator

from pages.nutrition_page_parts.current_item import collate_current_item
from pages.nutrition_page_parts.daily_overview import create_daily_feed
from pages.nutrition_page_parts.sample_food_item import *
from pages.nutrition_page_parts.daily_logbooks import create_logbook_panel


# Function to parse the contents of the uploaded file
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return decoded



def format_json_to_html(json_data):
    if isinstance(json_data, dict):
        return html.Ul([html.Li([f"{key}: ", format_json_to_html(value)]) for key, value in json_data.items()])
    elif isinstance(json_data, list):
        return html.Ul([html.Li(format_json_to_html(item)) for item in json_data])
    else:
        return json_data  # For basic data types
    
# def nutrition_numbers_layout():
#     # Assuming nutrition_numbers_container is a layout component
#     return create_nutrition_display()

# def combined_plots_layout():
#     # Create a layout that contains both the nutrient pie chart and the calories line plot side-by-side
#     return html.Div([
#         dcc.Graph(figure=create_nutrient_pie_chart(), style={'width': '50%', 'display': 'inline-block'}),
#         dcc.Graph(figure=create_calories_line_plot(), style={'width': '50%', 'display': 'inline-block'})
#     ])

# # List of carousel item functions
# carousel_items = [
#     lambda: create_nutrition_display('test argument'), 
#     combined_plots_layout
# ]


# Current file directory
current_dir = os.path.dirname(__file__)
# Root directory (one level up from current file)
root_dir = os.path.dirname(current_dir)
# Path to the Excel file
file_path = os.path.join(root_dir, 'data', 'McCance_Widdowsons_Composition_of_Foods_Integrated_Dataset_2021..xlsx')
# Load the specific sheet from the Excel file
df_database = pd.read_excel(file_path, sheet_name='1.3 Proximates')
# Get unique food names for dropdown suggestions
food_names = df_database['Food Name'].dropna().unique().tolist()

# # Footer content
# footer = html.Div(
#     [
#         html.P(" ", style={'text-align': 'center'}),
#         # Add more content here as needed
#     ],
#     style={
#         'height': '300px',
#         'background-color': 'white',
#         'color': 'black',
#         'text-align': 'center',
#         'padding': '10px',
#     }
# )


def nutrition_page():


    layout = html.Div([

    create_logbook_panel(),

    html.H3("Enter Nutritional Data", className="text-center mb-2"),
    html.P("Enter an image of your intake and/or a description:", className="text-center mb-2"),


# Combined input bar with '✨' AI-toggle, camera icon, and submit button
    html.Div([

        # displaying the image
        html.Div(
            children=[
                # Your 'display-image' div
                html.Div(
                    id='display-image',
                    style={
                        'width': '128px',  # Set the width for the image
                        'height': '128px',  # Set the height for the image
                        'vertical-align': 'top',
                        'margin': '0 auto',  # This centers the image in the flex container
                        'border': '2px dashed #ccc',  # Optional: add a dashed border
                        'display': 'flex',  # Use flex layout to center the content of 'display-image'
                        'justify-content': 'center',  # Center horizontally inside 'display-image'
                        'align-items': 'center',  # Center vertically inside 'display-image'
                        'background-image': 'url("/assets/placeholder-icon.svg")',
                        'background-repeat': 'no-repeat',
                        'background-position': 'center'
                    }
                ),
            ],
            # Styles for the outer container
            style={
                'display': 'flex',  # Use flexbox to enable centering
                'justify-content': 'center',  # Center horizontally in the outer container
                'width': '100%',  # Take the full width of the parent, adjust as needed
                'padding': '20px 0',  # Optional padding, adjust as needed
            }
        ),



    dbc.InputGroup([

    # Replace dbc.Button with daq.BooleanSwitch for AI Toggle
        html.Div([
            daq.BooleanSwitch(
                id='ai-toggle',
                on=False,  # Initially set to False, representing AI mode is OFF
                color="#00D8CC",  # Turquoise color when switched ON
                style={'display': 'block', 'margin': '10px auto'}  # Centering the switch
            ),

        ]),


        # Custom Text Input for AI mode
        dbc.Input(id='nutritional-text-input', type="search", placeholder="Optional: add details about intake", className='gradient-input', style={'display': 'none'}),
        dbc.Input(id='food-names-input', type="search", placeholder="Search food items", style={'display': 'block'}),

        dcc.Upload(
            id='upload-image',
            children=dbc.Button("📷", id='upload-trigger', color="light", style={'borderRadius': '0'}),
            style={'width': '38px', 'height': '38px', 'position': 'relative', 'overflow': 'hidden', 'display': 'inline-block'},
            multiple=True
        ),

        dbc.Button("Submit", id="submit-nutrition-data", color="primary", style={'borderRadius': '0 50px 50px 0'}),
    ], style={'width': '65%', 'margin': '0 auto', 'borderRadius': '50px', 'border': '2px solid grey'}),
    html.Div(id='suggestions-container', style={'position': 'absolute', 'width': '35%', 'maxHeight': '300px', 'overflowY': 'auto', 'background': 'white', 'border': '1px solid lightgrey', 'zIndex': '1000'}),  # Container for suggestions
    ], style={'padding-bottom': '24px', 'text-align': 'center'}),


    # images
    html.Div([]),





    # DISPLAY STATUS
    html.Div(id='update-status', style={'display': 'none'}),  # Initially hidden


    # Display entered item title
    html.H3("Current item:", className="text-center"),
   # Section for displaying the image, response text, and nutritional values
    html.Div([
      

        # Right part for response text and nutritional values
        html.Div([

            # Div for response text
            html.Div(id='response-text-output', style={
                'fontFamily': 'Courier New',
                'backgroundColor': '#f8f9fa',  # Very light grey background
                'padding': '10px',  # 10px padding on all sides
                # 'marginBottom': '20px',  # Spacing between text and nutritional values
                'borderRadius': '5px'  # Optional: rounded corners for the box
            }),
            ############## nutritional values input 

            html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                dcc.Tab(
                    label='Macros', value='tab-1',
                    style={'borderRadius': '15px 15px 0 0', 'marginRight': '5px', 'padding': '6px 10px', 'backgroundColor': 'rgba(158, 219, 224, 1)'},
                    selected_style={'backgroundColor': '#ffffff', 'border': '1px solid #d6d6d6', 'borderBottom': 'none', 'color': 'black', 'borderRadius': '15px 15px 0 0', 'padding': '6px 10px'}
                ),
                dcc.Tab(
                    label='Micronutrients', value='tab-2', 
                    style={'borderRadius': '15px 15px 0 0', 'marginRight': '5px', 'padding': '6px 10px', 'backgroundColor': 'rgba(158, 219, 224, 1)', 'zIndex': '1002'},
                    selected_style={'backgroundColor': '#ffffff', 'border': '1px solid #d6d6d6', 'borderBottom': 'none', 'color': 'black', 'borderRadius': '15px 15px 0 0', 'padding': '6px 10px'}
                ),
                dcc.Tab(
                    label='Sugars', value='tab-3',
                    style={'borderRadius': '15px 15px 0 0', 'marginRight': '5px', 'padding': '6px 10px', 'backgroundColor': 'rgba(158, 219, 224, 1)'},
                    selected_style={'backgroundColor': '#ffffff', 'border': '1px solid #d6d6d6', 'borderBottom': 'none', 'color': 'black', 'borderRadius': '15px 15px 0 0', 'padding': '6px 10px'}
                ),
                 dcc.Tab(
                    label='Diet', value='tab-4',
                    style={'borderRadius': '15px 15px 0 0', 'marginRight': '5px', 'padding': '6px 10px', 'backgroundColor': 'rgba(158, 219, 224, 1)'},
                    selected_style={'backgroundColor': '#ffffff', 'border': '1px solid #d6d6d6', 'borderBottom': 'none', 'color': 'black', 'borderRadius': '15px 15px 0 0', 'padding': '6px 10px'}
                ),
            ], style={'height': '36px',
                       'alignItems': 'center',
                        'zIndex': '1001', 'position': 
                        'relative', 
                        'marginBottom':'4.5px'}),
            
            html.Div(id='tabs-content'),
            ]),

            # # Div for Weight Input and Nutritional Values
            # html.Div([





            html.Div([
                dbc.Button("Add", id="add-to-csv-button", color="primary", className="mb-3")
            ], style={'text-align': 'center', 'padding-top': '24px'}),

            html.Div(id='add-status'),

            ######### addd button 
        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '70%', 'lineHeight': '34px'}),
        

    ], style={'display': 'flex', 'justify-content': 'center', 'width': '100%', 'lineHeight': '34px'}),



    
    ])
    return layout



def register_callbacks_nutrition(app):

    app.clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='trigger_animation'),
        Output('tabs-content', 'data-dummy'),  # Use a dummy output to trigger the callback
        [Input('tabs', 'value')]
    )
    @app.callback(Output('tabs-content', 'children'),
                [Input('tabs', 'value')])
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([

                # Weight Input with Update Button
                dbc.InputGroup([

                    # Meal Dropdown with Label
                    html.Div([
                        dbc.Label("Meal:", style={'marginRight': '10px', 'alignSelf': 'center'}),
                        dcc.Dropdown(
                            id='meal-dropdown',
                            options=[
                                {'label': 'Breakfast', 'value': 'Breakfast'},
                                {'label': 'Lunch', 'value': 'Lunch'},
                                {'label': 'Dinner', 'value': 'Dinner'},
                                {'label': 'Dessert', 'value': 'Dessert'},
                                {'label': 'Other', 'value': 'Other'}
                            ],
                            value='Breakfast',  # Default value
                            style={'width': '150px', 'display': 'inline-block', 'marginBottom': '0', 'marginTop': '0'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'paddingRight': '20px'}),
                    
                    # Weight Input and Update Button
                    dbc.InputGroupText("Weight (g):", style={'alignSelf': 'center'}),
                    dbc.Input(id="weight-input", type="number", min=0, step=1, style={'alignSelf': 'center'}),
                    dbc.Button("Update", id="update-nutrition-values", n_clicks=0, color="primary", style={'marginLeft': '15px', 'alignSelf': 'center'})
                ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'}),



                # Placeholder for Nutritional Values
                html.Div(id='dynamic-nutritional-values')
        ], className='fade-in-content', style={'height': '1150px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px',  'position': 'relative'}),



        elif tab == 'tab-2':
            return html.Div([
                # Place your Amino Acids & Minerals content here
                # Example: html.P("Amino Acids & Minerals content")
            ], className='fade-in-content')
        elif tab == 'tab-3':
            return html.Div([
                # Place your Sugars content here
                # Example: html.P("Sugars content")
            ], className='fade-in-content')
        elif tab == 'tab-4':
            return html.Div([
                # Place your Sugars content here
                # Example: html.P("Sugars content")
            ], className='fade-in-content')



    # Callback to toggle AI mode and switch between text input and dropdown
    @app.callback(
        [Output('nutritional-text-input', 'style'),
        Output('food-names-input', 'style')],
        [Input('ai-toggle', 'on')]  # Listen to the 'on' property of the BooleanSwitch
    )
    def toggle_input_mode(ai_mode_on):
        """Switch between lookup to LLM based on AI toggle switch."""
        if ai_mode_on:
            # AI mode is ON: Show custom text input for AI mode
            return {'display': 'block'}, {'display': 'none'}
        else:
            # AI mode is OFF: Show food names input for search mode
            return {'display': 'none'}, {'display': 'block'}


    # Callback to update options based on search input
    @app.callback(
        Output('food-search-dropdown', 'options'),
        Input('food-names-input', 'value')
    )
    def update_dropdown_options(search_value):
        """ search for typed term """
        if search_value:
            # Filter the dataframe for matching food names
            filtered_df = df_database[df_database['Food Name'].str.contains(search_value, case=False, na=False)]

            # Create dropdown options
            options = [{'label': name, 'value': name} for name in filtered_df['Food Name'].unique()]
            return options
        else:
            # If no input, return an empty list
            return []


    # Styling suggestions for hover effect
    app.clientside_callback(
        """
        function(hoverData) {
            if (!hoverData) {
                return [];
            }
            return hoverData.map((hovered, index) => {
                return hovered ? {'backgroundColor': 'lightblue'} : {};
            });
        }
        """,
        Output({'type': 'suggestion-item', 'index': ALL}, 'style'),
        [Input({'type': 'suggestion-item', 'index': ALL}, 'n_hover')]
    )


        # Callback to update suggestions based on input
    @app.callback(
        [Output('suggestions-container', 'children'),
        Output('food-names-input', 'value')],
        [Input('food-names-input', 'value'),
        Input({'type': 'suggestion-item', 'index': ALL}, 'n_clicks')],
        [State({'type': 'suggestion-item', 'index': ALL}, 'index')]
    )
    def update_suggestions(search_value, n_clicks, suggestion_indices):
        """ take the top option from the df"""
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id']

        # If a suggestion is clicked, update the input value and clear suggestions
        if 'suggestion-item' in triggered_id:
            selected_index = json.loads(triggered_id.split('.')[0])['index']
            return [], selected_index

        # Update suggestions based on input
        if search_value:
            filtered_df = df_database[df_database['Food Name'].str.contains(search_value, case=False, na=False)]
            top_matches = filtered_df['Food Name'].unique()[:25]  # Limit to top 25 matches
            suggestions = [{'label': name, 'value': name} for name in top_matches]
            return [html.Div(name, id={'type': 'suggestion-item', 'index': name}, style={'padding': '10px', 'cursor': 'pointer'}) for name in top_matches], dash.no_update
        else:
            return [], dash.no_update

    # Callback to store the selected food item when a suggestion is clicked
    @app.callback(
        Output('selected-food-item-store', 'data'),
        Input({'type': 'suggestion-item', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def store_selected_food_item(n_clicks):
        """ store selected food item when suggestions is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return {}

        selected_id = ctx.triggered[0]['prop_id'].split('.')[0]
        selected_name = json.loads(selected_id)['index']
        selected_row = df_database[df_database['Food Name'] == selected_name].iloc[0].to_dict()
        return selected_row





    @app.callback(
        [
            Output('nutritional-json-from-image', 'data'),
            Output('update-trigger', 'data'),
            Output('response-text-output', 'children')
        ],
        [Input('submit-nutrition-data', 'n_clicks'),
        Input({'type': 'suggestion-item', 'index': ALL}, 'n_clicks')],
        [State('stored-image', 'data'), 
        State('nutritional-text-input', 'value'),
        State('ai-toggle', 'on')]  # Use 'on' instead of 'n_clicks'
    )
    def store_json_from_image(n_clicks, n_clicks_row, stored_image_data, input_text, ai_toggle_on):

        """
        ___________               .___
        \_   _____/___   ____   __| _/
        |    __)/  _ \ /  _ \ / __ | 
        |     \(  <_> |  <_> ) /_/ | 
        \___  / \____/ \____/\____ | 
            \/                    \/ 

        Stores JSON data extracted from an image or input text into a specified storage mechanism, potentially utilizing AI for processing, depending on the toggle state.

        Parameters:
        - n_clicks (int): The number of times the submit button has been clicked. Used to trigger the function.
        - n_clicks_row (int): The number of times a specific row button has been clicked, if applicable.
        - stored_image_data (str): Base64 encoded string of the image data from which to extract information.
        - input_text (str): Text input provided by the user, which may contain additional information or instructions.
        - ai_toggle_on (bool): A boolean flag indicating whether AI processing mode is enabled or not.

        Returns:
        - None. The function is expected to store the processed data in a predefined location or format, not return it.

        Example:
        Assuming the function is properly connected to a UI with the necessary components:
        - User uploads an image and/or enters text.
        - User toggles AI processing mode if desired.
        - User clicks the submit button, triggering this function.

        Note: This docstring assumes the function's purpose based on its parameters. The actual implementation details are not provided.
        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # if n_clicks is None :
        #     raise PreventUpdate
        if not ctx.triggered: # ? 
            return dash.no_update, dash.no_update, dash.no_update
            
        # # Check if the trigger was the submit-nutrition-data button
        # if 'submit-nutrition-data' not in triggered_id:
        #     return dash.no_update, dash.no_update, dash.no_update
        
        # Check AI Toggle state
        if (ai_toggle_on is False) & ('suggestion-item' in triggered_id):  # AI mode is OFF

            selected_id = triggered_id
            selected_name = json.loads(selected_id)['index']
            selected_row = df_database[df_database['Food Name'] == selected_name] #.iloc[0].to_dict()

            json_nutrition_std = search_item_database(selected_row)
            message = "No matches found " if 'message' in json_nutrition_std else 'Nutritional data from database'
            print('SEARCH ITEM', json_nutrition_std)
        else:

            if stored_image_data is None:
                raise PreventUpdate

            # # Call the OpenAI API with the image and input text
            # json_nutrition_std, message = openai_vision_call(stored_image_data, textprompt=input_text)

            # run image extraction 
            nutrition = NutritionExtraction(detail='macro_detailed')

            # generate prompts
            pg = PromptGenerator(nutrition_class=nutrition)
            prompts = pg.generate_prompts(name_input='food', weight_input=100)

            # run api
            if input_text is not None:
                prompts['image_text_prompt'] = prompts['image_text_prompt'] + f' The item in the picture is a {input_text}'
            json_nutrition_std, missing_keys = nutrition.openai_api_image(prompt = prompts['image_text_prompt'], image=stored_image_data, n=1)
            print(f'currently a couple of variables are missing {missing_keys}')
            message = nutrition.response_summary

        # # also add amino acids please:
        # if (ai_toggle_clicks % 2 == 1):
        #     json_data, message = openai_vision_call(stored_image_data, 
        #                                        textprompt=input_text, 
        #                                        prompt_type='amino_acids',
        #                                        weight=json_nutrition_std['weight'],
        #                                        protein=json_nutrition_std['protein'])


        #     json_nutrition_std.update(json_data)

        return json_nutrition_std,  dash.no_update, message #json_grams['llm_output'].spit('```'[0])



    
    @app.callback(
        Output('item-submission-state', 'data'),
        [Input('submit-nutrition-data', 'n_clicks'),
        Input('add-to-csv-button', 'n_clicks')],
        [State('item-submission-state', 'data')]
    )
    def update_submission_state(n_clicks_submit, n_clicks_add, data):
        """ Check if the submit button is pressed for current item. We will revert it back after 'Add' """
        ctx = dash.callback_context
        if not ctx.triggered:
            return data
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'submit-nutrition-data':
            return {'submitted': True}
        elif button_id == 'add-to-csv-button':
            return {'submitted': False}
        return data


    def adjust_nutritional_weight_values(json_entry, trigger, weight_input):
            # Define keys to exclude from adjustments
            EXCLUDED_KEYS = ['glycemic index', 'name', 'description', 'meal_type', 'units']

            # Extract and validate weight from json_entry
            json_weight = max(json_entry.get('weight', 100), 1)  # Ensure weight is at least 1
            print(" max(json_entry.get('weight', 100), 1):::::::::::: ", json_weight)
            # Determine weight_input based on the trigger
            if 'submit-nutrition-data.n_clicks' in trigger:
                weight_input = json_weight
            else:
                weight_input = weight_input if weight_input not in (None, dash.no_update) else json_weight
            print('\n AFTER HTE IF STATEMENT ', weight_input)


            # Calculate adjustment factor based on weight input
            factor = weight_input / json_weight

            print('\n\nFACTOR', factor)
            # Dynamically adjust values based on factor, excluding specified keys
            for key, value in json_entry.items():
                if key not in EXCLUDED_KEYS and isinstance(value, (int, float)):
                    json_entry[key] = value * factor
            print("\n FINAL json_entry", json_entry)
            return json_entry


    @app.callback(
        [Output('dynamic-nutritional-values', 'children'),
        Output('weight-input', 'value')],
        [Input('nutritional-json-from-image', 'data'),
        Input('update-nutrition-values', 'n_clicks'),
        Input('add-to-csv-button', 'n_clicks'),
        Input('submit-nutrition-data', 'n_clicks'),  # Changed from 'item-submission-state' to 'submit-nutrition-data'
        Input('item-submission-state', 'data')],
        [State('weight-input', 'value'),
        State('meal-dropdown', 'value')]
    )
    def update_nutritional_values(json_entry, n_clicks_update, n_clicks_submit, n_clicks, submission_state, weight_input, meal_type):
        ctx = dash.callback_context

        if not json_entry:
            return "No nutritional data available", 100  # Default weight if no data

        # Add meal type
        json_entry['meal_type'] = meal_type

        # Determine which input triggered the callback
        trigger = ctx.triggered[0]['prop_id']

        # FUNCTIO NTHAT DOES ALL THE WEIGHT STUFF, BUT NOT ENTIRELY FUNCTIONAL
        # json_entry = adjust_nutritional_weight_values(json_entry, trigger, weight_input)

        # Extract the weight from json_entry, use default if not present or zero
        json_weight = json_entry.get('weight', 100)
        if json_weight == 0:
            json_weight = 100
        default_weight = json_weight

        # Update weight_input to json_entry weight when submit-nutrition-data button is clicked
        if 'submit-nutrition-data.n_clicks' in trigger:
            weight_input = json_weight
            default_weight = json_weight
        elif weight_input is None or weight_input == dash.no_update:
            # Maintain the existing weight_input value for other triggers
            weight_input = json_weight
            default_weight = json_weight


        # Adjust the values based on the input weight
        factor = weight_input / default_weight


        # adapt the weight of these items.
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
        columns_to_adjust = ['calories','carbohydrates','protein','fat',
                             'fiber','sugar','unsaturated fat','saturated fat','weight'] + essential_amino_acids
        for entry in columns_to_adjust:
            print('ALL JSON ENTRIES', json_entry)
            if entry in json_entry:
                print("specific entry: ",  json_entry[entry])
                json_entry[entry] = json_entry[entry]*factor


        # Check if the submit button was clicked
        if 'add-to-csv-button.n_clicks' in trigger:
            # Logic to save data
            # You can call a function here to save the data
            # Check if there is nutritional data to add
            if json_entry is None or not json_entry:
                return "No nutritional data to add."

            # now save the csv
            filename = 'data/nutrition_entries.csv' 
            now = datetime.now()

            # Convert JSON to DataFrame
            df_new = pd.DataFrame([json_entry])
            df_new['date'] = now.date()
            df_new['time'] = now.strftime("%H:%M:%S")
            if json_entry and 'name' in json_entry:
                df_new['name'] = json_entry['name'].replace('"', '').replace("'", "")
            else:
                df_new['name'] = 'template'
            today_str = datetime.now().strftime('%Y%m%d_%HH:%MM')
            df_new['file_name'] = f"{today_str}_{df_new['name'].loc[0].replace(' ', '_')}.png"
            df_new['units'] = 1
            # Read existing data or create new file
            try:

                df = pd.read_csv(filename)

                # Check each key in JSON data
                for key in df_new.columns:
                    if key not in df.columns:
                        df[key] = None  # Add new column for unmatched keys

                # Concatenate and reorder columns to match
                df = pd.concat([df, df_new], axis=0, ignore_index=True, sort=False)
            except FileNotFoundError:
                df = df_new

            # Save updated data
            df.to_csv(filename, index=False)

        # Default to 'Other' if no meal type is selected
        meal_type = meal_type if meal_type else 'Other'
        if not submission_state['submitted']:
            return dash.no_update, dash.no_update
        
        # Check if the submit-nutrition-data button was clicked
        # if ('submit-nutrition-data.n_clicks' in trigger): # or ('update-nutrition-values.n_clicks' in trigger): #or ('add-to-csv-button.n_clicks' in trigger) or submitted_current_item:
            # Call collate_current_item function
        

        if ('protein' not in json_entry) and ('carbohydrates' not in json_entry) and ('fat' not in json_entry) and ('calories' not in json_entry):
            return dash.no_update, dash.no_update
        

        current_item_layout = collate_current_item(json_entry, weight_input, meal_type)
        return current_item_layout, weight_input


    @app.callback(
        Output('status_2', 'children'),
        [Input('submit-nutrition-data', 'n_clicks'),
         ],
        [State('upload-image', 'contents')]
    )
    def process_nutritional_image(n_clicks, image_contents):
        if n_clicks is None:
            return dash.no_update

        if image_contents is not None:
            content_type, content_string = image_contents[0].split(',')
            decoded = base64.b64decode(content_string)
            src_str = 'data:image/png;base64,' + base64.b64encode(decoded).decode()
            image_display = html.Img(src=src_str, style={'max-width': '100%', 'height': 'auto'})
        else:
            image_display = "No image uploaded"

        # Display the image (Placeholder)
        image_display = html.Img(src='path/to/image', style={'max-width': '100%', 'height': 'auto'})

        return html.Div("Complete")
        

    # Function to process the image
    @app.callback(
        [Output('display-image', 'children'),
        Output('display-image', 'style'),
        Output('stored-image', 'data')],
        [Input('upload-image', 'contents')],
        prevent_initial_call=True
    )
    def process_image(image_contents):
        if image_contents is not None:
            # Process the image, incl conversion to base64 from png jpg or heic
            base64_image,image_format = resize_and_crop_image(image_contents,
                                                              pixels_size=512)
            # print('processed_image_data!!!!', processed_image_data[0:100])
            # Convert the processed image data back to base64 for displaying and storing
            # base64_image, image_format = base64.b64encode(processed_image_data).decode()
            src_str = f"data:image/{image_format};base64,{base64_image}"

            image_style = {
                'width': '128px',
                'height': '128px',
                'border': '5px solid transparent',  # Gradient border
                'background-image': 'linear-gradient(white, white), linear-gradient(to right, lightblue, darkblue)',
                'background-origin': 'border-box',
                'background-clip': 'content-box, border-box'
            }
            return html.Img(src=src_str, style={'max-width': '100%', 'height': 'auto'}), image_style, base64_image

        # No image uploaded
        return " ", {
        'display': 'flex',  # Ensure the div remains visible
        'justify-content': 'center',  # Center the content
        'align-items': 'center',  # Vertically center
        'width': '128px',  # Set the width for the image placeholder
        'height': '128px',  # Set the height for the image placeholder
        'border': '2px dashed #ccc',  # Optional: dashed border
        'background-repeat': 'no-repeat',
        'background-position': 'center',
        'background-size': '100px 100px',  # Adjust size of the background image (placeholder icon)
        'background-image': 'url("/assets/placeholder.png")'  # Placeholder icon
    }, None




    # @app.callback(
    #     Output('selected-date', 'date'),
    #     [
    #         Input('prev-day-button', 'n_clicks'),
    #         Input('next-day-button', 'n_clicks'),
    #         Input('selected-date', 'date'),
    #     ],
    #     [State('selected-date', 'date')]
    # )
    # def change_date(prev_clicks, next_clicks, selected_date, current_date):
    #     ctx = dash.callback_context

    #     # Check which button was clicked
    #     if not ctx.triggered:
    #         raise dash.exceptions.PreventUpdate

    #     button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #     # Calculate the new date
    #     date = datetime.strptime(current_date, '%Y-%m-%d').date()
    #     if button_id == 'prev-day-button':
    #         new_date = date - timedelta(days=1)
    #     elif button_id == 'next-day-button':
    #         new_date = date + timedelta(days=1)
    #     else:
    #         raise dash.exceptions.PreventUpdate

    #     return new_date.strftime('%Y-%m-%d')



    # @app.callback(
    #     Output('recent-entries-container', 'children'),
    #     [
    #         Input('submit-nutrition-data', 'n_clicks'),
    #         Input('refresh-entries-button', 'n_clicks'),
    #         Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
    #         Input({'type': 'unit-increase', 'index': ALL}, 'n_clicks'),
    #         Input({'type': 'unit-decrease', 'index': ALL}, 'n_clicks'),
    #         Input('update-trigger', 'data'),
    #         Input('selected-date', 'date'),
    #         Input('add-to-csv-button', 'n_clicks')
    #     ],
    # )
    # def update_entries(submit_clicks, refresh_clicks, delete_clicks, increase_clicks, decrease_clicks, update_trigger, selected_date_str, add_clicks):
    #     ctx = dash.callback_context
    #     trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    #     # Always read the CSV file when the callback is triggered
    #     filename = 'data/nutrition_entries.csv'
    #     try:
    #         df = pd.read_csv(filename)
    #         if 'units' not in df.columns:
    #             df['units'] = 1
    #         else:
    #             df['units'] = df['units'].fillna(1).apply(lambda x: 1 if pd.isna(x) or x <= 0 else x)
    #     except FileNotFoundError:
    #         return "No entries found."
        
    #     if trigger_id:
    #         # Handling delete, increase, and decrease actions
    #         if 'delete-button' in trigger_id:
    #             button_index = json.loads(trigger_id.split('.')[0])['index']
    #             df = df.drop(df.index[button_index])
    #         elif 'unit-increase' in trigger_id or 'unit-decrease' in trigger_id:
    #             button_index = json.loads(trigger_id.split('.')[0])['index']
    #             increment = 1 if 'unit-increase' in trigger_id else -1
    #             df.at[button_index, 'units'] = max(0, df.at[button_index, 'units'] + increment)

    #     # Save and sort dataframe for all scenarios
    #     df.to_csv(filename, index=False)
    #     df = df.sort_values(by='time', ascending=False)

    #     # Common operations for preparing feed layout
    #     script_dir = os.path.dirname(__file__)
    #     root_dir = os.path.dirname(script_dir)
    #     images_folder = os.path.join(root_dir, 'images')

    #     try:
    #         selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    #     except ValueError:
    #         selected_date = datetime.today().date()

    #     feed_layout = create_daily_feed(df, images_folder, selected_date)
    #     return feed_layout