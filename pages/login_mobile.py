# login.py

import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from utils_gc.supabase_utils import get_supabase_client


# login.py

# login.py

def create_login_layout():
    return dbc.Container([
        dcc.Store(id='login-mode', data='login'),
        dbc.Row([
            dbc.Col([
                html.H2("Login", id='login-header', className='text-center mb-4'),
                # Login fields
                html.Div([
                    dcc.Input(
                        id='login-username',
                        type='text',
                        placeholder='Enter your username',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                ], id='login-fields'),
                # Create profile fields
                html.Div([
                    dcc.Input(
                        id='create-username',
                        type='text',
                        placeholder='Choose a username',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-name',
                        type='text',
                        placeholder='Enter your name',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.DatePickerSingle(
                        id='create-dob',
                        placeholder='Enter your date of birth',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-height',
                        type='number',
                        placeholder='Enter your height in cm',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-weight',
                        type='number',
                        placeholder='Enter your weight in kg',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Textarea(
                        id='create-goals',
                        placeholder='Describe your fitness level, nutrition, and/or weight loss goals.',
                        className='mb-3',
                        style={'width': '100%', 'height': '100px'}
                    ),
                ], id='create-fields'),
                dbc.ButtonGroup([
                    dbc.Button('', id='primary-button', color='primary', style={'width': '150px'}),
                    dbc.Button('', id='toggle-mode-button', color='secondary', style={'width': '150px'}),
                ], className='d-flex justify-content-center mb-3'),
                html.Div(id='login-message', className='text-danger'),
            ], width=12)
        ], justify='center', class_name='mt-5')
    ])


# login.py

def create_login_validation_layout():
    return dbc.Container([
        dcc.Store(id='login-mode', data='login'),
        dbc.Row([
            dbc.Col([
                html.H2("Login", id='login-header', className='text-center mb-4'),
                html.Div(id='login-fields', children=[
                    # Include both login and create components
                    dcc.Input(
                        id='login-username',
                        type='text',
                        placeholder='Enter your username',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-username',
                        type='text',
                        placeholder='Choose a username',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-name',
                        type='text',
                        placeholder='Enter your name',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.DatePickerSingle(
                        id='create-dob',
                        placeholder='Enter your date of birth',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-height',
                        type='number',
                        placeholder='Enter your height in cm',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='create-weight',
                        type='number',
                        placeholder='Enter your weight in kg',
                        className='mb-3',
                        style={'width': '100%'}
                    ),
                    dcc.Textarea(
                        id='create-goals',
                        placeholder='Describe your fitness level, nutrition, and/or weight loss goals.',
                        className='mb-3',
                        style={'width': '100%', 'height': '100px'}
                    ),
                ]),
                dbc.ButtonGroup([
                    dbc.Button('', id='primary-button', color='primary', style={'width': '150px'}),
                    dbc.Button('', id='toggle-mode-button', color='secondary', style={'width': '150px'}),
                ], className='d-flex justify-content-center mb-3'),
                html.Div(id='login-message', className='text-danger')
            ], width=12)
        ], justify='center', class_name='mt-5')
    ])


def openai_user_settings_goals(user_data):
    import openai
    import os
    import json
    import re
    from datetime import datetime

    # Securely set your OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Extract user data
    name = user_data.get('name', 'User')
    weight = user_data.get('weight')
    height = user_data.get('height')
    dob = user_data.get('DOB')  # Assuming 'DOB' is a date string in 'YYYY-MM-DD'
    goals = user_data.get('goals', '')

    # Calculate age from DOB
    if dob:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    else:
        age = 'unknown'

    # Construct the prompt
    prompt = f"""
    You are a nutritionist assistant. A user has provided the following information:

    - Name: {name}
    - Age: {age}
    - Weight: {weight} kg
    - Height: {height} cm
    - Goals: {goals}

    Based on this information, estimate the user's daily nutritional intake goals in terms of:

    - Calories (kcal)
    - Carbohydrates (grams)
    - Protein (grams)
    - Fat (grams)

    Please provide your recommendations in JSON format with the keys: "kcal_goal", "carb_goal", "protein_goal", "fat_goal".

    Example format:

    {{
        "kcal_goal": 2000,
        "carb_goal": 250,
        "protein_goal": 75,
        "fat_goal": 55
    }}

    Ensure the response is only the JSON data without any additional text.
    """

    try:
        # Call the OpenAI API
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None
        )

        # Extract the text response
        text_response = response.choices[0].text.strip()

        # Use regex to extract JSON
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            goals_data = json.loads(json_text)
        else:
            raise ValueError("Failed to extract JSON from the response.")

        # Add the goals to processed_data
        processed_data = user_data.copy()
        processed_data.update({
            'kcal_goal': goals_data.get('kcal_goal'),
            'carb_goal': goals_data.get('carb_goal'),
            'protein_goal': goals_data.get('protein_goal'),
            'fat_goal': goals_data.get('fat_goal'),
        })

        return processed_data

    except Exception as e:
        print(f"Error in openai_user_settings_goals: {e}")
        # Handle exceptions appropriately
        # For now, return the original user_data
        return user_data




def register_login_callbacks(app):
    @app.callback(
        Output('primary-button', 'children'),
        Output('toggle-mode-button', 'children'),
        Input('login-mode', 'data')
    )
    def update_button_text(mode):
        if mode == 'login':
            return 'Login', 'Create Profile'
        elif mode == 'create':
            return 'Create Profile', 'Back to Login'
        else:
            return dash.no_update, dash.no_update

                
    @app.callback(
        Output('login-mode', 'data'),
        Input('toggle-mode-button', 'n_clicks'),
        State('login-mode', 'data'),
        prevent_initial_call=True
    )
    def switch_mode(n_clicks, mode):
        if n_clicks:
            if mode == 'login':
                return 'create'
            else:
                return 'login'
        return dash.no_update



    @app.callback(
        Output('session-store', 'data'),
        Output('url', 'pathname'),
        Output('login-message', 'children'),
        Input('primary-button', 'n_clicks'),
        State('login-mode', 'data'),
        State('login-username', 'value'),
        State('create-username', 'value'),
        State('create-name', 'value'),
        State('create-dob', 'date'),
        State('create-height', 'value'),
        State('create-weight', 'value'),
        State('create-goals', 'value'),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, mode, login_username, create_username, create_name, create_dob, create_height, create_weight, create_goals):
        try:
            if n_clicks:
                supabase = get_supabase_client()
                if mode == 'login':
                    if login_username:
                        username = login_username.strip()
                        response = supabase.table('user_profiles').select("*").eq('username', username).execute()
                        if response.data:
                            # Successful login
                            session_data = {'username': username}
                            return session_data, '/app', ''
                        else:
                            # Username not found
                            return dash.no_update, dash.no_update, 'Username not found.'
                    else:
                        # No username entered
                        return dash.no_update, dash.no_update, 'Please enter a username.'
                elif mode == 'create':
                    required_fields = [create_username, create_name, create_dob, create_height, create_weight]
                    if all(required_fields):
                        username = create_username.strip()
                        response = supabase.table('user_profiles').select("*").eq('username', username).execute()
                        if response.data:
                            return dash.no_update, dash.no_update, 'Username already exists.'
                        else:
                            user_data = {
                                'username': username,
                                'name': create_name.strip(),
                                'date_of_birth': create_dob,
                                'height': float(create_height),
                                'weight': float(create_weight),
                                # 'goals': create_goals.strip(),
                            }
                            # processed_data = openai_user_settings_goals(user_data)
                            response = supabase.table('user_profiles').insert(user_data).execute()
                            # print(response)
                            # if response.error is not None:  # Check for errors properly
                            #     return dash.no_update, dash.no_update, 'Error creating profile.'
                            # else:
                            return dash.no_update, '/', 'Profile created successfully. Please log in.'
                    else:
                        return dash.no_update, dash.no_update, 'Please fill in all fields.'
                else:
                    return dash.no_update, dash.no_update, dash.no_update
            else:
                return dash.no_update, dash.no_update, dash.no_update
        except Exception as e:
            print(f"Error in handle_login: {e}")
            return dash.no_update, dash.no_update, 'An error occurred.'

                                    
    @dash.callback(
        Output('login-fields', 'style'),
        Output('create-fields', 'style'),
        Output('login-header', 'children'),
        Input('login-mode', 'data')
    )
    def update_login_fields(mode):
        if mode == 'login':
            return {'display': 'block'}, {'display': 'none'}, "Login"
        elif mode == 'create':
            return {'display': 'none'}, {'display': 'block'}, "Create Profile"
        else:
            return dash.no_update, dash.no_update, dash.no_update


