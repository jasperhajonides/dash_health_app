import dash
from dash import html, dcc, Input, Output, State, callback_context, MATCH, ALL
import time

import os
import datetime
import dash_bootstrap_components as dbc
import base64
from dotenv import load_dotenv
import json
import diskcache


# Import utility modules
from utils_gc.gcp_utils import upload_image_to_gcs, get_image_url_from_gcs, list_files_in_gcs, generate_id_and_custom_timestamp
from utils_gc.image_processing import process_image
from utils_gc.nutrition_utils import get_nutritional_info, adjust_nutritional_weight_values
from utils_gc.supabase_utils import get_supabase_client, insert_nutrition_data
from functions.nutrition_plots import create_circular_progress
from pages.nutrition_page_parts.current_item_mobile import collate_current_item
from pages.nutrition_page_parts.log_entries_mobile import create_todays_entries_layout
from pages.login_mobile import create_login_layout, register_login_callbacks, create_login_validation_layout
from pages.profile_mobile import create_profile_layout, register_profile_callbacks
from pages.navigation_mobile import create_navbar, register_navbar_callbacks
from pages.main_page_visualisations import register_visualisation_callbacks
# Set your Google Cloud Storage bucket name
GCS_BUCKET = 'dash_health_store'

# Load environment variables
load_dotenv()


# Ensure cache directory is outside the main process to prevent conflicts
if 'DASH_DEBUG_MODE' in os.environ:
    cache = diskcache.Cache("./cache")
else:
    cache = diskcache.Cache("/tmp/cache")
background_callback_manager = dash.long_callback.DiskcacheLongCallbackManager(cache)

external_stylesheets = [
    dbc.themes.MINTY,
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
]



# Initialize the app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                    suppress_callback_exceptions=True,  # Add this parameter
                    background_callback_manager=background_callback_manager,
)

server = app.server  # Expose the Flask server

# Get the current date
current_date = datetime.datetime.now().strftime('%A, %B %d, %Y')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store'),
    html.Div(id='page-content')
])

# Set validation_layout before registering callbacks
app.validation_layout = html.Div([
    app.layout,
    create_login_layout(),
    create_profile_layout(),
    # Include other layouts as needed
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    if pathname == '/':
        return create_login_layout()
    elif pathname == '/app':
        if session_data and 'username' in session_data:
            return html.Div([
                create_navbar(),
                dbc.Container([
                    # Daily Progress Section
                    html.Div(id='daily-progress', className='daily-progress-section'),

                    # Entries Section with sky blue background and rounded edges
                    html.Div([
                        # First Row: Image and Buttons
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    # Image Display with Delete Button
                                    html.Div([
                                        html.Img(id='uploaded-image', src='', style={'width': '100%'}),
                                        html.Button(
                                            '✖',  # Cross symbol
                                            id='delete-image-button',
                                            n_clicks=0,
                                            style={
                                                'position': 'absolute',
                                                'top': '5px',
                                                'right': '5px',
                                                'background-color': 'rgba(255, 255, 255, 0.7)',
                                                'border': 'none',
                                                'border-radius': '50%',
                                                'width': '25px',
                                                'height': '25px',
                                                'cursor': 'pointer',
                                                'font-size': '16px',
                                                'font-weight': 'bold',
                                                'display': 'none'  # Hidden by default
                                            }
                                        )
                                    ], style={'position': 'relative', 'display': 'inline-block'}),
                                ], id='output-image-preview', className='image-preview-container'),
                                width={'size': 4, 'order': 1},  # Image first on larger screens
                                xs=12,  # Full width on extra small screens
                                md=4    # 4-column width on medium screens and up
                            ),
                            dbc.Col(
                                html.Div([
                                    # Upload Button
                                    dcc.Upload(
                                        id='upload-image',
                                        children=dbc.Button('Upload Image', color='primary', className='mt-2',
                                                            style={'border-radius': '10px', 'width': '150px'}),
                                        multiple=False
                                    ),
                                    # Calculate Button
                                    dbc.Button('Calculate', id='calculate-button', color='success', className='mt-2',
                                            style={'border-radius': '10px', 'width': '150px'}),
                                    # Loading Spinner and Status Message using dcc.Loading
                                    # Replace the existing loading section with this:
                                    html.Div([
                                        dbc.Spinner(
                                            id="status-spinner",
                                            size="sm",  # Small size
                                            color="primary",
                                            fullscreen=False,
                                            spinner_style={'margin-right': '10px'},  # Spacing between spinner and message
                                        ),
                                        html.Div(id='output-calculate-status', style={'align-self': 'center'})
                                    ], style={'display': 'flex', 'align-items': 'center'})


                                ], className='buttons-container'),
                                width={'size': 8, 'order': 2},  # Buttons second on larger screens
                                xs=12,  # Full width on extra small screens
                                md=8    # 8-column width on medium screens and up
                            )
                        ], className='entries-row'),

                        # Second Row: Meal Type Dropdown and Image Description
                        dbc.Row([
                            dbc.Col(
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
                                width=6
                            ),
                            dbc.Col(
                                dbc.Input(id='image-description', type='text',
                                        placeholder='e.g., Grilled Chicken Salad', className='mt-2'),
                                width=6
                            )
                        ], className='entries-row'),

                        # Third Row: Weight Adjustment Div (hidden initially)
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    dbc.InputGroup([
                                        dbc.InputGroupText("Weight (grams):"),
                                        dbc.Input(id='weight-input', type='number', min=1, step=1,
                                                placeholder='Enter weight'),
                                        dbc.Button('Update', id='update-nutrition-button', color='secondary',
                                                className='ms-2'),
                                    ], className='mt-2'),
                                ], id='weight-adjustment-div', style={'display': 'none'}),
                                width=12
                            )
                        ], className='entries-row'),
                    ], className='entries-section',
                        style={'background-color': 'skyblue', 'padding': '10px', 'border-radius': '15px'}),

                    # Nutritional Information Section
                    dbc.Card([
                        dbc.CardHeader(html.H5("Nutritional Information")),
                        dbc.CardBody([
                            html.Div(id='nutritional-info', className='mt-3')
                        ])
                    ], className='mb-3'),

                    # Upload to Google Cloud Section
                    dcc.Interval(id='upload-status-interval', interval=2000, n_intervals=0, max_intervals=1),  # 2 seconds timeout

                    dbc.Card([
                        dbc.CardHeader(html.H5("Upload to Google Cloud")),
                        dbc.CardBody([
                            dbc.Button('Upload to Google Cloud', id='upload-button', color='info', className='mt-2'),
                            dbc.Toast(
                                id='output-upload-status',
                                header='Upload Status',
                                is_open=False,
                                dismissable=True,
                                icon='success',
                                duration=2000,  # 2 seconds
                                style={
                                    'position': 'fixed',
                                    'top': '50%',
                                    'left': '50%',
                                    'transform': 'translate(-50%, -50%)',
                                    'width': 350,
                                    'zIndex': 1500,  # Ensure it appears above other elements
                                },
                            ),
                        ])
                    ], className='mb-3'),

                    # Button group
                    # Updated Button group with larger size, padding, and centered alignment
                    html.Div(
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    html.I(className="fas fa-list"),
                                    id='btn-todays-entries',
                                    color='secondary',
                                    outline=True,
                                    className='btn-icon rounded-pill',
                                    style={
                                        'width': '80px',
                                        'height': '80px',
                                        'padding': '10px',
                                        'font-size': '24px',
                                        'margin': '5px'  # Adds spacing between buttons
                                    }
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-chart-bar"),
                                    id='btn-calorie-history',
                                    color='secondary',
                                    outline=True,
                                    className='btn-icon rounded-pill',
                                    style={
                                        'width': '80px',
                                        'height': '80px',
                                        'padding': '10px',
                                        'font-size': '24px',
                                        'margin': '5px'
                                    }
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-chart-line"),
                                    id='btn-cumulative-calories',
                                    color='secondary',
                                    outline=True,
                                    className='btn-icon rounded-pill',
                                    style={
                                        'width': '80px',
                                        'height': '80px',
                                        'padding': '10px',
                                        'font-size': '24px',
                                        'margin': '5px'
                                    }
                                ),
                            ],
                            size='lg',
                            className='mb-3'
                        ),
                        style={
                            'display': 'flex',
                            'justify-content': 'center'  # Centers the button group horizontally
                        }
                    ),


                    # Content container
                    html.Div(id='content-container'),


                    # Hidden stores for nutritional data
                    dcc.Store(id='nutritional-json-data'),
                    dcc.Store(id='adjusted-nutritional-json-data'),
                    dcc.Store(id='todays_nutritional_data', data=[]),
                    dcc.Store(id='data-refresh-trigger'),  # New store to trigger data refresh
                    dcc.Interval(id='interval-startup', interval=1*1000, n_intervals=0, max_intervals=1),
                    dcc.Store(id='selected-date-store', data=str(datetime.date.today())),
                    dcc.Store(id='active-button', data='btn-todays-entries'),  # for visualisations main page
                    dcc.Store(id='past-14-days-data', data=[]),  # for visualisation

                    # Add these to your layout inside dbc.Container or at the appropriate place
                    # Add this Interval component to your layout
                    dcc.Interval(id='interval-startup', interval=1*1000, n_intervals=0, max_intervals=1),

                    dcc.Store(id='todays-entries-data'),
                    dcc.Store(id='calorie-history-data'),
                    dcc.Store(id='cumulative-calories-data'),

                ], fluid=True)
        ])



        else:
            return create_login_layout()
    elif pathname == '/profile':
        if session_data and 'username' in session_data:
            return html.Div([
                create_navbar(),
                create_profile_layout()
            ])
        else:
            return create_login_layout()
    else:
        return '404'
    


# Register callbacks from modules
register_login_callbacks(app)
register_profile_callbacks(app)
register_navbar_callbacks(app)
register_visualisation_callbacks(app)
    
# Callback to fetch today's nutritional data on page load or when new data is uploaded or deleted
import datetime
import pytz

# Callback to fetch today's nutritional data on page load or when new data is uploaded or deleted
# Callback to fetch today's nutritional data on page load or when new data is uploaded or deleted
@app.callback(
    Output('todays_nutritional_data', 'data'),
    Input('interval-startup', 'n_intervals'),
    Input('output-upload-status', 'children'),
    Input('data-refresh-trigger', 'data'),
    Input('selected-date-store', 'data'),  # Changed from State to Input
    State('session-store', 'data'),
    prevent_initial_call=True
)
def fetch_todays_data(n_intervals, upload_status, refresh_trigger, selected_date, session_data):
    # Function body
    try:
        if not session_data or 'username' not in session_data:
            return []
        username = session_data['username']

        supabase_client = get_supabase_client()

        # Parse the selected date
        selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Define start and end of the selected day in UTC
        start_of_day = datetime.datetime.combine(selected_date_obj, datetime.time.min).replace(tzinfo=pytz.utc)
        end_of_day = datetime.datetime.combine(selected_date_obj, datetime.time.max).replace(tzinfo=pytz.utc)

        # Format timestamps for the query in ISO format
        start_str = start_of_day.isoformat()
        end_str = end_of_day.isoformat()

        # Query to fetch data for the current username and selected date
        response = supabase_client.table('sandbox_nutrition')\
                    .select("*")\
                    .eq('username', username)\
                    .gte('created_at', start_str)\
                    .lte('created_at', end_str)\
                    .execute()

        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        print(f"Error fetching data from Supabase: {str(e)}")
        return []
    

    from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import callback_context
from dash.exceptions import PreventUpdate

from dash import callback_context
from dash.exceptions import PreventUpdate

@app.callback(
    [Output('uploaded-image', 'src'),
     Output('delete-image-button', 'style')],
    [Input('upload-image', 'contents'),
     Input('delete-image-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_image(contents, n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if prop_id == 'upload-image' and contents:
            # Show the image and display the delete button
            return contents, {'display': 'block'}
        elif prop_id == 'delete-image-button' and n_clicks:
            # Clear the image and hide the delete button
            return '', {'display': 'none'}
        else:
            raise PreventUpdate



# Callback to update daily progress section
@app.callback(
    Output('daily-progress', 'children'),
    Input('todays_nutritional_data', 'data')
)
def update_daily_progress(todays_data):
    if todays_data:
        # Sum up the values
        total_calories = sum(item.get('calories', 0) for item in todays_data)
        total_protein = sum(item.get('protein', 0) for item in todays_data)
        total_fat = sum(item.get('fat', 0) for item in todays_data)
        total_carbs = sum(item.get('carbohydrates', 0) for item in todays_data)

        # Create the progression circles using create_circular_progress
        calories_progress = create_circular_progress(
            total_calories, 3400, " ", "Daily Calories", "#4CAF50",
            layout_direction='below', radius=65, fontsize_text=16, fontsize_num=30,
            stroke_width_backgr=8, stroke_width_complete=12, stroke_dashoffset=0
        )
        protein_progress = create_circular_progress(
            total_protein, 140, "", "Protein", "#ff6384", radius=45, fontsize_text=16, fontsize_num=24, layout_direction='below'
        )
        fat_progress = create_circular_progress(
            total_fat, 100, "", "Fat", "#36a2eb", radius=45, fontsize_text=16, fontsize_num=24
        )
        carbs_progress = create_circular_progress(
            total_carbs, 250, "", "Carbohydrates", "#4bc0c0", radius=45, fontsize_text=16, fontsize_num=24
        )

        # Arrange the circles
        progress_circles = html.Div(
            [
                # Calories progress circle centered
                html.Div(
                    calories_progress,
                    style={'display': 'flex', 'justify-content': 'center'}
                ),
                # Other three progress circles centered below
                html.Div(
                    [
                        html.Div(protein_progress, className='progress-circle-small'),
                        html.Div(fat_progress, className='progress-circle-small'),
                        html.Div(carbs_progress, className='progress-circle-small'),
                    ],
                    style={'display': 'flex', 'justify-content': 'center', 'margin-top': '20px'}
                )
            ],
            className='progress-circles-container'
        )

        return progress_circles
    else:
        return html.Div("No data for today.")

# # Callback to display image preview
# @app.callback(
#     Output('output-image-preview', 'children'),
#     Input('upload-image', 'contents'),
#     State('upload-image', 'filename')
# )
# def update_image_preview(image_contents, filename):
#     if image_contents is not None:
#         # Process the image (auto-rotate, crop to square, and resize)
#         src_str, base64_image = process_image(image_contents)

#         if src_str:
#             # Define the image style with gradient border and rounded edges
#             image_style = {
#                 'width': '128px',
#                 'height': '128px',
#                 'border-radius': '15px',
#                 'border': '5px solid transparent',  # Gradient border
#                 'background-image': 'linear-gradient(white, white), linear-gradient(to right, lightblue, darkblue)',
#                 'background-origin': 'border-box',
#                 'background-clip': 'content-box, border-box'
#             }
#             # Display the image preview
#             return html.Img(src=src_str, style=image_style)
#     return None

import time
from dash.long_callback import DiskcacheLongCallbackManager
@app.long_callback(
    output=[
        Output('output-calculate-status', 'children'),
        Output('nutritional-json-data', 'data'),
        Output('weight-adjustment-div', 'style'),
        Output('status-spinner', 'children')  # Add spinner toggle for tick or error icon
    ],
    inputs=[
        Input('calculate-button', 'n_clicks'),
        State('upload-image', 'contents'),
        State('image-description', 'value')
    ],
    progress=[Output('output-calculate-status', 'children')],
    running=[
        (Output('calculate-button', 'disabled'), True, False),
        (Output('upload-image', 'disabled'), True, False),
        (Output('image-description', 'disabled'), True, False),
        (Output('status-spinner', 'children'), dbc.Spinner(size="sm", color="primary"), html.I(className="fa fa-check text-success"))
    ],
    prevent_initial_call=True
)
def calculate_nutritional_info(set_progress, n_clicks, image_contents, description):
    if n_clicks is None or n_clicks == 0:
        return ("", None, {'display': 'none'}, "")

    if not image_contents and not description:
        set_progress(html.Div("Please add an image or text description."))
        return ("Please add an image or text description.", None, {'display': 'none'}, html.I(className="fa fa-exclamation-circle text-danger"))

    import time
    start_time = time.time()

    base64_image = None
    if image_contents:
        set_progress(html.Div("Processing image..."))
        src_str, base64_image = process_image(image_contents)

    set_progress(html.Div("Calculating nutritional information..."))

    json_nutrition_std = get_nutritional_info(base64_image, description, detail='all')

    if json_nutrition_std:
        end_time = time.time()
        calculation_time = end_time - start_time
        json_nutrition_std['calculation_time'] = calculation_time

        set_progress(html.Div(f"Nutritional information calculated successfully in {calculation_time:.2f} seconds."))

        return (
            f"Nutritional information calculated successfully in {calculation_time:.2f} seconds.",
            json_nutrition_std,
            {'display': 'block'},
            html.I(className="fa fa-check text-success")  # Success icon
        )
    else:
        set_progress(html.Div("Error in nutritional analysis."))
        return ("Error in nutritional analysis.", None, {'display': 'none'}, html.I(className="fa fa-exclamation-circle text-danger"))



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
    ctx = callback_context
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
        adjusted_json['meal_type'] = meal_type  # Include meal type

        
        # Use the collate_current_item layout
        recommended_intakes = {
            'calories': 2000,
            'carbohydrates': 300,
            'fat': 70,
            'protein': 50,
        }
        
        current_item_layout = collate_current_item(adjusted_json, weight, meal_type, recommended_intakes=recommended_intakes)
        
        # Store the adjusted data
        return current_item_layout, weight_input, adjusted_json
    return "No nutritional data available.", dash.no_update, dash.no_update



# Callback to toggle sub-bars
@app.callback(
    Output({'type': 'collapse', 'index': MATCH}, 'is_open'),
    Output({'type': 'toggle-button', 'index': MATCH}, 'children'),
    Input({'type': 'toggle-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'collapse', 'index': MATCH}, 'is_open'),
    State({'type': 'toggle-button', 'index': MATCH}, 'children'),
    prevent_initial_call=True,
)
def toggle_sub_bars(n_clicks, is_open, current_text):
    if n_clicks:
        new_is_open = not is_open
        if new_is_open:
            new_text = "Hide Breakdown"
        else:
            # Extract the nutrient name from the current text
            words = current_text.split()
            if words[0] == "Hide":
                nutrient_name = " ".join(words[2:])
            else:
                nutrient_name = " ".join(words[1:])
            new_text = f"Show {nutrient_name} breakdown"
        return new_is_open, new_text
    return is_open, current_text


# from datetime import datetime
import dash
from dash.exceptions import PreventUpdate

from dash.exceptions import PreventUpdate
import base64  # Ensure base64 is imported
import datetime

@app.callback(
    [
        Output('output-upload-status', 'children'),
        Output('output-upload-status', 'is_open'),
        Output('output-upload-status', 'icon')
    ],
    [
        Input('upload-button', 'n_clicks')
    ],
    [
        State('meal-type-dropdown', 'value'),  # Changed from Input to State
        State('selected-date-store', 'data'),   # Changed from Input to State
        State('upload-image', 'filename'),
        State('upload-image', 'contents'),
        State('adjusted-nutritional-json-data', 'data'),
        State('session-store', 'data'),
    ],
    prevent_initial_call=True
)
def upload_image_to_cloud(n_clicks, meal_type, selected_date, filename, image_contents, adjusted_json_nutrition_std, session_data):
    """
    Handles the upload of nutritional data and image to Google Cloud and Supabase.

    Parameters:
    - n_clicks: Number of times the upload button has been clicked.
    - meal_type: Selected meal type from the dropdown.
    - selected_date: The date selected for the entry.
    - filename: Name of the uploaded image file.
    - image_contents: Base64-encoded contents of the uploaded image.
    - adjusted_json_nutrition_std: Adjusted nutritional data.
    - session_data: User session data containing username.

    Returns:
    - upload_status: Status message to display to the user.
    - is_open: Boolean to control the visibility of the status toast.
    - icon: Icon indicating success, warning, or danger based on the outcome.
    """
    if not n_clicks:
        # If the button hasn't been clicked, do nothing
        raise PreventUpdate

    # Validate user session
    if not session_data or 'username' not in session_data:
        return 'User not logged in.', True, 'warning'

    username = session_data['username']
    print('USERNAME IN UPLOAD FUNCTION', username)

    # Generate the ID
    id_str, custom_timestamp = generate_id_and_custom_timestamp(selected_date)

    try:
        id_int = int(id_str)
    except ValueError:
        return 'Error generating ID.', True, 'warning'

    # Rename the image file to the generated ID with .png extension
    new_filename = f"{id_int}_{username}.png"

    # Process and upload the image
    if image_contents:
        try:
            src_str, base64_image = process_image(image_contents)
            if base64_image:
                # Convert base64 image back to bytes for uploading
                decoded_image = base64.b64decode(base64_image)

                # Upload image to Google Cloud Storage with the new filename
                upload_image_to_gcs(GCS_BUCKET, new_filename, decoded_image)
            else:
                upload_status = f"Error converting and uploading '{new_filename}'."
                return upload_status, True, 'warning'
        except Exception as e:
            upload_status = f"Error processing image: {str(e)}"
            return upload_status, True, 'danger'
    else:
        upload_status = "No image uploaded."
        return upload_status, True, 'warning'

    # Update the JSON data to include the ID and image filename
    if adjusted_json_nutrition_std:
        adjusted_json_nutrition_std['id'] = id_int
        adjusted_json_nutrition_std['image_filename'] = new_filename
        adjusted_json_nutrition_std['username'] = username
        adjusted_json_nutrition_std['meal_type'] = meal_type
        adjusted_json_nutrition_std['date'] = selected_date
        adjusted_json_nutrition_std['created_at'] = custom_timestamp  # Add the custom created_at timestamp

        # Push the JSON data to Supabase
        try:
            supabase_client = get_supabase_client()
            success = insert_nutrition_data(supabase_client, 'sandbox_nutrition', adjusted_json_nutrition_std)
            if success:
                # Get current local time
                local_time = datetime.datetime.now().strftime('%H:%M:%S')

                # After successful operations
                upload_status = f"Success! Added at {local_time}"
                return upload_status, True, 'success'
            else:
                upload_status = f"Error inserting data to Supabase."
                return upload_status, True, 'danger'
        except Exception as e:
            print(f"Error with Supabase: {str(e)}")
            upload_status = f"Errored out with Supabase: {str(e)}"
            return upload_status, True, 'danger'
    else:
        upload_status = "No nutritional information found."
        return upload_status, True, 'danger'



# Callback to update today's entries
@app.callback(
    Output('todays-entries-container', 'children'),
    Input('todays_nutritional_data', 'data')
)
def update_todays_entries(data):
    if not data:
        return html.Div("No entries found for today.")
    return create_todays_entries_layout(data)

# Callback to handle deletion of entries
@app.callback(
    Output('data-refresh-trigger', 'data'),
    Input({'type': 'delete-button', 'index': ALL}, 'n_clicks_timestamp'),
    prevent_initial_call=True
)
def delete_entry(n_clicks_timestamp_list):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Get the IDs and timestamps of all delete buttons
    inputs = ctx.inputs
    timestamp_by_id = {}
    for k, v in inputs.items():
        id_str = k.split('.')[0]
        id_dict = json.loads(id_str.replace("'", '"'))
        entry_id = id_dict['index']
        timestamp = v
        if timestamp is not None:
            timestamp_by_id[entry_id] = timestamp

    if not timestamp_by_id:
        raise dash.exceptions.PreventUpdate

    # Find the entry_id with the latest timestamp
    entry_id = max(timestamp_by_id, key=timestamp_by_id.get)

    # Perform deletion from Supabase
    delete_entry_from_supabase(entry_id)

    # Return a value to trigger data refresh
    return str(datetime.datetime.now())

def delete_entry_from_supabase(entry_id):
    try:
        supabase_client = get_supabase_client()
        supabase_client.table('sandbox_nutrition').delete().eq('id', entry_id).execute()
    except Exception as e:
        print(f"Error deleting entry from Supabase: {str(e)}")


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

                grouped_data = defaultdict(lambda: {'calories': 0, 'carbohydrates': 0, 'fat': 0, 'protein': 0, 'sugar': 0})

                for entry in nutrition_data:
                    # Convert created_at to date (handle fractional seconds)
                    date_str = datetime.datetime.strptime(entry['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d')
                    
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