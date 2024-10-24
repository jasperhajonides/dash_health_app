# navigation.py

import dash_bootstrap_components as dbc
from dash import html, Input, Output, State
import datetime
import dash

def create_navbar():
    navbar = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        html.I(className="fa fa-chevron-left"),
                        id="date-prev-button",
                        color="primary",
                        class_name="me-2",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        id="selected-date-display",
                        className="navbar-date-display",
                        style={"color": "black", "fontSize": "18px", "fontWeight": "bold"},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        html.I(className="fa fa-chevron-right"),
                        id="date-next-button",
                        color="primary",
                        class_name="ms-2",
                    ),
                    width="auto",
                ),
                dbc.Col(dbc.NavbarBrand("Nutrition Monitoring v1.1", class_name="ms-2",style={"fontSize": "18px"})),
                # dbc.Col(
                #     dbc.Button(
                #         html.I(className="fa fa-bars"),
                #         id="navbar-toggle",
                #         color="primary",
                #         class_name="me-2",
                #     ),
                #     width="auto",
                # ),
            ], align="center", class_name="g-0"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Home", href="/app")),
                    dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
                    dbc.NavItem(dbc.NavLink("Logout", href="/")),
                ], class_name="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ]),
        color="light",
        dark=False,
        expand="md",
    )
    return navbar


def register_navbar_callbacks(app):

    @app.callback(
        Output('selected-date-display', 'children'),
        Input('selected-date-store', 'data')
    )
    def update_date_display(selected_date):
        return datetime.datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')

    @app.callback(
        Output('selected-date-store', 'data'),
        Input('date-prev-button', 'n_clicks'),
        Input('date-next-button', 'n_clicks'),
        State('selected-date-store', 'data'),
        prevent_initial_call=True
    )
    def change_selected_date(prev_clicks, next_clicks, current_date_str):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        current_date = datetime.datetime.strptime(current_date_str, '%Y-%m-%d').date()

        if button_id == 'date-prev-button':
            new_date = current_date - datetime.timedelta(days=1)
        elif button_id == 'date-next-button':
            new_date = current_date + datetime.timedelta(days=1)
        else:
            raise dash.exceptions.PreventUpdate

        return new_date.strftime('%Y-%m-%d')

