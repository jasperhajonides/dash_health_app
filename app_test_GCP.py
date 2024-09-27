# app.py

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import os
from datetime import datetime
import base64
from utils_gc.gcp_utils import upload_image_to_gcs, get_image_url_from_gcs, list_files_in_gcs, generate_id
from utils_gc.image_processing import process_image
from utils_gc.nutrition_utils import get_nutritional_info, adjust_nutritional_weight_values, display_nutritional_info
from utils_gc.supabase_utils import get_supabase_client, insert_nutrition_data
from pages.nutrition_page_parts.current_item_mobile import collate_current_item

external_stylesheets = [
    dbc.themes.CERULEAN,
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Navbar with menu icon
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand(datetime.now().strftime("%A, %d %B %Y"), className="ml-2")),
                    ],
                    align="center",
                    class_name="g-0",
                ),
                href="#",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Home", href="#"),
                    dbc.DropdownMenuItem("Profile", href="#"),
                    dbc.DropdownMenuItem("Settings", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label=html.I(className="fa fa-bars", style={"font-size": "24px", "color": "white"}),
                right=True,
                toggle_style={"color": "white", "border": "none", "background": "none"},
                className="ml-auto",
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="navbar-custom",
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Submit Photo and Calculate", className="text-center text-primary mt-3"),
                        html.Div(
                            [
                                # Upload button and Calculate button side by side
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label(
                                                    [
                                                        dbc.Button(
                                                            "Upload Photo",
                                                            color="primary",
                                                            className="btn-custom",
                                                        ),
                                                        dcc.Upload(
                                                            id="upload-image",
                                                            accept="image/*",
                                                            children=html.Div(),
                                                        ),
                                                    ],
                                                    className="upload-button-label",
                                                ),
                                            ],
                                            width=6,
                                            className="text-center",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Calculate",
                                                    id="calculate-button",
                                                    color="success",
                                                    className="btn-custom",
                                                    disabled=True,
                                                ),
                                            ],
                                            width=6,
                                            className="text-center",
                                        ),
                                    ],
                                    className="mt-2",
                                ),
                                # Image preview
                                html.Div(id="output-image-preview", className="mt-3"),
                                # Text input box below the picture
                                dbc.Input(
                                    id="image-description",
                                    type="text",
                                    placeholder="Describe the image (optional)",
                                    className="mt-3",
                                    style={"borderRadius": "10px", "padding": "10px"},
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
        # Display collate_current_item content
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id="nutritional-info", className="mt-4"),
                    ],
                    width=12,
                ),
            ]
        ),
        # Submit button
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            "Submit",
                            id="upload-button",
                            color="info",
                            className="btn-custom btn-block mt-3",
                            disabled=False,
                        ),
                        html.Div(id="output-upload-status", className="mt-3 text-center"),
                    ],
                    width=12,
                ),
            ]
        ),
        # Hidden store for nutritional data
        dcc.Store(id="nutritional-json-data"),
    ],
    fluid=True,
    style={"padding": "0px"},
)

# Callbacks and functions remain the same, but with adjustments to IDs and components

# Callback to enable Calculate button when an image is uploaded
@app.callback(
    Output("calculate-button", "disabled"),
    Input("upload-image", "contents"),
)
def enable_calculate_button(image_contents):
    if image_contents is not None:
        return False  # Enable button
    return True  # Disable button

# Callback to display image preview
@app.callback(
    Output("output-image-preview", "children"),
    Input("upload-image", "contents"),
)
def update_image_preview(image_contents):
    if image_contents is not None:
        # Process the image
        src_str, base64_image = process_image(image_contents)

        if src_str:
            # Display the image preview
            return html.Div(
                [
                    html.Img(src=src_str, style={"max-width": "100%", "height": "auto", "borderRadius": "10px"}),
                ]
            )
    return None

# Modify the calculate_nutritional_info callback
@app.callback(
    Output("nutritional-json-data", "data"),
    Input("calculate-button", "n_clicks"),
    State("upload-image", "contents"),
    State("image-description", "value"),
)
def calculate_nutritional_info(n_clicks, image_contents, description):
    if n_clicks and image_contents:
        # Process the image
        src_str, base64_image = process_image(image_contents)

        if base64_image:
            # Get nutritional information
            json_nutrition_std = get_nutritional_info(base64_image, description)
            if json_nutrition_std:
                return json_nutrition_std
    return None

# Callback to display nutritional info using collate_current_item
@app.callback(
    Output("nutritional-info", "children"),
    Input("nutritional-json-data", "data"),
)
def display_nutritional_info_callback(json_entry):
    if json_entry is not None:
        weight_input = json_entry.get("weight", 100)
        meal_type = "other"  # Default meal type
        current_item_layout = collate_current_item(json_entry, weight_input, meal_type)
        return current_item_layout
    return None

# Callback to handle submission (Upload to Google Cloud)
@app.callback(
    Output("output-upload-status", "children"),
    Input("upload-button", "n_clicks"),
    State("upload-image", "filename"),
    State("upload-image", "contents"),
    State("nutritional-json-data", "data"),
)
def upload_image_to_cloud(n_clicks, filename, image_contents, json_nutrition_std):
    if n_clicks and image_contents and json_nutrition_std:
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

            # Update the JSON data to include the ID
            json_nutrition_std["id"] = id_str

            # Push the JSON data to Supabase
            try:
                supabase_client = get_supabase_client()
                success = insert_nutrition_data(supabase_client, "sandbox_nutrition", json_nutrition_std)
                if success:
                    upload_status = "Data successfully uploaded!"
                else:
                    upload_status = "Error inserting data to Supabase."
            except Exception as e:
                print(f"Error with Supabase: {str(e)}")
                upload_status = f"Error with Supabase: {str(e)}"

            return upload_status
    return ""

if __name__ == "__main__":
    app.run_server(debug=False)
