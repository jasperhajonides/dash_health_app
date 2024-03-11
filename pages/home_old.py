import sys
import numpy as np
import tempfile
import os
import base64
import io


import pandas as pd
import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc

import json
from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate

# Replace '/path/to/your/folder' with the actual path of your folder
# folder_path = '/Users/jasperhajonides/Documents/Projects/datascience/fitness_insights'

# # Add the folder to sys.path
# if folder_path not in sys.path:
#     sys.path.append(folder_path)

    
from functions.fit_import import LoadFitFiles



# # Mock dataframe (replace with your actual dataframe)
# df = pd.DataFrame({
#     'Date': pd.date_range(start='2023-01-01', periods=7, freq='D'),
#     'Heart Rate': [72, 75, 71, 73, 74, 76, 72],
#     'Steps': [10000, 11000, 10500, 9500, 12000, 11500, 10000],
#     'Calories Burned': [2200, 2300, 2100, 2250, 2350, 2400, 2220],
#     'Sleep Hours': [7, 6.5, 8, 7.5, 7, 6, 7.5]
# })

# # Calculate averages for tiles
# avg_heart_rate = df['Heart Rate'].mean()
# avg_steps = df['Steps'].mean()
# avg_calories_burned = df['Calories Burned'].mean()
# avg_sleep_hours = df['Sleep Hours'].mean()

# # Create a Plotly time series plot
# fig = px.line(df, x='Date', y='Heart Rate', title='Heart Rate Over Time')



file_upload_area = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


layout = html.Div([
    html.H1("Home", className="text-center"),
    file_upload_area,
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Average Heart Rate", className="card-title"),
                html.P(id="avg-heart-rate", children="Loading...")
            ])
        ])),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Average Steps", className="card-title"),
                html.P(id="avg-steps", children="Loading...")
            ])
        ])),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Average Calories Burned", className="card-title"),
                html.P(id="avg-calories-burned", children="Loading...")
            ])
        ])),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Average Sleep Hours", className="card-title"),
                html.P(id="avg-sleep-hours", children="Loading...")
            ])
        ])),
    ]),
    html.H3("These are the stats of the week", className="text-center my-3"),
    dcc.Graph(id="average-data-plot")  # Update this as well if needed
])


def register_callbacks(app):


    @app.callback(
        Output('session-avg-fit-files', 'data'),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def load_in_fit_files(list_of_contents, list_of_names):
        if list_of_contents is None:
            raise PreventUpdate
        # Temporary directory to save uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            list_fit_files = []
            for content, name in zip(list_of_contents, list_of_names):
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                
                # Save each file temporarily
                file_path = os.path.join(temp_dir, name)
                with open(file_path, 'wb') as f:
                    f.write(decoded)
                list_fit_files.append(file_path)

            # Process the files using LoadFitFiles
            lff = LoadFitFiles(directory=temp_dir, list_fit_files=list_fit_files)
            df_all_fits = lff.get_fit_data()
            df_averages = df_all_fits.loc[df_all_fits.trigger == 'activity_end'].dropna(axis=1,how='all') 

            # Convert DataFrame to JSON for storage in dcc.Store
            return df_averages.to_json(date_format='iso', orient='split')


    # update figure:
    @app.callback(
        Output('average-data-plot', 'figure'),
        [Input('session-avg-fit-files', 'data')]
    )
    def update_graph(json_data):
        if json_data is None:
            # Return an empty figure if no data is available
            return px.line()

        # Convert JSON data back to DataFrame
        df_averages = pd.read_json(json_data, orient='split')

        df = df_averages[['sport','start_time','total_timer_time']]

        # Convert the start_time column to datetime
        df['start_time'] = pd.to_datetime(df['start_time'])

        # Convert the total_timer_time from seconds to minutes
        df.loc[:,'total_timer_time'] = df['total_timer_time'] / 60

        # Set the date as the index and drop the time component
        df.set_index('start_time', inplace=True)
        df.index = df.index.date

        # Reshape the dataframe to get total time per sport per day
        df_reshaped = df.pivot_table(values='total_timer_time', index=df.index, columns='sport', aggfunc=np.sum)

        # Reindex to include all dates from the earliest to the last (plus 1 week)
        new_index = pd.date_range(start=df_reshaped.index.min(), end=df_reshaped.index.max() + pd.DateOffset(weeks=1))
        df_reshaped = df_reshaped.reindex(new_index, fill_value=0)

        # Reset index to make date a column again for plotting
        df_reshaped.reset_index(inplace=True)
        df_reshaped.rename(columns={'index': 'date'}, inplace=True)

        # Melt the dataframe to prepare it for scatter plot
        df_melted = df_reshaped.melt(id_vars='date', var_name='sport', value_name='total_time')

        # Filter out rows with total_time equal to 0
        df_melted = df_melted[df_melted['total_time'] != 0]
        df_melted['total_time'] = df_melted['total_time'].fillna(0)


        # Creating the scatter plot
        fig = px.scatter(df_melted, x="date", y="sport", color="sport", size="total_time", color_discrete_sequence=px.colors.qualitative.Plotly)

        # Adding customizations
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Sport",
            xaxis=dict(
                tickmode='linear',
                tick0='2021-01-01',  # Replace with the first date of your dataset
                dtick=86400000.0 * 7  # One tick per week
            )
        )

        return fig
    

    # update the boxes
    @app.callback(
        [Output("avg-heart-rate", "children"),
         Output("avg-steps", "children"),
         Output("avg-calories-burned", "children"),
         Output("avg-sleep-hours", "children")],
        [Input("session-avg-fit-files", "data")]
    )
    def update_averages(json_data):
        if json_data is None:
            return ["N/A", "N/A", "N/A", "N/A"]

        df_averages = pd.read_json(json_data, orient='split')

        # Calculate averages, ensure these columns exist in your df_averages
        avg_heart_rate = df_averages['avg_heart_rate'].mean() if 'avg_heart_rate' in df_averages else "N/A"
        avg_distance = df_averages['total_distance'].mean() if 'Steps' in df_averages else "N/A"
        avg_calories_burned = df_averages['total_calories'].mean() if 'total_calories' in df_averages else "N/A"
        avg_speed = df_averages['avg_speed'].mean() if 'avg_speed' in df_averages else "N/A"

        # Format the return values as strings
        return [f"{avg_heart_rate:.2f} bpm" if avg_heart_rate != "N/A" else "N/A",
                f"{avg_distance:.0f}" if avg_distance != "N/A" else "N/A",
                f"{avg_calories_burned:.0f}" if avg_calories_burned != "N/A" else "N/A",
                f"{avg_speed:.1f} m/s" if avg_speed != "N/A" else "N/A"]