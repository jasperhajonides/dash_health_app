from dash import html, dcc
import dash_bootstrap_components as dbc

def create_top_navbar():
    navbar_layout =  dbc.Navbar(
                        [
                            # Logo and brand on the left
                            html.A(
                                dbc.Row(
                                    [
                                        dbc.Col(html.Img(src="./assets/logo_v1.png", height="84px"), className="my-auto"),
                                        dbc.Col(dbc.NavbarBrand("Vitalics.ai", className="ml-2"), className="my-auto"),
                                    ],
                                    align="center",
                                    className="flex-grow-0",
                                ),
                                href="/",
                            ),
                            # Right-side elements
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            # dcc.Link("Home", href="/", className="landing-page-text"),
                                            dcc.Link("All Activities", href="/all-activities", className="landing-page-text"),
                                            # dcc.Link("Activities", href="/activities", className="landing-page-text01"),
                                            dcc.Link("Profile", href="/profile", className="landing-page-text01"),
                                            dcc.Link("Nutrition", href="/nutrition", className="landing-page-text02"),
                                            dcc.Link("Information", href="/information", className="landing-page-text03"),
                                        ],
                                        className="landing-page-links-container"
                                    ),
                                    # 'Explore places' button
                                    dcc.Link(
                                        html.Button(
                                            "Explore places",
                                            className="solid-button-button"
                                        ),
                                        href="#main-section",
                                    ),
                                ],
                                className="landing-page-right-side"  # This div corresponds to 'landing-page-right-side' in your CSS
                            ),
                        ],
                        className="landing-page-navbar",  # Use your custom CSS class
                        dark=False,
                        sticky="top",
                    ),
                # ],
            #     className="landing-page-top-container",
            # ),
        # ],
    #     className="landing-page-container",
    # )
    return navbar_layout
