import dash
from dash import html, dcc, Input, Output, State
import os
from datetime import datetime
import dash_bootstrap_components as dbc
import base64
from dotenv import load_dotenv

# Import utility modules
from utils_gc.gcp_utils import upload_image_to_gcs, get_image_url_from_gcs, list_files_in_gcs, generate_id
from utils_gc.image_processing import process_image
from utils_gc.nutrition_utils import get_nutritional_info, adjust_nutritional_weight_values
from utils_gc.supabase_utils import get_supabase_client, insert_nutrition_data
from pages.nutrition_page_parts.current_item_mobile import collate_current_item

# Set your Google Cloud Storage bucket name
GCS_BUCKET = 'dash_health_store'

# Load environment variables
load_dotenv()

# Initialize the app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])  # MINTY is a pastel green/blue theme
server = app.server  # Expose the Flask server

# Get the current date
current_date = datetime.now().strftime('%A, %B %d, %Y')

# Layout for the Dash app
app.layout = dbc.Container([
    # Top Row with date and menu button
    dbc.Row([
        dbc.Col(
            html.Div(),
            width=1  # Empty column to balance
        ),
        dbc.Col(
            html.H5(current_date, className='date-header'),
            width=10
        ),
        dbc.Col(
            dbc.Button("☰", color="link", id="navbar-toggle", className='menu-button', style={'font-size': '24px'}),
            width=1
        )
    ], align='center', className='my-2'),

    # Photo Submission Card
    dbc.Card([
        dbc.CardHeader(html.H5("Step 1: Upload an Image")),
        dbc.CardBody([
            dcc.Upload(
                id='upload-image',
                children=dbc.Button('Click to Upload Image', color='primary', className='mt-2'),
                multiple=False  # Allow only one file
            ),
            html.Div(id='output-image-preview', className='mt-3'),
        ])
    ], className='mb-3'),

    # Description Input Card (hidden initially)
    dbc.Card([
        dbc.CardHeader(html.H5("Step 2: Describe the Image (Optional)")),
        dbc.CardBody([
            dbc.Input(id='image-description', type='text', placeholder='e.g., Grilled Chicken Salad', className='mt-2'),
            dcc.Dropdown(
                id='meal-type-dropdown',
                options=[
                    {'label': 'Breakfast', 'value': 'breakfast'},
                    {'label': 'Lunch', 'value': 'lunch'},
                    {'label': 'Dinner', 'value': 'dinner'},
                    {'label': 'Other', 'value': 'other'}
                ],
                placeholder='Select meal type',
                className='mt-2'
            ),
            dbc.Button('Calculate', id='calculate-button', color='success', className='mt-2'),
            html.Div(id='output-calculate-status', className='mt-2')
        ], id='description-div', style={'display': 'none'})
    ], className='mb-3'),

    # Weight Adjustment Card (hidden initially)
    dbc.Card([
        dbc.CardHeader(html.H5("Step 3: Adjust Weight and Update Nutritional Values")),
        dbc.CardBody([
            dbc.InputGroup([
                dbc.InputGroupText("Weight (grams):"),
                dbc.Input(id='weight-input', type='number', min=1, step=1, placeholder='Enter weight'),
                dbc.Button('Update', id='update-nutrition-button', color='secondary', className='ms-2'),
            ], className='mt-2'),
        ], id='weight-adjustment-div', style={'display': 'none'})
    ], className='mb-3'),

    # Nutritional Information Card
    dbc.Card([
        dbc.CardHeader(html.H5("Nutritional Information")),
        dbc.CardBody([
            html.Div(id='nutritional-info', className='mt-3')
        ])
    ], className='mb-3'),

    # Upload to Google Cloud Card
    dbc.Card([
        dbc.CardHeader(html.H5("Step 4: Upload to Google Cloud")),
        dbc.CardBody([
            dbc.Button('Upload to Google Cloud', id='upload-button', color='info', className='mt-2'),
            html.Div(id='output-upload-status', className='mt-2')
        ])
    ], className='mb-3'),

    # Display Nutritional Data Card
    dbc.Card([
        dbc.CardHeader(html.H5("Display Daily Nutritional Summary")),
        dbc.CardBody([
            dbc.Button('Display Nutritional Data', id='display-button', color='warning', className='mt-3'),
            html.Div(id='output-nutrition-data', className='mt-2')
        ])
    ], className='mb-3'),


    # Hidden store for nutritional data
    dcc.Store(id='nutritional-json-data'),
    dcc.Store(id='adjusted-nutritional-json-data')  # Add this line

], fluid=True)

# Callback to display image preview and show description input
@app.callback(
    Output('output-image-preview', 'children'),
    Output('description-div', 'style'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename')
)
def update_image_preview(image_contents, filename):
    if image_contents is not None:
        # Process the image (auto-rotate and adjust)
        src_str, base64_image = process_image(image_contents)

        if src_str:
            # Display the image preview
            return (
                html.Div([
                    html.H3(f"Preview of '{filename}':"),
                    html.Img(src=src_str, className='image-preview'),
                ]),
                {'display': 'block'}
            )
    return (None, {'display': 'none'})

# Callback to calculate nutritional information
@app.callback(
    Output('output-calculate-status', 'children'),
    Output('nutritional-json-data', 'data'),
    Output('weight-adjustment-div', 'style'),
    Input('calculate-button', 'n_clicks'),
    State('upload-image', 'contents'),
    State('image-description', 'value')
)
def calculate_nutritional_info(n_clicks, image_contents, description):
    if n_clicks is not None and n_clicks > 0 and image_contents is not None:
        # Process the image
        src_str, base64_image = process_image(image_contents)


        if base64_image:
            # Get nutritional information
            json_nutrition_std = get_nutritional_info(base64_image, description)

            if json_nutrition_std:
                # Store the nutritional data and show the weight adjustment div
                return (
                    "Nutritional information calculated successfully.",
                    json_nutrition_std,
                    {'display': 'block'}
                )
            else:
                return ("Error in nutritional analysis.", None, {'display': 'none'})
    return ("", None, {'display': 'none'})

# Callback to adjust nutritional values based on weight input
# Callback to adjust nutritional values based on weight input
@app.callback(
    Output('nutritional-info', 'children'),
    Output('weight-input', 'value'),  # Update weight-input field
    Output('adjusted-nutritional-json-data', 'data'),  # Store adjusted data
    Input('nutritional-json-data', 'data'),
    Input('update-nutrition-button', 'n_clicks'),
    Input('meal-type-dropdown', 'value'),  # Get the selected meal type
    State('weight-input', 'value')
)
def update_nutritional_values(json_entry, n_clicks_update, meal_type, weight_input):
    ctx = dash.callback_context
    if json_entry is not None:
        # Determine which input triggered the callback
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == 'nutritional-json-data':
            # If the json data has been updated, use the weight from json_entry
            weight = json_entry.get('weight', 100)
            # Update weight-input field
            weight_input = weight
        else:
            # Use the weight from the input field
            weight = weight_input if weight_input is not None else json_entry.get('weight', 100)

        # Adjust nutritional values based on weight
        adjusted_json = adjust_nutritional_weight_values(json_entry, weight)
        adjusted_json['weight'] = weight  # Update weight in adjusted data
        
        # Use the collate_current_item layout
        current_item_layout = collate_current_item(adjusted_json, weight, meal_type)
        
        # Store the adjusted data
        return current_item_layout, weight_input, adjusted_json
    return "No nutritional data available.", dash.no_update, dash.no_update





# Callback to upload image and nutritional data to Google Cloud and Supabase
@app.callback(
    Output('output-upload-status', 'children'),
    Input('upload-button', 'n_clicks'),
    State('upload-image', 'filename'),
    State('upload-image', 'contents'),
    State('adjusted-nutritional-json-data', 'data')  # Use adjusted data
)
def upload_image_to_cloud(n_clicks, filename, image_contents, adjusted_json_nutrition_std):
    if n_clicks is not None and n_clicks > 0 and image_contents is not None:
        # Generate the ID
        id_str = generate_id()
        
        # Rename the image file to the generated ID with .png extension
        new_filename = f"{id_str}.png"
        
        # Process the image
        src_str, base64_image = process_image(image_contents)
        
        if base64_image:
            # Convert base64 image back to bytes for uploading
            decoded_image = base64.b64decode(base64_image)
            
            # Upload image to Google Cloud Storage with the new filename
            upload_image_to_gcs(GCS_BUCKET, new_filename, decoded_image)
            list_files_in_gcs(GCS_BUCKET)  # List all files in the bucket
            
            # Update the JSON data to include the ID
            if adjusted_json_nutrition_std is not None:
                adjusted_json_nutrition_std['id'] = id_str
                
                # Push the JSON data to Supabase
                try:
                    supabase_client = get_supabase_client()
                    success = insert_nutrition_data(supabase_client, 'sandbox_nutrition', adjusted_json_nutrition_std)
                    if success:
                        upload_status = f"Image '{new_filename}' and nutritional data successfully uploaded!"
                    else:
                        upload_status = f"Image '{new_filename}' uploaded, but error inserting data to Supabase."
                except Exception as e:
                    print(f"Error with Supabase: {str(e)}")
                    upload_status = f"Image '{new_filename}' uploaded, but error with Supabase: {str(e)}"
            else:
                upload_status = f"Image '{new_filename}' uploaded, but no nutritional data to insert."
            
            return upload_status
    return ""


@app.callback(
    Output('output-nutrition-data', 'children'),
    Input('display-button', 'n_clicks')
)
def display_nutritional_data(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        # Step 1: Fetch data from Supabase
        try:
            supabase_client = get_supabase_client()
            # Query to fetch and group data by date and sum for each date
            response = supabase_client.table('sandbox_nutrition')\
                .select("calories, carbohydrates, fat, protein, sugar, created_at")\
                .execute()

            if response.data:
                # Step 2: Process the data - group by date and sum the values
                nutrition_data = response.data
                
                # Convert 'created_at' to date only and sum values grouped by date
                from collections import defaultdict
                from datetime import datetime

                grouped_data = defaultdict(lambda: {'calories': 0, 'carbohydrates': 0, 'fat': 0, 'protein': 0, 'sugar': 0})

                for entry in nutrition_data:
                    # Convert created_at to date (handle fractional seconds)
                    date_str = datetime.strptime(entry['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d')
                    
                    # Sum the nutritional values per date
                    grouped_data[date_str]['calories'] += entry.get('calories', 0)
                    grouped_data[date_str]['carbohydrates'] += entry.get('carbohydrates', 0)
                    grouped_data[date_str]['fat'] += entry.get('fat', 0)
                    grouped_data[date_str]['protein'] += entry.get('protein', 0)
                    grouped_data[date_str]['sugar'] += entry.get('sugar', 0)

                # Step 3: Create a table to display the grouped data
                table_header = [
                    html.Thead(html.Tr([html.Th("Date"), html.Th("Calories"), html.Th("Carbohydrates"), html.Th("Fat"), html.Th("Protein"), html.Th("Sugar")]))
                ]
                table_rows = []

                for date, values in grouped_data.items():
                    row = html.Tr([
                        html.Td(date),
                        html.Td(f"{values['calories']:.2f}"),
                        html.Td(f"{values['carbohydrates']:.2f}g"),
                        html.Td(f"{values['fat']:.2f}g"),
                        html.Td(f"{values['protein']:.2f}g"),
                        html.Td(f"{values['sugar']:.2f}g"),
                    ])
                    table_rows.append(row)

                table_body = [html.Tbody(table_rows)]

                # Return the table to be displayed
                return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, striped=True)

            else:
                return "No data available."

        except Exception as e:
            print(f"Error fetching data from Supabase: {str(e)}")
            return f"Error fetching data: {str(e)}"
    return ""



if __name__ == '__main__':
    # Use the PORT environment variable if it's available, otherwise default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run_server(debug=True, host='0.0.0.0', port=port)
