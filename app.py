import sys
from dash import Dash, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dcc


from pages.nutrition import nutrition_page, register_callbacks_nutrition
from pages.all_activities import all_activities_page, register_callbacks_all_activities
# Import sidebar and pages
from pages import (
    sidebar, 
    home, 
    single_activity,
    profile,
    ) 

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])



# Register callbacks for each page
# all_activities.register_callbacks(app)
# information.register_callbacks(app)


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



    dbc.Row(
        [
            dbc.Col(sidebar.create_sidebar(), width=2, style={"position": "fixed", "left": 0, "width": "20%", "minHeight": "100vh"}),
            dbc.Col(id="page-content", style={"marginLeft": "25%","marginRight": "10%" , "padding": "20px"}), #"width": "60%"
        ]
    ),
    dcc.Location(id="url", refresh=False)
])

# Register callbacks from sidebar
sidebar.register_callbacks(app)
home.register_callbacks(app)
register_callbacks_all_activities(app)
single_activity.register_callbacks(app)
register_callbacks_nutrition(app)

# profile.register_callbacks(app)


# Callback for updating page content

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/all-activities':
        return all_activities_page()
    elif pathname == '/profile':
        return profile.layout
    elif pathname == '/information':
        return information.layout
    elif pathname == '/single_activity':
        return single_activity.layout  # No need to pass row_data here
    elif pathname == '/nutrition':
        return nutrition_page()
    else:
        return home.layout
    

# @app.callback(
#     Output('all_fit_files', 'data')
#     Input()
# )
# def load_in_fit_files():

#     lff = LoadFitFiles(directory= '/Users/jasperhajonides/Desktop/garmin_data/',list_fit_files=None ) #, list_fit_files=list_fits)#root_path + 'data/garmin_test_data/')
#     df_all_fits = lff.get_fit_data()

#     return df_all_fits

if __name__ == '__main__':
    app.run_server(debug=True)
