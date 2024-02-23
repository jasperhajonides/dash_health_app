from dash import html, dcc, Input, Output, State, callback, ALL
import dash
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd
import os
import json

# Define your panel_style_initial somewhere in this file or import it if defined elsewhere
panel_style_initial = {
    # Your style here
}

def create_logbook_panel():
    return dbc.Container([
        html.Div([
            html.Button('←', id='prev-day-button', 
                        style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
            dcc.DatePickerSingle(
                id='selected-date',
                date=datetime.today().date(),
                style={'display': 'inline-block'}
            ),
            html.Button('→', id='next-day-button', 
                        style={'display': 'inline-block', 'background-color': 'white', 'border': '1px solid darkgrey'}),
        ], style={'textAlign': 'center', 'padding': '10px'}),
        html.Div([dbc.Button('Show Entries', id='refresh-entries-button', color="primary", className="mb-3")
                ], style={'text-align': 'center', 'padding-top': '24px'}),
        html.Div(id='recent-entries-container'),
        # Include your footer here if it's part of the panel
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

    @app.callback(
        Output('recent-entries-container', 'children'),
        [
            Input('submit-nutrition-data', 'n_clicks'),
            Input('refresh-entries-button', 'n_clicks'),
            Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
            Input({'type': 'unit-increase', 'index': ALL}, 'n_clicks'),
            Input({'type': 'unit-decrease', 'index': ALL}, 'n_clicks'),
            Input('update-trigger', 'data'),
            Input('selected-date', 'date'),
            Input('add-to-csv-button', 'n_clicks')
        ],
    )
    def update_entries(submit_clicks, refresh_clicks, delete_clicks, increase_clicks, decrease_clicks, update_trigger, selected_date_str, add_clicks):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

        # Always read the CSV file when the callback is triggered
        filename = 'data/nutrition_entries.csv'
        try:
            df = pd.read_csv(filename)
            if 'units' not in df.columns:
                df['units'] = 1
            else:
                df['units'] = df['units'].fillna(1).apply(lambda x: 1 if pd.isna(x) or x <= 0 else x)
        except FileNotFoundError:
            return "No entries found."
        
        if trigger_id:
            # Handling delete, increase, and decrease actions
            if 'delete-button' in trigger_id:
                button_index = json.loads(trigger_id.split('.')[0])['index']
                df = df.drop(df.index[button_index])
            elif 'unit-increase' in trigger_id or 'unit-decrease' in trigger_id:
                button_index = json.loads(trigger_id.split('.')[0])['index']
                increment = 1 if 'unit-increase' in trigger_id else -1
                df.at[button_index, 'units'] = max(0, df.at[button_index, 'units'] + increment)

        # Save and sort dataframe for all scenarios
        df.to_csv(filename, index=False)
        df = df.sort_values(by='time', ascending=False)

        # Common operations for preparing feed layout
        script_dir = os.path.dirname(__file__)
        root_dir = os.path.dirname(script_dir)
        images_folder = os.path.join(root_dir, 'images')

        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.today().date()

        feed_layout = create_daily_feed(df, images_folder, selected_date)
        return feed_layout
