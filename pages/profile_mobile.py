# profile.py

import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash
from utils_gc.supabase_utils import get_supabase_client

def create_profile_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("User Profile", className='text-center mb-4'),
                dbc.Form([
                    dbc.CardGroup([
                        dbc.Label("Name"),
                        dbc.Input(type="text", id="profile-name", placeholder="Enter your name"),
                    ]),
                    # Display Username (non-editable)
                    dbc.CardGroup([
                        dbc.Label("Username"),
                        dbc.Input(type="text", id="profile-username", disabled=True),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Date of Birth"),
                        dbc.Input(type="date", id="profile-dob"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Height (cm)"),
                        dbc.Input(type="number", id="profile-height", placeholder="Enter your height"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Weight (kg)"),
                        dbc.Input(type="number", id="profile-weight", placeholder="Enter your weight"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Activity Level"),
                        dcc.Dropdown(
                            id="profile-activity-level",
                            options=[
                                {"label": "1. No exercise", "value": "low"},
                                {"label": "2. Some exercise", "value": "medium"},
                                {"label": "3. A lot of exercise", "value": "high"},
                            ],
                            placeholder="Select activity level",
                            style={'width': '100%','width': '300px'}  # Set width to 100% of the parent container
                        ),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Calorie Goal"),
                        dbc.Input(type="number", id="profile-kcal-goal", placeholder="e.g., 2000"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Carbohydrate Goal (g)"),
                        dbc.Input(type="number", id="profile-carb-goal", placeholder="e.g., 250"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Protein Goal (g)"),
                        dbc.Input(type="number", id="profile-protein-goal", placeholder="e.g., 75"),
                    ]),
                    dbc.CardGroup([
                        dbc.Label("Fat Goal (g)"),
                        dbc.Input(type="number", id="profile-fat-goal", placeholder="e.g., 70"),
                    ]),
                    dbc.Button('Save Profile', id='save-profile-button', color='success', className='mt-3'),
                    html.Div(id='save-profile-message', className='text-success mt-2')
                ])
            ], width=6)
        ], justify='center', className='mt-5')
    ])


# profile.py (continued)


# profile.py (continued)

def register_profile_callbacks(app):
    @app.callback(
        Output('profile-username', 'value'),
        Output('profile-name', 'value'),
        Output('profile-dob', 'value'),
        Output('profile-height', 'value'),
        Output('profile-weight', 'value'),
        Output('profile-activity-level', 'value'),
        Output('profile-kcal-goal', 'value'),
        Output('profile-carb-goal', 'value'),
        Output('profile-protein-goal', 'value'),
        Output('profile-fat-goal', 'value'),
        Input('url', 'pathname'),
        State('session-store', 'data'),
    )
    def load_profile(pathname, session_data):
        if pathname == '/profile' and session_data:
            username = session_data.get('username')
            supabase = get_supabase_client()
            response = supabase.table('user_profiles').select("*").eq('username', username).execute()
            if response.data:
                profile = response.data[0]
                return (
                    profile.get('username', ''),
                    profile.get('name', ''),
                    profile.get('DOB', ''),
                    profile.get('height', ''),
                    profile.get('weight', ''),
                    profile.get('activity_level', ''),
                    profile.get('kcal_goal', ''),
                    profile.get('carb_goal', ''),
                    profile.get('protein_goal', ''),
                    profile.get('fat_goal', ''),
                )
        raise dash.exceptions.PreventUpdate


    @app.callback(
        Output('save-profile-message', 'children'),
        Input('save-profile-button', 'n_clicks'),
        State('profile-name', 'value'),
        State('profile-dob', 'value'),
        State('profile-height', 'value'),
        State('profile-weight', 'value'),
        State('profile-activity-level', 'value'),
        State('profile-kcal-goal', 'value'),
        State('profile-carb-goal', 'value'),
        State('profile-protein-goal', 'value'),
        State('profile-fat-goal', 'value'),
        State('session-store', 'data'),
        prevent_initial_call=True
    )
    def save_profile(n_clicks, name, dob, height, weight, activity_level, kcal_goal, carb_goal, protein_goal, fat_goal, session_data):
        if session_data:
            username = session_data.get('username')
            supabase = get_supabase_client()
            data = {
                'name': name,
                'DOB': dob,
                'height': height,
                'weight': weight,
                'activity_level': activity_level,
                'kcal_goal': kcal_goal,
                'carb_goal': carb_goal,
                'protein_goal': protein_goal,
                'fat_goal': fat_goal,
            }
            response = supabase.table('user_profiles').update(data).eq('username', username).execute()
            if response.error:
                return "Error saving profile."
            else:
                return "Profile saved successfully!"
        else:
            return "User not logged in."
