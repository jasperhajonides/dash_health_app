from dash import html, dcc, Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate

import dash
import dash_bootstrap_components as dbc
import dash_iconify as di
from datetime import datetime, timedelta
import pandas as pd
import os
import json

from pages.nutrition_page_parts.daily_overview import create_daily_feed



import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env


from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_iconify as di
import os

custom_js = html.Script(src='/assets/datatable_logging.js')


def create_daily_feed(df, images_folder, selected_date):
    # Custom sort the DataFrame by 'meal_type'
    meal_order = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Other']
    df['meal_type'] = pd.Categorical(df['meal_type'], categories=meal_order, ordered=True)
    df_sorted = df.sort_values(['meal_type', 'date'])

    table_header = html.Thead(
        html.Tr([
            html.Th("Meal Type", style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '16px'}),
            html.Th("Quantity"),
            html.Th("Image"),
            html.Th("Name"),
            html.Th("kcal"),
            html.Th("Carbs (g)"),
            html.Th("Fat (g)"),
            html.Th("Protein (g)"),
        ])
    )

    table_body_rows = []
    current_meal_type = None
    for index, row in df_sorted.iterrows():
        # Check if the meal type has changed
        if row['meal_type'] != current_meal_type:
            # Insert a header row for the new meal type
            table_body_rows.append(html.Tr([
                html.Td(row['meal_type'], colSpan="8", style={'fontWeight': 'bold', 'fontSize': '18px', 'textAlign': 'center', 'backgroundColor': '#e9ecef'}),
            ]))
            current_meal_type = row['meal_type']

        # Insert row for the current entry
        units = row.get('units', 1)
        calories = row.get('calories', 'N/A') * units if row.get('calories', 'N/A') != 'N/A' else 'N/A'
        carbohydrates = row.get('carbs', 'N/A') * units if row.get('carbs', 'N/A') != 'N/A' else 'N/A'
        fat = row.get('fat', 'N/A') * units if row.get('fat', 'N/A') != 'N/A' else 'N/A'
        protein = row.get('protein', 'N/A') * units if row.get('protein', 'N/A') != 'N/A' else 'N/A'
        image_filename = row.get('file_name', 'default_file_name.png')
        image_path = f"{images_folder}/{image_filename}"

        table_body_rows.append(html.Tr([
            html.Td([  # Include buttons for increasing or decreasing the unit count
                html.Button('-', id={'type': 'unit-decrease', 'index': index}, 
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 
                                'box-shadow': '0 2px 4px rgba(0,0,0,0.2)', 'margin-right': '5px'}),
                html.Span(f"{units:.1f}"),  # Display units rounded to one decimal point
                html.Button('+', id={'type': 'unit-increase', 'index': index}, 
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 
                                'box-shadow': '0 2px 4px rgba(0,0,0,0.2)', 'margin-left': '5px'}),
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
            html.Td(html.Img(src=image_path, style={'width': '50px', 'height': '50px'}), style={'textAlign': 'center'}),
            html.Td(row['name']),
            html.Td(f"{calories * units:.1f}" if calories != 'N/A' else 'N/A'),
            html.Td(f"{carbohydrates * units:.1f} g" if carbohydrates != 'N/A' else 'N/A'),
            html.Td(f"{fat * units:.1f} g" if fat != 'N/A' else 'N/A'),
            html.Td(f"{protein * units:.1f} g" if protein != 'N/A' else 'N/A'),
        ]))

    table_body = html.Tbody(table_body_rows)

    # Combine header and body to create the table
    scrollable_table_container = html.Div(
        dbc.Table([table_header, table_body], bordered=False, hover=True, responsive=True, className="mt-4"),
                    style={
            'maxHeight': '400px',  # Adjust based on your needs
            'overflowY': 'scroll',
            'width': '100%',
            'position': 'relative'
        }
    )
    return scrollable_table_container







def prepare_logbook_panel_contents(footer):
    panel_contents = html.Div([
        html.Button('←', id='prev-day-button', 
                    style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
        dcc.DatePickerSingle(
            id='selected-date',
            date=datetime.today().date(),
            style={'display': 'inline-block'}
        ),
        html.Button('→', id='next-day-button', 
                    style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
        html.Div([dbc.Button('Show Entries', id='refresh-entries-button', color="primary", className="mb-3")
        ], style={'text-align': 'center', 'padding-top': '24px'}),
        html.Div(id='daily-feed-table-container'),  # Placeholder for dynamic content
        footer,
        
        # for testing
        html.Div(id='dummy-output', style={'display': 'none'})  # Dummy output

    ], style={'textAlign': 'center', 'padding': '10px'})
    return panel_contents



def create_logbook_panel():

    panel_style_initial = {
    "position": "fixed",
    "bottom": "-45%",  # Start with the panel mostly off-screen, adjust based on your UI
    "left": 0,
    "right": 0,
    "height": "50%",  # Panel fills half the screen height
    "background": "#fff",
    "transition": "bottom 0.5s ease-out",  # Smooth transition for sliding
    "box-shadow": "0 -2px 5px rgba(0,0,0,0.3)",
    "zIndex": "1029",
}




    button = html.Button(
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
        )



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

    
    return dbc.Container([
    button,
    html.Div(
        id="settings-panel",
        children=prepare_logbook_panel_contents(footer),
        style=panel_style_initial
    )
], style={"position": "relative", "padding": "2rem"})



# Callbacks related to the logbook panel
def register_callbacks_logbook(app):


    @app.callback(
        Output('selected-date', 'date'),
        [
            Input('prev-day-button', 'n_clicks'),
            Input('next-day-button', 'n_clicks'),
            Input('selected-date', 'date'),
        ],
        [State('selected-date', 'date')]
    )
    def change_date(prev_clicks, next_clicks, selected_date, current_date):
            ctx = dash.callback_context

            # Check which button was clicked
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            # Calculate the new date
            date = datetime.strptime(current_date, '%Y-%m-%d').date()
            if button_id == 'prev-day-button':
                new_date = date - timedelta(days=1)
            elif button_id == 'next-day-button':
                new_date = date + timedelta(days=1)
            else:
                raise dash.exceptions.PreventUpdate

            return new_date.strftime('%Y-%m-%d')

            

    # Assuming the rest of your callback setup is correctly defined

        
    @app.callback(
        Output('daily-feed-table-container', 'children'),
        [Input({'type': 'unit-increase', 'index': ALL}, 'n_clicks'),
        Input({'type': 'unit-decrease', 'index': ALL}, 'n_clicks'),
        Input('selected-date', 'date'),
        Input('refresh-entries-button', 'n_clicks')],
        [State('selected-date', 'date')]
    )
    def update_feed_and_units(inc_clicks, dec_clicks, selected_date_input, refresh_clicks, state_selected_date):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id']
        action, prop_id = triggered_id.split('.')

        df = pd.read_csv('data/nutrition_entries.csv')  # Adjust path as necessary

        # Handling button clicks for unit increase/decrease
        if action.startswith('{'):
            try:
                button_info = json.loads(action)
                button_type = button_info['type']
                button_index = int(button_info['index'])

                # Find the row in the DataFrame to update
                if 'unit-increase' in button_type:
                    df.at[button_index, 'units'] += 1
                elif 'unit-decrease' in button_type:
                    df.at[button_index, 'units'] = max(1, df.at[button_index, 'units'] - 1)

                # Save the updated DataFrame
                df.to_csv('data/nutrition_entries.csv', index=False)

                print(df[['calories','protein','units']])
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                raise PreventUpdate
        else:
            # Handling non-button inputs like 'selected-date' and 'refresh-entries-button'
            selected_date = datetime.strptime(selected_date_input or state_selected_date, '%Y-%m-%d')
        
        # Regardless of the input, regenerate and return the updated table
        selected_date = datetime.strptime(selected_date_input or state_selected_date, '%Y-%m-%d')
        return create_daily_feed(df, '/assets/images', selected_date)
