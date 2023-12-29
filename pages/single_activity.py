from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# Layout for single_activity page
layout = html.Div([
    dcc.Store(id='activity-data'),
    dcc.Graph(id='activity-bar-chart'),
    dcc.Location(id='current-url', refresh=False)
])

# Callback to update bar chart
def register_callbacks(app):
    @app.callback(
        Output('activity-bar-chart', 'figure'),
        [Input('activity-data', 'data')]
    )
    def update_bar_chart(data):
        if data is None:
            return {}
        df = pd.DataFrame([data])
        fig = px.bar(df, x=df.columns, y=df.values[0])
        return fig
