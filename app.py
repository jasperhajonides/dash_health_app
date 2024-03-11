import os
from dash import Dash, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dcc, no_update


from pages.nutrition import nutrition_page, register_callbacks_nutrition
from pages.all_activities import all_activities_page, register_callbacks_all_activities
from pages.nutrition_page_parts.daily_logbooks import register_callbacks_logbook
# Import sidebar and pages
from pages import (
    sidebar, 
    single_activity,
    profile,
    ) 

from data.user_data import UserData

user_data_instance = UserData(user_id=1)  # Assuming a fixed user ID for demonstration


app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    dcc.Store(id='selected_sport'),  # Store component
    dcc.Store(id='selected-row-data', storage_type='session'),
    dcc.Store(id='activity-data', storage_type='session'),  # Use session storage
    dcc.Store(id='stored-image', storage_type='session'),
    dcc.Store(id='nutritional-json-from-image', storage_type='session'),
    # dcc.Store(id='all-fit-files', storage_type='session'),  # Store for the loaded data 
    dcc.Store(id='session-avg-fit-files', storage_type='session'),  # Store for the loaded data 
    dcc.Store(id='update-trigger', data={'timestamp': None}), # nutrition finished openai api update

    dcc.Store(id='carousel-index-store', data={'index': 0}, storage_type='session'), # carousel index
    dcc.Store(id='selected-food-item-store', storage_type='session'), # selected row ai-toggle off
    dcc.Store(id='item-submission-state', data={'submitted': False}), # whether we pressed item submission or not in the nutrition app


    dbc.Row(
        [
            dbc.Col(sidebar.create_top_navbar(), width=12),  # Replace sidebar with top navbar
            dbc.Col(id="page-content", style={"marginLeft": "0%", "marginRight": "0%", "padding": "1px"}),
        ]
    ),
    dcc.Location(id="url", refresh=False)
])

# Register callbacks from sidebar
# sidebar.register_callbacks(app)
register_callbacks_all_activities(app)
single_activity.register_callbacks(app)
register_callbacks_nutrition(app)
register_callbacks_logbook(app)
profile.callback_functions_profile(app, user_data_instance)



# Callback for updating page content

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/all-activities':
        return all_activities_page()
    elif pathname == '/profile':
        return profile.profile_layout(user_data_instance)
    elif pathname == '/information':
        return no_update()
    elif pathname == '/single_activity':
        return single_activity.layout  # No need to pass row_data here
    elif pathname == '/nutrition':
        return nutrition_page()
    else:
        return html.Div([
                    html.Iframe(src="/assets/index.html", style={"width": "100%", "height": "100vh", "border": "none"})
                ])
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
