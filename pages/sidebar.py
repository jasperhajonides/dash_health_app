import dash_bootstrap_components as dbc
from dash import html, dcc

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_iconify as di

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_iconify as di

def create_sidebar():
    # Define a function to generate icon links with hover effects
    def icon_link(icon, href, text, id):
        return html.Div(
            [
                dcc.Link(
                    di.DashIconify(icon=icon, width=24, height=24, className="mr-2"),
                    href=href,
                ),
                dbc.Tooltip(text, target=id, placement="right"),
            ],
            className="d-flex align-items-center my-2 icon-container",
            id=id,
        )

    sidebar = dbc.Col(
        [
            html.Div(
                [
                    html.Img(src="./assets/logo_v1.png", height="50px", className="mr-2"),
                    html.H2("Vitalics.ai", className="gradient-text display-4", style={'fontSize': '2.8rem'}),
                ],
                style={"display": "flex", "alignItems": "center"}
            ),
            html.Hr(),
            dbc.Nav(
                [
                    icon_link("mdi:home", "/", "Home", "home-icon"),
                    icon_link("mdi:format-list-bulleted", "/all-activities", "All Activities", "all-activities-icon"),
                    icon_link("mdi:run", "/activities", "Activities", "activities-icon"),
                    icon_link("mdi:account-circle", "/profile", "Profile", "profile-icon"),
                    icon_link("mdi:food-apple", "/nutrition", "Nutrition", "nutrition-icon"),
                    icon_link("mdi:information-outline", "/information", "Information", "information-icon"),
                ],
                vertical=True,
                pills=True,
                className="d-flex flex-column align-items-start",
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