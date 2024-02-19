import dash_bootstrap_components as dbc
from dash import html, dcc

def create_sidebar():
    sidebar = dbc.Col(
        [
# Use a div to horizontally align the logo and the title
           html.Div(
                [
                    html.Img(src="./assets/logo_v1.png", height="50px", className="mr-2"),  # Logo
                    # Apply the 'gradient-text' class to the H2 element
                    html.H2("Vitalics.ai", className="gradient-text display-4", style={'fontSize': '2.8rem'}),  # Smaller font size
                ],
                style={"display": "flex", "alignItems": "center"}
            ),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact", className="sidebar-link"),
                    dbc.NavLink("All Activities", href="/all-activities", active="exact", className="sidebar-link"),
                    dbc.DropdownMenu(
                        label="Activities",
                        children=[
                            dbc.DropdownMenuItem("Swimming", id="swimming"),
                            dbc.DropdownMenuItem("Cycling", id="cycling"),
                            dbc.DropdownMenuItem("Running", id="running"),
                            dbc.DropdownMenuItem("Gym", id="gym"),
                        ],
                        nav=True,
                        in_navbar=True,
                        className="sidebar-link"
                    ),
                    dbc.NavLink("Profile", href="/profile", active="exact", className="sidebar-link"),
                    dbc.NavLink("Nutrition", href="/nutrition", active="exact", className="sidebar-link"),
                    dbc.NavLink("Information", href="/information", active="exact", className="sidebar-link"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={"width": "20%", "position": "fixed", "left": 0, "top": 0, "bottom": 0, "padding": "2rem 1rem"},
        className="bg-light",
    )
    return sidebar




def register_callbacks(app):
    from dash.dependencies import Input, Output

    @app.callback(
        Output('selected_sport', 'data'),
        [Input('swimming', 'n_clicks'),
         Input('cycling', 'n_clicks'),
         Input('running', 'n_clicks'),
         Input('gym', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_selected_sport(swim, cycle, run, gym):
        ctx = dash.callback_context

        if not ctx.triggered:
            return None
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        sports = {
            'swimming': 'Swimming',
            'cycling': 'Cycling',
            'running': 'Running',
            'gym': 'Gym'
        }

        return sports.get(button_id, None)