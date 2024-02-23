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

from dash import callback_context
from dash.dependencies import Input, Output, State, ALL
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
from pages.history_ui import generate_settings_offcanvas
from pages.daily_logbooks import create_logbook_panel


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
    
def nutrition_numbers_layout():
    # Assuming nutrition_numbers_container is a layout component
    return create_nutrition_display()

def combined_plots_layout():
    # Create a layout that contains both the nutrient pie chart and the calories line plot side-by-side
    return html.Div([
        dcc.Graph(figure=create_nutrient_pie_chart(), style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(figure=create_calories_line_plot(), style={'width': '50%', 'display': 'inline-block'})
    ])

# List of carousel item functions
carousel_items = [nutrition_numbers_layout, combined_plots_layout]



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

# Footer content
footer = html.Div(
    [
        html.P(" ", style={'text-align': 'center'}),
        # Add more content here as needed
    ],
    style={
        'height': '300px',
        'background-color': 'white',
        'color': 'black',
        'text-align': 'center',
        'padding': '10px',
    }
)

# define the 
settings_offcanvas = generate_settings_offcanvas(
    settings_offcanvas_id="settings-offcanvas"
)

def nutrition_page():


    layout = html.Div([

    dbc.Container([
        html.Button(
        children=[
            di.DashIconify(icon="mdi:book-open-page-variant", width=30, height=30, style={"verticalAlign": "middle"}),
            " Daily Overview"
        ],
        id="toggle-settings",
        style={
            "position": "fixed",
            "bottom": "20px",
            "left": "50%",
            "transform": "translateX(-50%)",
            "transition": "bottom 0.5s ease-out",
            "zIndex": "1030",
            "background": "linear-gradient(90deg, rgba(0,77,64,1) 0%, rgba(45,105,94,1) 100%)",
            "border": "none",
            "color": "white",
            "padding": "10px 20px",
            "borderRadius": "30px",
            "cursor": "pointer"
        }
    ),
        create_logbook_panel(),
    ], style={"position": "relative", "padding": "2rem"}),

    html.H2("Nutritional Information", className="text-center mb-3"),

     # Carousel Content
    html.Div([
        # Left navigation button
        html.Div(
            dbc.Button('<', id='carousel-left-btn', color='light', className='carousel-btn', 
                        style={'height': '80px', 'width': '40px'}),
            style={'position': 'absolute', 'left': '0', 'top': '50%', 'transform': 'translateY(-50%)'}
        ),

        # Carousel content container
        html.Div(id='carousel-content', className='carousel-content', 
                    style={'height': '400px', 'overflow': 'hidden'}),

        # Right navigation button
        html.Div(
            dbc.Button('>', id='carousel-right-btn', color='light', className='carousel-btn', 
                        style={'height': '80px', 'width': '40px'}),
            style={'position': 'absolute', 'right': '0', 'top': '50%', 'transform': 'translateY(-50%)'}
        ),
    ], style={'position': 'relative', 'height': '400px', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '100%'}),

    html.H3("Enter Nutritional Data", className="mb-2"),
    html.P("Enter an image of your intake and/or a description:", className="mb-2"),


# Combined input bar with '✨' AI-toggle, camera icon, and submit button
    html.Div([
    dbc.InputGroup([
        dbc.Button("✨", id='ai-toggle', n_clicks=1, color="light", style={'borderRadius': '50px 0 0 50px', 'backgroundColor': 'lightblue'}),
        dcc.Upload(
            id='upload-image',
            children=dbc.Button("📷", id='upload-trigger', color="light", style={'borderRadius': '0'}),
            style={'width': '38px', 'height': '38px', 'position': 'relative', 'overflow': 'hidden', 'display': 'inline-block'},
            multiple=True
        ),
        # Custom Text Input for AI mode
        dbc.Input(id='nutritional-text-input', type="search", placeholder="Optional: add details about intake", className='gradient-input', style={'display': 'none'}),
        dbc.Input(id='food-names-input', type="search", placeholder="Search food items", style={'display': 'block'}),
        dbc.Button("Submit", id="submit-nutrition-data", color="primary", style={'borderRadius': '0 50px 50px 0'}),
    ], style={'width': '65%', 'margin': '0 auto', 'borderRadius': '50px', 'border': '2px solid grey'}),
    html.Div(id='suggestions-container', style={'position': 'absolute', 'width': '35%', 'maxHeight': '300px', 'overflowY': 'auto', 'background': 'white', 'border': '1px solid lightgrey', 'zIndex': '1000'}),  # Container for suggestions
    ], style={'padding-bottom': '24px', 'text-align': 'center'}),




    # DISPLAY STATUS
    html.Div(id='update-status', style={'display': 'none'}),  # Initially hidden


    # Display entered item title
    html.H3("Entered item:", className="text-center"),
   # Section for displaying the image, response text, and nutritional values
    html.Div([
        # Left part for the image
        html.Div(id='display-image', style={
            'display': 'none',  # Initially hidden
            'width': '256px',  # Set the width for the image
            'height': '256px',  # Set the height for the image
            'vertical-align': 'top',
            'margin': '0 auto'  # Center align if desired
        }),

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
            # Div for nutritional values
            
            # Div for Weight Input and Nutritional Values
            html.Div([
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
            ], style={'height': '1150px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),




            html.Div([
                dbc.Button("Add", id="add-to-csv-button", color="primary", className="mb-3")
            ], style={'text-align': 'center', 'padding-top': '24px'}),

            html.Div(id='add-status'),

            ######### addd button 
        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '70%', 'lineHeight': '34px'}),
        

    ], style={'display': 'flex', 'justify-content': 'center', 'width': '100%', 'lineHeight': '34px'}),

    ################# daily feed  ################
    # html.H2('Daily feed'),
    # html.Div([
    #     # Left arrow button
    #     html.Button('←', id='prev-day-button', 
    #                 style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
        
    #     # Date picker
    #     dcc.DatePickerSingle(
    #         id='selected-date',
    #         date=datetime.today().date(),
    #         style={'display': 'inline-block'}
    #     ),

    #     # Right arrow button
    #     html.Button('→', id='next-day-button', 
    #                 style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
    # ], style={'textAlign': 'center', 'padding': '10px'}),

    # # show the previous entries (today)

    # html.Div([dbc.Button('Show Entries', id='refresh-entries-button', color="primary", className="mb-3")
    #         ], style={'text-align': 'center', 'padding-top': '24px'}),

    # html.Div(id='recent-entries-container'),
    # footer,


    
    ])
    return layout



def register_callbacks_nutrition(app):

    @app.callback(
        [
            Output("settings-panel", "style"),
            Output("toggle-settings", "style")
        ],
        [Input("toggle-settings", "n_clicks")],
        [
            State("settings-panel", "style"),
            State("toggle-settings", "style")
        ],
    )
    def toggle_settings_panel(n_clicks, panel_style, button_style):
        if n_clicks:
            if panel_style["bottom"] == "0%":
                # Panel is open; move it to "closed" state, leaving a small part visible
                panel_style["bottom"] = "-45%"  # Adjust as needed
                button_style["bottom"] = "2.5%"  # Adjust to align with the visible part of the panel
            else:
                # Panel is "closed"; open it fully, but ensure it slides just below half the button
                panel_style["bottom"] = "0%"
                button_style["bottom"] = "47.5%"  # Adjust so the panel goes slightly under the button
            return panel_style, button_style
        return panel_style, button_style





    # Callback to toggle AI mode and switch between text input and dropdown
    @app.callback(
        [Output('nutritional-text-input', 'style'),
        Output('food-names-input', 'style')],
        [Input('ai-toggle', 'n_clicks')],
        # prevent_initial_call=True
    )
    def toggle_input_mode(n_clicks):
        """ switch between lookup to LLM """
        if n_clicks % 2 == 0:
            # AI mode is OFF: Show food names input
            return {'display': 'none'}, {'display': 'block'}
        else:
            # AI mode is ON: Show custom text input
            return {'display': 'block'}, {'display': 'none'}

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
        State('ai-toggle', 'n_clicks')]
    )
    def store_json_from_image(n_clicks, n_clicks_row, stored_image_data, input_text, ai_toggle_clicks):
        """
        ___________               .___
        \_   _____/___   ____   __| _/
        |    __)/  _ \ /  _ \ / __ | 
        |     \(  <_> |  <_> ) /_/ | 
        \___  / \____/ \____/\____ | 
            \/                    \/ 
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
        if (ai_toggle_clicks % 2 == 0) & ('suggestion-item' in triggered_id):  # AI mode is OFF

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
            message = json_nutrition_std['llm_output']

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
            if entry in json_entry:
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
        

        if ('protein' not in json_entry) and ('fat' not in json_entry) and ('valine' not in json_entry):
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
                'width': '256px',
                'height': '256px',
                'border': '5px solid transparent',  # Gradient border
                'background-image': 'linear-gradient(white, white), linear-gradient(to right, lightblue, darkblue)',
                'background-origin': 'border-box',
                'background-clip': 'content-box, border-box'
            }
            return html.Img(src=src_str, style={'max-width': '100%', 'height': 'auto'}), image_style, base64_image

        # No image uploaded
        return "No image uploaded", {'display': 'none'}, None




    @app.callback(
        [Output('carousel-content', 'children'),
        Output('carousel-index-store', 'data')],
        [Input('carousel-left-btn', 'n_clicks'),
        Input('carousel-right-btn', 'n_clicks')],
        [State('carousel-index-store', 'data')]
    )
    def update_carousel_content(left_clicks, right_clicks, index_data):
        ctx = dash.callback_context

        # Retrieve the current index from dcc.Store
        current_index = index_data['index']

        if not ctx.triggered:
            # Default content on initial load
            return carousel_items[current_index](), index_data
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if button_id == 'carousel-right-btn':
                # Increment index and loop back if at the end
                current_index = (current_index + 1) % len(carousel_items)
            elif button_id == 'carousel-left-btn':
                # Decrement index and loop back if at the start
                current_index = (current_index - 1) % len(carousel_items)

            # Call the function to get the layout and update the index
            return carousel_items[current_index](), {'index': current_index}


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