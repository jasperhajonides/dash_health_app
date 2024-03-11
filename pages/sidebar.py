from dash import html, dcc
import dash_bootstrap_components as dbc

def create_top_navbar():
    navbar_layout = dbc.Navbar(
        [
            # Logo and brand on the left
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="./assets/logo_v1.png", height="50px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("Vitalics.ai", className="ml-2"), width="auto"),
                    ],
                    align="center",
                    # no_gutters=True,
                ),
                href="/",
            ),
            # Navigation items on the right
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("All Activities", href="/all-activities")),
                    dbc.NavItem(dbc.NavLink("Activities", href="/activities")),
                    dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
                    dbc.NavItem(dbc.NavLink("Nutrition", href="/nutrition")),
                    dbc.NavItem(dbc.NavLink("Information", href="/information")),
                ],
                className="ml-auto",  # This will push the nav to the right side of the navbar
                navbar=True,
            ),
            # 'Explore places' button
            dbc.Button("Explore places", color="primary", className="ml-2", href="#main-section"),
        ],
        className="landing-page-navbar",  # Use your custom CSS class
        color="light",
        dark=False,
        sticky="top",
    )
    return navbar_layout
