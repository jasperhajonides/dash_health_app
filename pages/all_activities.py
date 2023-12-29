import dash
import sys
from dash import html, dcc, dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import ALL


# Define the path to be added
path_to_add = '/Users/jasperhajonides/Documents/Projects/website/dash_health_app/functions'

# Add the path to sys.path if it's not already there
if path_to_add not in sys.path:
    sys.path.append(path_to_add)
    
# from llama_cpp_functions import llama_cpp_Q2



# Assuming this is your DataFrame
df = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=7, freq='D'),
    'Heart Rate': [72, 75, 71, 73, 74, 76, 72],
    'Steps': [10000, 11000, 10500, 9500, 12000, 11500, 10000],
    'Calories Burned': [2200, 2300, 2100, 2250, 2350, 2400, 2220],
    'Sleep Hours': [7, 6.5, 8, 7.5, 7, 6, 7.5],
    'Sport':['run','swim','swim','cycle','run','swim','swim'],
})


def create_sport_buttons(sports):
    return [dbc.Button(sport, id={'type': 'sport-button', 'index': sport}, 
                       color="primary", outline=True, className="me-1") for sport in sports]


def all_activities_page():
    layout = html.Div([
        html.H2("All Activities", className="mb-3"),

       # Outer box with gradient background
        # Outer box with gradient background
        html.Div([
            # Loading component wrapping the inner box
            dcc.Loading(
                id="loading-1",
                type="default",  # You can choose the spinner type
                children=html.Div(id="generated-text", style={
                    'padding': '10px',
                    'background-color': 'rgba(211, 211, 211, 0.33)',
                    'height': '200px',
                    'overflow': 'auto',
                    'border-radius': '10px',
                    'font-weight': 'bold',
                    'color': 'black',
                    'width': '100%'
                })
            ),
        ], style={
            'width': '75%',
            'margin': '0 auto',
            'background-image': 'linear-gradient(to right, darkblue, lightblue)',
            'padding': '10px',
            'border-radius': '10px',  # Rounded corners
            'opacity': '0.75',  # Alpha 0.75
            'position': 'relative'  # Needed for correct spinner positioning
        }),

        # Centered "Generate" button with gradient
        html.Div([
            dbc.Button("Generate", id="generate-button", className="my-3", 
                       style={
                           'background-image': 'linear-gradient(to right, lightblue, darkblue)',
                           'color': 'white',
                           'border': 'none'
                       })
        ], style={'text-align': 'center'}),

        
        html.Div(
            [dbc.Button("Select All", id="select-all-button", color="secondary", className="me-1")] +
            create_sport_buttons(df['Sport'].unique()),
            className="d-flex flex-wrap mb-3"
        ),
        dash_table.DataTable(
            id='activities-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records')
        ),
        dcc.Location(id='redirect', refresh=True),
        dcc.Store(id='selected-sports', data=df['Sport'].unique().tolist())

    ])
    return layout

# Callback for updating the table based on the dropdown selection
# Assuming this is in all_activities.py
def register_callbacks_all_activities(app):
    # Callback to handle sport button clicks
    @app.callback(
        Output('selected-sports', 'data'),
        [Input({'type': 'sport-button', 'index': dash.ALL}, 'n_clicks'),
         Input('select-all-button', 'n_clicks')],
        [State('selected-sports', 'data')]
    )
    def update_selected_sports(sport_clicks, select_all_clicks, selected_sports):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        print("Button clicked:", button_id)  # Debugging line

        if 'index' in button_id:
            sport = eval(button_id)['index']
            if sport in selected_sports:
                selected_sports.remove(sport)
            else:
                selected_sports.append(sport)
        elif button_id == "select-all-button":
            print('select all clicked')  # Debugging line
            if len(selected_sports) == len(df['Sport'].unique()):
                selected_sports = []
            else:
                selected_sports = df['Sport'].unique().tolist()

        print("Selected sports:", selected_sports)  # Debugging line
        return selected_sports

    # Callback to update the table based on selected sports
    @app.callback(
        Output('activities-table', 'data'),
        [Input('selected-sports', 'data')]
    )
    def update_table(selected_sports):
        print("Updating table with:", selected_sports)  # Debugging line
        filtered_df = df[df['Sport'].isin(selected_sports)]
        return filtered_df.to_dict('records')
    
    @app.callback(
        [Output({'type': 'sport-button', 'index': ALL}, 'style')],
        [Input('selected-sports', 'data')]
    )
    def update_button_styles(selected_sports):
        styles = []
        for sport in df['Sport'].unique():
            if sport in selected_sports:
                styles.append({'background-color': 'blue', 'color': 'white'})
            else:
                styles.append({'background-color': 'lightgrey', 'color': 'black'})
        return [styles]
    
    @app.callback(
        Output('select-all-button', 'style'),
        [Input('selected-sports', 'data')]
    )
    def update_select_all_button_style(selected_sports):
        if len(selected_sports) == len(df['Sport'].unique()):
            # All sports are selected, set to turquoise
            return {'background-color': 'turquoise', 'color': 'white'}
        else:
            # Not all sports are selected, set to dark grey
            return {'background-color': 'darkgrey', 'color': 'white'}


    @app.callback(
            Output('generated-text', 'children'),
            [Input('generate-button', 'n_clicks')],
            prevent_initial_call=True
        )
    def update_generated_text(n_clicks):
        if n_clicks is None:
            raise PreventUpdate


        generated_string = llama_cpp_Q2()  # Update this string as needed
        return html.P(generated_string, style={'white-space': 'pre-line'})





# redirect to the single activity page
    @app.callback(
        [Output('redirect', 'pathname'),
         Output('selected-row-data', 'data')],
        [Input('activities-table', 'active_cell')],
        prevent_initial_call=True
    )
    def on_row_click(active_cell):
        print("Active cell:", active_cell)  # Debugging line
        if active_cell is None:
            raise PreventUpdate

        row = df.iloc[active_cell['row']].to_dict()
        print("Row data:", row)  # Debugging line
        return '/single_activity', row
