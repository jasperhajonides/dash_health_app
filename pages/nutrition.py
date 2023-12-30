# nutrition.py

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import callback_context

from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import pandas as pd
from datetime import datetime


import base64
from PIL import Image
import io
import os
import json



from functions.nutrition_processing import *
from functions.openai_api_calls import * 
from functions.nutrition_plots import *
from functions.nutrition_image import *


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


def nutrition_page():

    layout = html.Div([
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

   # Drop box for image upload with modified children for text layout
    html.Div([
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                html.Div('Drag and Drop or Select Files', style={'padding': '0px'}),  # Each line as a separate div
            ], style={
                'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'height': '100%'
            }),
            style={
                'width': '60%', 'height': '100px', 'lineHeight': '60px',
                'borderWidth': '2px', 'borderStyle': 'dashed',
                'borderImage': 'linear-gradient(to right, lightblue, darkblue) 1',
                'textAlign': 'center', 'margin': '10px auto',
                'display': 'block', 'backgroundColor': 'rgba(173, 216, 230, 0.1)',
                'fontFamily': 'Courier New'
            },
            multiple=True
        )
    ], style={'padding-bottom': '20px'}),

    # Text input with subtle gradient background and light grey color
    html.Div([
        dbc.Input(id='nutritional-text-input', placeholder="Optional: add details about intake", 
                style={
                    'width': '60%', 'margin': '0 auto', 'display': 'block',
                    'background': 'rgba(128, 128, 128, 0.95)',  # Light grey with 95% opacity
                    'background-image': 'linear-gradient(to right, lightblue, blue)',
                    'color': 'black',  # Ensure text is fully black
                    'border': '1px solid #ccc',  # Optional: add border for better visibility
                })
    ], style={'padding-bottom': '24px'}),

    # Submit button
    html.Div([
        dbc.Button("Submit", id="submit-nutrition-data", color="primary", className="mb-3")
    ], style={'text-align': 'center', 'padding-bottom': '24px'}),

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

            # Div for nutritional values
            html.Div(id='nutritional-values', style={
                'vertical-align': 'top'
            })

        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '70%'})

    ], style={'display': 'flex', 'justify-content': 'center', 'width': '100%'}),

    # show the previous entries (today)
    html.Button('Refresh Entries', id='refresh-entries-button'),

    html.Div(id='recent-entries-container'),

    
    ])
    return layout

def register_callbacks_nutrition(app):
    @app.callback(
        Output('nutritional-values', 'children'),
        [Input('submit-nutrition-data', 'n_clicks'),
         Input('nutritional-json-from-image', 'data')],
        [State('nutritional-text-input', 'value'),
        State('upload-image', 'contents')]
    )
    def process_nutritional_info(n_clicks, json_dict_final, text_input, image_contents):
        if n_clicks is None:
            return dash.no_update

        # If there's an image uploaded, display it
        if image_contents is not None:
            content_type, content_string = image_contents[0].split(',')
            decoded = base64.b64decode(content_string)
            src_str = 'data:image/png;base64,' + base64.b64encode(decoded).decode()
            image_display = html.Img(src=src_str, style={'max-width': '100%', 'height': 'auto'})
        else:
            image_display = "No image uploaded"

        # Display the image (Placeholder)
        image_display = html.Img(src='path/to/image', style={'max-width': '100%', 'height': 'auto'})

        # run formatting of json for viz
        formatted_json_display = format_json_to_html(json_dict_final)

        # Display nutritional values
        # nutritional_display = html.Ul([html.Li(f"{key}: {value}") for key, value in json_nutrition.items()])
        return formatted_json_display
    



    @app.callback(
        [Output('display-image', 'children'),
        Output('display-image', 'style'),
        Output('stored-image', 'data')],  # Add an output to store the base64 image data
        [Input('upload-image', 'contents')],
        prevent_initial_call=True
    )
    def process_image(image_contents):
        if image_contents is not None:
            image_data = parse_contents(image_contents[0])
            processed_image_data = resize_and_crop_image(image_data)

            # Convert to base64 for displaying and storing
            base64_image = base64.b64encode(processed_image_data).decode()
            src_str = f"data:image/jpeg;base64,{base64_image}"

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
        return "No image uploaded", {'display': 'none'}, None  # Also return None for the stored data
    


    @app.callback(
        [
            Output('nutritional-json-from-image', 'data'),
            Output('update-trigger', 'data'),
            Output('response-text-output', 'children')  # New output for displaying the response text

            ],
        [Input('submit-nutrition-data', 'n_clicks')],
        [State('stored-image', 'data'), 
         State('nutritional-text-input', 'value')]
    )
    def store_json_from_image(n_clicks, stored_image_data, input_text):

        if n_clicks is None:
            raise PreventUpdate

        if stored_image_data is None:
            raise PreventUpdate
        else:
            pass
            # print('image_data', stored_image_data[0:100])


        print('Button clicked. Running function to start calling OpenAI API.', input_text)

        # Call the OpenAI API with the image and input text
        response_text = openai_vision_call(stored_image_data, textprompt=input_text)
        # response_text = '```json\n{\n  "name item": "raisin pastry",\n  "grams in picture": 100,\n  "total calories (kcal)": 290, \n  "carbohydrates (g)": 45, \n  "of which sugar (g)": 12,\n  "fiber (g)": 2,\n  "protein (g)": 6, \n  "saturated fat (g)": 6,\n  "unsaturated fat (g)": 4,\n  "cholesterol (g)": 0.1\n}\n```'
        
        json_data = preprocess_and_load_json(response_text)
        # ensure all values are values
        json_grams = convert_to_grams(json_data)
        json_nutrition_std = extract_nutrition(json_grams)

        try: 
            # now save the csv
            filename = 'data/nutrition_entries.csv'
            now = datetime.now()

            # Convert JSON to DataFrame
            df_new = pd.DataFrame([json_nutrition_std])
            df_new['date'] = now.date()
            df_new['time'] = now.strftime("%H:%M:%S")
            if json_data and 'name item' in json_data:
                df_new['name'] = json_data['name item'].replace('"', '').replace("'", "")
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
                df = pd.concat([df, df_new], axis=0, sort=False).reindex(columns=df.columns)
            except FileNotFoundError:
                df = df_new

            # Save updated data
            df.to_csv(filename, index=False)

            # store image too
            # Check if json_nutrition_std is not empty and save the image
            save_image(stored_image_data, df_new['name'].iloc[0])

            return json_nutrition_std, dash.no_update, response_text.split('```')[0]
        except:
            print('not updating the list with todays entries.')
            return json_nutrition_std, {'timestamp': datetime.now().isoformat()}, response_text.split('```')[0]
        
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





    @app.callback(
        Output('recent-entries-container', 'children'),
        [
            Input('submit-nutrition-data', 'n_clicks'),
            Input('refresh-entries-button', 'n_clicks'),
            Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
            Input({'type': 'unit-increase', 'index': ALL}, 'n_clicks'),
            Input({'type': 'unit-decrease', 'index': ALL}, 'n_clicks'),
            Input('update-trigger', 'data')
        ],
    )
    def update_entries(submit_clicks, refresh_clicks, delete_clicks, increase_clicks, decrease_clicks, update_trigger):
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

        if trigger_id is None:
            raise dash.exceptions.PreventUpdate


        filename = 'data/nutrition_entries.csv'
        try:
            df = pd.read_csv(filename)
            # Initialize 'units' column if it doesn't exist
            if 'units' not in df.columns:
                df['units'] = 1
            else:
                # Set 'units' to 1 for rows where it is NaN or non-existent
                df['units'] = df['units'].fillna(1).apply(lambda x: 1 if pd.isna(x) or x <= 0 else x)
        except FileNotFoundError:
            return "No entries found."
        
        # Handling delete, increase, and decrease actions
        if 'delete-button' in trigger_id:
            button_index = json.loads(trigger_id.split('.')[0])['index']
            df = df.drop(df.index[button_index])
        elif 'unit-increase' in trigger_id or 'unit-decrease' in trigger_id:
            button_index = json.loads(trigger_id.split('.')[0])['index']
            increment = 1 if 'unit-increase' in trigger_id else -1
            df.at[button_index, 'units'] = max(0, df.at[button_index, 'units'] + increment)
        
        df.to_csv(filename, index=False)
        df = df.sort_values(by='time', ascending=False)

        script_dir = os.path.dirname(__file__)
        root_dir = os.path.dirname(script_dir)
        images_folder = os.path.join(root_dir, 'images')

        entry_boxes = []
        for index, row in df.iterrows():
            image_filename = row.get('file_name', 'default_file_name.png')
            image_path = os.path.join(images_folder, image_filename)


            # Unit Counter Part
                # Unit Counter Part
            unit_counter = html.Div([
                html.Button('+', id={'type': 'unit-increase', 'index': index}, 
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 'box-shadow': '0 2px 4px rgba(0,0,0,0.2)',
                                'margin-bottom': '5px'}),
                html.Div(str(row.get('units', 1)), style={'text-align': 'center'}),
                html.Button('-', id={'type': 'unit-decrease', 'index': index},
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 'box-shadow': '0 2px 4px rgba(0,0,0,0.2)',
                                'margin-top': '5px'})
            ], style={'width': '10%', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})

            # Macros and Additional Nutritional Info Part
            nutritional_info = html.Div([
                html.H4(row.get('name', 'Item Name'), style={'fontSize': '28px'}),  # Title from row['name']
                
                # Serving size and Calories row
                
                # Serving size and Calories row
                html.Div([
                    html.Span('🍽️', style={'fontSize': '20px'}),  # Placeholder icon for serving size
                    html.Span(f"{row.get('weight', 'N/A')} g", style={'marginLeft': '5px', 'marginRight': '20px'}),
                    html.Span('🔥', style={'fontSize': '20px'}),  # Placeholder icon for calories
                    html.Span(f"{row.get('calories', 'N/A')} kcal", style={'marginLeft': '5px'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

                
                # Two-column layout for macros and additional info
                html.Div([
                    # Column 1: Macros
                    html.Div([
                        html.Ul([
                            html.Li(f"Fat: {row.get('fat', 'N/A')} g"),
                            html.Li(f"Carbohydrates: {row.get('carbs', 'N/A')} g"),
                            html.Li(f"Protein: {row.get('protein', 'N/A')} g"),
                        ], style={'listStyleType': 'none', 'paddingLeft': '0'}),
                    ], style={'width': '50%', 'display': 'inline-block'}),

                    # Column 2: Additional Info
                    html.Div([
                        html.Ul([
                            html.Li(f"Fiber: {row.get('fiber', 'N/A')} g"),
                            html.Li(f"Sugar: {row.get('sugar', 'N/A')} g"),
                            html.Li(f"Unsaturated Fat: {row.get('unsaturated fat', 'N/A')} g"),
                            html.Li(f"Saturated Fat: {row.get('saturated fat', 'N/A')} g"),
                            html.Li(f"Cholesterol: {row.get('cholesterol', 'N/A')} mg"),
                        ], style={'listStyleType': 'none', 'paddingLeft': '0'}),
                    ], style={'width': '50%', 'display': 'inline-block'}),
                ], style={'display': 'flex'}),

            ], style={'width': '65%', 'display': 'inline-block'})

                # Delete Button Layout
            delete_button = html.Div([
                html.Button('×', id={'type': 'delete-button', 'index': index},  # Using the multiply symbol
                            style={
                                'width': '30px', 
                                'height': '30px', 
                                'lineHeight': '30px',  # Adjusted for vertical centering
                                'padding': '0',  # Remove padding to fit symbol within the button
                                'border': '1px solid darkgrey', 
                                'background-color': 'white', 
                                'color': 'darkgrey', 
                                'font-weight': 'bold', 
                                'font-size': '20px',  # Font size for the symbol
                                'text-align': 'center',
                                'cursor': 'pointer',
                                'position': 'absolute', 
                                'top': '10px',  # Positioning the button within the box
                                'right': '10px'
                            })
            ])

            box = html.Div([
                # Unit Counter Part
                unit_counter,
                
                # Image Part
                html.Div([
                    html.Img(src=image_path, style={'width': '192px', 'height': '192px'})
                ], style={'width': '25%', 'display': 'inline-block'}),

                # Data Part
                nutritional_info,

                
                # Delete Button
                delete_button,
                ], style={'display': 'flex', 'border': '1px solid black', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px', 'position': 'relative', 'margin': '10px 0'})
            entry_boxes.append(box)

        return entry_boxes
