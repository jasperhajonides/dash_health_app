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


# Function to parse the contents of the uploaded file
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return decoded

# Function to resize and crop the image
def resize_and_crop_image(image_data, pixels_size = 512):
    # Open the image and determine smaller side
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size
    new_size = min(width, height)

    # Resize with the smaller side being 512 pixels
    ratio = pixels_size / new_size
    new_width, new_height = int(ratio * width), int(ratio * height)
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crop to a 512x512 square
    left = (new_width - pixels_size) / 2
    top = (new_height - pixels_size) / 2
    right = (new_width + pixels_size) / 2
    bottom = (new_height + pixels_size) / 2
    image = image.crop((left, top, right, bottom))

    # Convert the image to binary data for storage
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return buffered.getvalue()


def save_image(stored_image_data, file_name):
    if (file_name is None) or (len(file_name) <= 1):
        file_name = 'template'
            # Decode the base64 string
    image_data = base64.b64decode(stored_image_data)

    # Create the filename
    today_str = datetime.now().strftime('%Y%m%d')
    item_name = file_name.replace(' ', '_')
    filename = f"{today_str}_{item_name}.png"

    # Define the path to the images folder relative to the root of the project
    script_dir = os.path.dirname(__file__)  # Directory of the current script
    root_dir = os.path.dirname(script_dir)  # Root directory of the project
    images_folder = os.path.join(root_dir, 'assets', 'images')

    # Create the directory if it doesn't exist
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # Full path for the image
    image_path = os.path.join(images_folder, filename)

    # Save the image
    with open(image_path, 'wb') as f:
        f.write(image_data)

    print(f"Image saved as {filename}")




def format_json_to_html(json_data):
    if isinstance(json_data, dict):
        return html.Ul([html.Li([f"{key}: ", format_json_to_html(value)]) for key, value in json_data.items()])
    elif isinstance(json_data, list):
        return html.Ul([html.Li(format_json_to_html(item)) for item in json_data])
    else:
        return json_data  # For basic data types

def nutrition_page():
    # first plot
    nutrient_pie_chart = create_nutrient_pie_chart()
    calories_line_plot = create_calories_line_plot()
    nutrition_numbers_container =  create_nutrition_display()


    layout = html.Div([
    html.H2("Nutritional Information", className="text-center mb-3"),

    # Add the Pie Chart here
    dcc.Graph(figure=nutrient_pie_chart, style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(figure=calories_line_plot, style={'width': '50%', 'display': 'inline-block'}),
    nutrition_numbers_container,
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
        response_text = openai_vision_call(stored_image_data, input_text)
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
                df_new['name'] = json_data['name item'].replace('"', '').replace("'", "").replace(' ', '_')
            else:
                df_new['name'] = 'template'
            today_str = datetime.now().strftime('%Y%m%d')
            df_new['file_name'] = f"{today_str}_{df_new['name'].loc[0]}.png"
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
        


    # @app.callback(
    #     Output('update-status', 'children'),  # Replace with an appropriate output
    #     [Input('submit-nutrition-data', 'n_clicks')],
    #     [State('nutritional-json-from-image', 'data')]
    # )
    # def update_csv(n_clicks, json_data):
    #     if n_clicks is None or json_data is None:
    #         raise dash.exceptions.PreventUpdate

    #     filename = 'data/nutrition_entries.csv'
    #     now = datetime.datetime.now()

    #     # Convert JSON to DataFrame
    #     df_new = pd.DataFrame([json_data])
    #     df_new['date'] = now.date()
    #     df_new['time'] = now.strftime("%H:%M:%S")

    #     # Read existing data or create new file
    #     try:
    #         df = pd.read_csv(filename)

    #         # Check each key in JSON data
    #         for key in df_new.columns:
    #             if key not in df.columns:
    #                 df[key] = None  # Add new column for unmatched keys

    #         # Concatenate and reorder columns to match
    #         df = pd.concat([df, df_new], axis=0, sort=False).reindex(columns=df.columns)
    #     except FileNotFoundError:
    #         df = df_new

    #     # Save updated data
    #     df.to_csv(filename, index=False)
    #     return "Data saved successfully"





    @app.callback(
        Output('recent-entries-container', 'children'),
        [
            Input('submit-nutrition-data', 'n_clicks'),
            Input('refresh-entries-button', 'n_clicks'),
            Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
            Input('update-trigger', 'data')
        ],
    )
    def update_entries(submit_clicks, refresh_clicks, delete_clicks, update_trigger):
        ctx = callback_context

        # Determine which input triggered the callback
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

        # if not ctx.triggered:
        #     raise PreventUpdate

        filename = 'data/nutrition_entries.csv'
        try:
            df = pd.read_csv(filename)
        except FileNotFoundError:
            return "No entries found."
        
        # Handle delete action
        if trigger_id and 'delete-button' in trigger_id:
            button_index = json.loads(trigger_id.split('.')[0])['index']
            df = df.drop(df.index[button_index])
            df.to_csv(filename, index=False)

        # Sort the DataFrame to show the most recent entries first
        df = df.sort_values(by='time', ascending=False)

        # directory in which the current images are written
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        root_dir = os.path.dirname(script_dir)  # Root directory of the project
        images_folder = os.path.join(root_dir, 'images')

        entry_boxes = []
        for index, row in df.iterrows():
            # Use 'default_file_name.png' if 'file_name' is NaN or not present
            image_filename = row['file_name'] if 'file_name' in row and pd.notna(row['file_name']) else 'default_file_name.png'
            image_url = f'/assets/images/{image_filename}'  # Construct the URL path

            box = html.Div([
                # Image part
                html.Div([
                    html.Img(src=image_url, style={'width': '256px', 'height': '256px'})
                ], style={'width': '30%', 'display': 'inline-block'}),
                
                # Data part
                html.Div([
                    html.Ul([html.Li(f"{key}: {value}") for key, value in row.drop(['file_name', 'date', 'time']).items()])
                ], style={'width': '70%', 'display': 'inline-block'}),
                
                # Delete button
                html.Div([
                    html.Button('X', id={'type': 'delete-button', 'index': index}, className='delete-btn')
                ], style={'position': 'absolute', 'top': '0', 'right': '0'})
            ], style={'display': 'flex', 'border': '1px solid black', 'padding': '10px', 'position': 'relative', 'margin': '10px 0'})
            entry_boxes.append(box)

        return entry_boxes