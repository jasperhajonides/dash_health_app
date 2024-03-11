from dash import html

# Define the layout for the home page
layout = html.Div([
    html.Iframe(src="/assets/home_page.html", style={"width": "100%", "height": "100vh", "border": "none"})
])
