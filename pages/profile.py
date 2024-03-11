from dash.dependencies import Input, Output, State, MATCH, ALL
import json
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


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

def create_activity_level_slider(activity_profile):
    # Extract activity level from user_data_instance, defaulting to 1 if not found
    activity_level = activity_profile.user_info.get("activity_profile", {}).get("activity_level", 1)
    slider = dcc.Slider(
        id='activity-level-slider',
        min=1,
        max=7,
        step=1,
        value=activity_level,  # Use the extracted or default activity level
        marks={i: str(i) for i in range(1, 8)},
        className="mb-3",
    )

    return html.Div(id='slider-output-container', children=[slider])


def profile_layout(user_data_instance):
    user_profile = user_data_instance.user_info["user_profile"]
    activity_profile = user_data_instance.user_info["activity_profile"]

    nutritional_info = user_data_instance.get_nutritional_info()  # Example method to get nutritional info

    # Define the layout
    layout = html.Div([
            html.Div([
            html.H2("User Profile", className="text-center mb-4 section-header"),
            dbc.Container(fluid=True, children=[
                dbc.Row([
                    dbc.Col([
                        create_info_field("Name", user_profile["name"]),
                        create_info_field("Weight", user_profile["weight"], editable=True,field_id="user_profile-weight"),
                        create_info_field("Height", user_profile["height"], editable=True, field_id="user_profile-height"),
                        create_info_field("Sports", activity_profile["sports"]),
                    ], md=6),
                    dbc.Col([
                        create_info_field("Date of Birth", user_profile["dob"]),
                        create_info_field("Location", user_profile["location"]),
                        create_info_field("Member since", user_profile["member_since"]),
                    ], md=6),
                ], className="mb-4"),
                html.H4("Activity Level", className="text-center mb-3"),
                dbc.Row(
                    dbc.Col([
                        html.Div(id="slider-text-output", className="text-center"),
                        create_activity_level_slider(user_data_instance),  # This replaces the direct dcc.Slider creatio
                    ], width=12),
                ),
            ]),
            dbc.Row(
                dbc.Col([
                    dbc.Button("Save Profile", id={'type': 'save-btn', 'section': 'user-profile'}, className="mt-2")
                ], width={"size": 6, "offset": 3}),
                className="mb-4"),

        ], className="section-box"),
        
        html.Div([
            html.H3("Nutritional Information", className="text-center mb-4 section-header"),
            html.P("This section indicates the recommended daily limits. Press \"Predict\" to get tailor-made predictions for your profile. Edit quantities where required.",
                className="text-center mb-4", id="nutrition-subtitle"),
            dbc.Row(
                dbc.Col(
                    dbc.Button("Predict", color="info", className="me-1", id="predict-button"),
                    width={"size": 6, "offset": 3},
                ),
                className="mb-4"
            ),
            dbc.Container(fluid=True, children=[
                        dbc.Row([
                            dbc.Col(create_nutritional_card(nutritional_info['daily_macros'], "Daily Macros", "daily_macros"), md=4),
                            dbc.Col(create_nutritional_card(nutritional_info['vitamins'], "Vitamins", "vitamins"), md=4),
                            dbc.Col(create_nutritional_card(nutritional_info['amino_acids'], "Amino Acids", "amino_acids"), md=4),
                        ], className="mb-4"),
                        dbc.Row([
                            dbc.Col(create_nutritional_card(nutritional_info['minerals'], "Minerals", "minerals"), md=4),
                            dbc.Col(create_nutritional_card(nutritional_info['sugars_fibers'], "Sugars & Fibers", "sugars_fibers"), md=4),
                            dbc.Col(create_nutritional_card(nutritional_info['fats'], "Fats", "fats"), md=4),
                        ]),
                    ]),
        dbc.Row([
                dbc.Col([
                    dbc.Button("Save Nutritional Info", id={'type': 'save-btn', 'section': 'nutritional-info'}, className="mt-2")
                ], width={"size": 6, "offset": 3}),
            ]),

        ], className="section-box"),
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

def callback_functions_profile(app, user_data_instance):

    @app.callback(
        Output('slider-text-output', 'children'),
        [Input('activity-level-slider', 'value')]
    )
    def update_output(value):
        return activity_levels[value - 1]

    @app.callback(
        Output('save-success-notification', 'children'),
        [Input({'type': 'save-btn', 'section': ALL}, 'n_clicks')],
        [State({'type': 'editable-input', 'index': ALL}, 'value'),
         State({'type': 'editable-input', 'index': ALL}, 'id')],
        prevent_initial_call=True
    )
    def save_section_info(n_clicks, values, ids):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        triggered_id = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])
        print("Button ID Dict:", triggered_id)

        section_updates = {}
        nutritional_info_subcategories = [
            'daily_macros', 'vitamins', 'amino_acids', 'minerals', 'sugars_fibers', 'fats'
        ]


        # Process updates 
        for value, id_info in zip(values, ids):
            # Extract category and field from id_info['index']
            parts = id_info['index'].split('-')
            if (parts[0] in nutritional_info_subcategories) or (parts[0] in ['user_profile']):
                category = parts[0]
                field = '-'.join(parts[1:])

                if category not in section_updates:
                    section_updates[category] = {}
                section_updates[category][field] = value
    

        # Perform the update based on the section
        if triggered_id['section'] == 'nutritional-info':
            user_data_instance.update_nutritional_info_bulk(section_updates)
            print("Updated Nutritional Info:", section_updates)
        else:  # Assuming all other sections are for user_info
            user_data_instance.update_user_info_bulk(section_updates)
            print("Updated User Info:", section_updates)

        user_data_instance.print_user_info()
        if triggered_id['section'] == 'nutritional-info':
            user_data_instance.print_nutrition_info()

        return "Data saved successfully!"
