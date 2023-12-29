from dash import html
import dash_bootstrap_components as dbc

# Example user information (replace with actual user data)
user_info = {
    "Name": "John Doe",
    "Age": "30",
    "Location": "New York",
    "Interests": "Running, Cycling, Swimming",
    "Member Since": "2023-01-01"
}

# Function to create a card for each user info
def create_info_card(title, content):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(content, className="card-text"),
            ]
        )
    )
    return card

# Layout for the profile page
layout = html.Div(
    [
        html.H2("User Profile", className="text-center my-3"),
        dbc.Row(
            [
                dbc.Col(create_info_card(title, user_info[title]), width=4) 
                for title in user_info
            ],
            justify="around",  # Adjust the positioning of the columns
        )
    ]
)
