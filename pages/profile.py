from dash.dependencies import Input, Output, State, MATCH, ALL
from dash import Dash, dcc, html, Input, Output, State, callback_context, MATCH, ALL

import json
import dash
import dash_bootstrap_components as dbc

import time

from dash import Input, State, Output


# Placeholder user data and nutritional recommendations (Ensure data is fetched or calculated appropriately)

# Updated user_info dictionary to include "Date of Birth"
# user_info = {
#     "Name": "John Doe",
#     "Weight": 70,  # kg
#     "Height": 175,  # cm
#     "Sports": "Running, Cycling, Swimming",
#     "Date of Birth": "1990-01-01",
#     "Location": "New York",
#     "Member Since": "2023-01-01"
# }

activity_levels = [
    "Easy walking throughout the week.",
    "1-2 sessions with 30 minutes of exercise where you get your heart rate up slightly.",
    "2-4 weekly sessions with a few sessions with some 150+ HR sessions",
    "4-7 sessions in a week of 30mins or more.",
    "7-10 sessions throughout the week including some interval sessions.",
    "A serious, well-rounded training schedule of 10-14 sessions throughout the week.",
    "14+ sessions in the week including intervals and cardio sessions."
]

# For the sake of example, let's use simplified nutritional data. You'll need to replace these with actual dynamic values.
daily_macros = {
    "Calories": 2500,  # kcal
    "Protein": 150,    # g
    "Fat": 70,         # g
    "Carbohydrates": 300  # g
}

vitamins = {
    "Vitamin A": 900,  # mcg
    "Vitamin C": 90,   # mg
    "Vitamin D": 20,   # mcg
    "Vitamin E": 15,   # mg
    "Vitamin K": 120   # mcg
}

amino_acids = {
    "Histidine": 14,
    "Isoleucine": 20,
    "Leucine": 42,
    "Lysine": 38,
    "Methionine": 19
}

minerals = {
    "Calcium": 1000,      # mg
    "Iron": 8,            # mg
    "Magnesium": 420,     # mg
    "Phosphorus": 700,    # mg
    "Potassium": 3400     # mg
}

sugars_fibers = {
    "Sugar": "",          # Placeholder
    "Fiber": "",          # Placeholder
    "Glucose": "",        # Placeholder
    "Fructose": "",       # Placeholder
    "Galactose": "",      # Placeholder
    "Lactose": "",        # Placeholder
    "Soluble Fiber": "",  # Placeholder
    "Insoluble Fiber": "" # Placeholder
}

fats = {
    "Saturated Fat": "",   # Placeholder
    "Unsaturated Fat": "", # Placeholder
    "Cholesterol": ""      # Placeholder
}


def create_info_field(label, value, editable=False, field_id=None):
    # Adjust id structure to use pattern-matching keys
    if editable:
        if not field_id:
            raise ValueError("field_id must be provided for editable fields.")
        
        input_id = {'type': 'editable-input', 'index': field_id}  # field_id example: 'user-profile-name'
    else:
        input_id = None

    return dbc.InputGroup(
        [
            dbc.InputGroupText(label),
            dbc.Input(value=value, type="text", id=input_id,
                       className="mb-3") if editable else html.P(value, className="lead"),
        ],
        className="mb-3",
    )



# Utility function to generate cards for nutritional categories, making values editable
def create_nutritional_card(info, title, section):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.Div([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(key),
                        dbc.Input(type="text", value=value, id={'type': 'editable-input', 'index': f"{section}-{key}"}),
                    ],
                    className="mb-2",
                ) for key, value in info.items() if isinstance(value, dict)
            ] + [
                create_info_field(key, value, editable=True, field_id=f"{section}-{key}")
                for key, value in info.items() if not isinstance(value, dict)
            ]),
        ]),
        className="h-100",
    )


def profile_layout(user_data_instance):
    user_profile = user_data_instance.user_profile
    api_profile = user_data_instance.api_profile  # Direct access, no ["api_profile"] needed

    # Assuming 'activity_profile' is part of 'user_profile' based on your initial structure
    activity_profile = user_profile.get("activity_profile", {})  # Provides an empty dict as default if not found
    nutritional_info = user_data_instance.nutritional_info  # Directly access nutritional_info
    # Define the layout
    layout = html.Div([
        # Omitting head elements like styles and scripts, which should be in the assets folder or handled via Dash's external_stylesheets
        html.Div(className="workbench-container", children=[
            # User Settings Menu Container
            html.Div(className="usersettingsmenu-container", children=[
                html.Div(className="usersettingsmenu-options", children=[
                    html.H1("User Profile", className="usersettingsmenu-text"),
                    html.Div(className="usersettingsmenu-container1", children=[
                        html.Span("Name", className="usersettingsmenu-text1"),
                        dcc.Input(
                            value=user_profile.get("name", ""),
                            id={'type': 'user-info', 'field': 'name'},
                            type="text",
                            placeholder="John Smith",
                            className="usersettingsmenu-textinput input",
                        ),
                    ]),
                    html.Div(className="usersettingsmenu-container2", children=[
                        html.Span("Weight", className="usersettingsmenu-text2"),
                        dcc.Input(
                            value=user_profile.get("weight", ""),
                            id={'type': 'user-info', 'field': 'weight'},
                            type="text",
                            placeholder="0 kg",
                            className="usersettingsmenu-textinput1 input"
                        ),
                    ]),
                    html.Div(className="usersettingsmenu-container3", children=[
                        html.Span("Height", className="usersettingsmenu-text3"),
                        dcc.Input(
                            value=user_profile.get("height", ""),
                            id={'type': 'user-info', 'field': 'height'},
                            type="text",
                            placeholder="0 cm",
                            className="usersettingsmenu-textinput2 input"
                        ),
                    ]),
                    html.Div(className="usersettingsmenu-container4", children=[
                        html.Span("Date of Birth", className="usersettingsmenu-text4"),
                        dcc.Input(
                            value=user_profile.get("dob", ""),
                            id={'type': 'user-info', 'field': 'dob'},
                            type="text",
                            placeholder="01-01-1990",
                            className="usersettingsmenu-textinput3 input"
                        ),
                    ]),
                    html.Div(className="usersettingsmenu-container5", children=[
                        html.Span("Location", className="usersettingsmenu-text5"),
                        dcc.Input(
                            value=user_profile.get("location", ""),
                            id={'type': 'user-info', 'field': 'location'},
                            type="text",
                            placeholder="London, UK",
                            className="usersettingsmenu-textinput4 input"
                        ),
                    ]),
                    html.Div(className="usersettingsmenu-container6", children=[
                        html.Span("Activity levels", className="usersettingsmenu-text6"),
                        dcc.Dropdown(
                            value=activity_profile.get("activity_level", ""),
                            id={'type': 'user-info', 'field': 'activity_level'},
                            options=[
                                {"label": "1. No exercise", "value": "low"},
                                {"label": "2. Some exercise", "value": "medium"},
                                {"label": "3. A lot of exercise", "value": "high"},
                            ],
                            className="usersettingsmenu-select"
                        ),
                    ]),
                ]),
                html.Button("Save", id={'type': 'save-btn', 'section': 'user-info'}, className="save-btn")
            ]),
            # API Settings Container
            html.Div(className="apisettings-container apisettings-root-class-name", children=[
                html.Div(className="apisettings-options", children=[
                    html.H1("API settings", className="apisettings-text"),
                    html.Div(className="apisettings-container1", children=[
                        html.Span("OpenAI API key", className="apisettings-apikeys"),
                        dcc.Input(
                            value=api_profile.get("openai_api_key", ""),
                            id={'type': 'api-settings', 'field': 'openai_api_key'},
                            type="text",
                            placeholder="rc3****************x3",
                            className="apisettings-apikeyinput input"
                        ),
                    ]),
                    html.Div(className="apisettings-textqualitysettings", children=[
                        html.Span("Text Quality", className="apisettings-textqualitydesc"),
                        dcc.Dropdown(
                            value=api_profile.get("text_quality_settings", None),
                            id={'type': 'api-settings', 'field': 'text_quality_settings'},
                            options=[
                                {"label": "Base Quality (gpt3.5)", "value": "base"},
                                {"label": "High Quality (gpt4)", "value": "high"},
                            ],
                            className="apisettings-textqualityoptions"
                        ),
                    ]),
                    html.Div(className="apisettings-imagequalitysettings", children=[
                        html.Span("Image Quality", className="apisettings-imagequalitydesc"),
                        dcc.Dropdown(
                            value=api_profile.get("image_quality_settings", None),
                            id={'type': 'api-settings', 'field': 'image_quality_settings'},
                            options=[
                                {"label": "Base Quality (512x512px)", "value": "base"},
                                {"label": "High Quality (768x2000px)", "value": "high"},
                            ],
                            className="apisettings-imagequalityoptions"
                        ),
                    ]),
                ]),
                html.Button("Save User Info", id={'type': 'save-btn', 'section': 'api-settings'}, className="save-btn"),


            ]),
        ]),
        
        # html.Div([
        #     html.H3("Nutritional Information", className="text-center mb-4 section-header"),
        #     html.P("This section indicates the recommended daily limits. Press \"Predict\" to get tailor-made predictions for your profile. Edit quantities where required.",
        #         className="text-center mb-4", id="nutrition-subtitle"),
        #     dbc.Row(
        #         dbc.Col(
        #             dbc.Button("Predict", color="info", className="me-1", id="predict-button"),
        #             width={"size": 6, "offset": 3},
        #         ),
        #         className="mb-4"
        #     ),
        #     dbc.Container(fluid=True, children=[
        #                 dbc.Row([
        #                     dbc.Col(create_nutritional_card(nutritional_info['daily_macros'], "Daily Macros", "daily_macros"), md=4),
        #                     dbc.Col(create_nutritional_card(nutritional_info['vitamins'], "Vitamins", "vitamins"), md=4),
        #                     dbc.Col(create_nutritional_card(nutritional_info['amino_acids'], "Amino Acids", "amino_acids"), md=4),
        #                 ], className="mb-4"),
        #                 dbc.Row([
        #                     dbc.Col(create_nutritional_card(nutritional_info['minerals'], "Minerals", "minerals"), md=4),
        #                     dbc.Col(create_nutritional_card(nutritional_info['sugars_fibers'], "Sugars & Fibers", "sugars_fibers"), md=4),
        #                     dbc.Col(create_nutritional_card(nutritional_info['fats'], "Fats", "fats"), md=4),
        #                 ]),

        #             ]),
        # # dbc.Row([
        # #         dbc.Col([
        # #             dbc.Button("Save Nutritional Info", id={'type': 'save-btn', 'section': 'nutritional-info'}, className="save-btn")
        # #         ], width={"size": 6, "offset": 3}),
        # #     ]),

        # ], className="section-box"),

        html.Div(id='save-success-notification'),

    ], className="main-background")

    return layout

########### functions

# Similarly adjust create_nutritional_card to assign appropriate ids to inputs


########## callbacks

from dash.dependencies import Input, Output, State, MATCH, ALL

# Update callback_functions_profile to handle both profile and nutritional info saves
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import json

# def callback_functions_profile(app, user_data_instance):

#     @app.callback(
#         Output('slider-text-output', 'children'),
#         [Input('activity-level-slider', 'value')]
#     )
#     def update_output(value):
#         return activity_levels[value - 1]





def callback_functions_profile(app, user_data_instance):

    @app.callback(
        Output('save-success-notification', 'children'),
        [
            Input({'type': 'save-btn', 'section': ALL}, 'n_clicks'),  # This matches the button's ID pattern
            ],
        [
            State({'type': ALL, 'field': ALL}, 'value'),
            State({'type': ALL, 'field': ALL}, 'id')
         ],
        prevent_initial_call=True
    )
    def save_section_info(n_clicks, values, ids):
        print('...')
        if not callback_context.triggered:
            raise PreventUpdate
        print("click")
        triggered_id = json.loads(callback_context.triggered[0]['prop_id'].split('.')[0])
        section = triggered_id['section']
        print('section', section, time.time() )
        user_profile_updates = {}
        api_profile_updates = {}
        nutritional_info_updates = {}

        for value, id_info in zip(values, ids):
            print(value, id_info)
            section_type = id_info['type']
            field = id_info['field']

            if section_type == 'user-info':
                user_profile_updates[field] = value
            elif section_type == 'api-settings':
                api_profile_updates[field] = value
            elif section_type == 'nutritional-info':
                category, subfield = field.split('-')
                if category not in nutritional_info_updates:
                    nutritional_info_updates[category] = {}
                nutritional_info_updates[category][subfield] = value

        if section == 'user-info':
            user_data_instance.user_profile.update(user_profile_updates)
        elif section == 'api-settings':
            user_data_instance.api_profile.update(api_profile_updates)
            print('these are the proposed API changes:', api_profile_updates)

        elif section == 'nutritional-info':
            for category, updates in nutritional_info_updates.items():
                if category in user_data_instance.nutritional_info:
                    user_data_instance.nutritional_info[category].update(updates)

        user_data_instance.update_csv_user_data()

        return f"Data in section {section} saved successfully!"
