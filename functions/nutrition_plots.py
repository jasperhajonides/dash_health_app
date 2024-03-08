import pandas as pd
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
from dash import html

from datetime import datetime, timedelta, time
import dash_daq as daq

from functions.nutrition_df_helper_functions import load_and_filter_df

def create_nutrient_pie_chart():
    try:
        # Get the current script directory (functions/nutrition_plots.py)
        current_script_dir = os.path.dirname(__file__)

        # Navigate up one level to the root directory
        root_dir = os.path.dirname(current_script_dir)

        # Construct the path to the CSV file in the data folder
        csv_path = os.path.join(root_dir, 'data', 'nutrition_entries.csv')
        
        df = pd.read_csv(csv_path)

        # Assuming 'carbohydrates', 'protein', 'fat' columns are numeric
        avg_nutrients = df[['carbohydrates', 'protein', 'fat']].mean()
        fig = px.pie(avg_nutrients, values=avg_nutrients.values, names=avg_nutrients.index, title='Average Nutritional Composition')
        return fig
    except Exception as e:
        print(f"Error reading CSV or creating chart: {e}")
        return px.pie()  # Return an empty pie chart in case of error





def time_to_seconds_since_midnight(time_val):
    return (time_val.hour * 3600) + (time_val.minute * 60) + time_val.second


def create_calories_line_plot():


    try:
        # Get the current script directory (functions/nutrition_plots.py)
        current_script_dir = os.path.dirname(__file__)

        # Navigate up one level to the root directory
        root_dir = os.path.dirname(current_script_dir)

        # Construct the path to the CSV file in the data folder
        csv_path = os.path.join(root_dir, 'data', 'nutrition_entries.csv')
        
        df = pd.read_csv(csv_path)
        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['time_seconds'] = df['time'].apply(time_to_seconds_since_midnight)

        fig = go.Figure()
        max_cumulative_calories = 0

        for date in df['date'].unique():
            daily_data = df[df['date'] == date].copy()
            daily_data_sorted = daily_data.sort_values('time_seconds')

            # Start the day with a zero calorie count at midnight
            start_of_day = pd.DataFrame({'date': [date], 'time_seconds': [0], 'calories': [0]})
            daily_data_sorted = pd.concat([start_of_day, daily_data_sorted])

            daily_data_sorted['cumulative_calories'] = daily_data_sorted['calories'].cumsum()

            if date == datetime.now().date():
                current_time_seconds = time_to_seconds_since_midnight(datetime.now().time())
                daily_data_sorted = daily_data_sorted[daily_data_sorted['time_seconds'] <= current_time_seconds]

            line_width = 3 if date == datetime.now().date() else 1
            fig.add_trace(go.Scatter(x=daily_data_sorted['time_seconds'], y=daily_data_sorted['cumulative_calories'], 
                                     mode='lines', name=str(date), line=dict(width=line_width), line_shape='hv'))

            max_cumulative_calories = max(max_cumulative_calories, daily_data_sorted['cumulative_calories'].max())

        y_axis_range = [0, max(max_cumulative_calories + 100, 3600)]
        x_axis_ticks = [time_to_seconds_since_midnight(time(hour=h)) for h in [6, 12, 18]]
        x_axis_ticks.append(time_to_seconds_since_midnight((datetime.now() + timedelta(days=1)).time()))

        fig.update_layout(title='Cumulative Calories by Time of Day', 
                          xaxis_title='Time', yaxis_title='Cumulative Calories',
                              plot_bgcolor='white',
                          xaxis=dict(tickvals=x_axis_ticks, ticktext=['06:00', '12:00', '18:00', '00:00']),
                          yaxis=dict(range=y_axis_range))
        return fig
    except Exception as e:
        print(f"Error processing data or creating line plot: {e}")
        return go.Figure()  # Return an empty line plot in case of error
    



def calculate_todays_nutrition(df):
    try:

         # Get the current script directory (functions/nutrition_plots.py)
        current_script_dir = os.path.dirname(__file__)
        root_dir = os.path.dirname(current_script_dir)
        csv_path = os.path.join(root_dir, 'data', 'nutrition_entries.csv')

        # df = pd.read_csv(csv_path)
        # df['date'] = pd.to_datetime(df['date'])
        # today = datetime.now().date()

        # Filter for today's entries
        # df_today = df[df['date'].dt.date == today]

        # Calculate the sums
        protein_today = df['protein'].sum()
        fat_today = df['fat'].sum()
        calories_today = df['calories'].sum()
        carbs_today = df['carbohydrates'].sum()
        sugar_today = df['sugar'].sum()

        return protein_today, fat_today, calories_today, carbs_today, sugar_today
    except Exception as e:
        print(f"Error calculating today's nutrition: {e}")
        # Return zeros if there's an error
        return 0, 0, 0, 0, 0
    


import base64
from dash import html

import base64
from dash import html

import base64
from dash import html

def create_circular_progress(value, target, unit, description, color, layout_direction='below', radius=45, fontsize_text=16, fontsize_num=36):
    value = round(value)  # Round the value to an integer
    percentage = min(value / target, 1)  # Ensure percentage doesn't exceed 100%
    circumference = 2 * 3.14 * radius  # Circumference of the circle
    stroke_length = percentage * circumference

    # The dash array creates the stroke length
    stroke_dasharray = f"{stroke_length} {circumference}"

    # Offset to start the stroke from the top of the circle
    stroke_dashoffset = 0 #-circumference / 4

    svg_circle = f'''
    <svg width="{2*radius+10}" height="{2*radius+10}" viewBox="0 0 {2*radius+10} {2*radius+10}" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{radius+5}" cy="{radius+5}" r="{radius}" fill="transparent" stroke="#ddd" stroke-width="4"></circle>
        <circle cx="{radius+5}" cy="{radius+5}" r="{radius}" fill="transparent" stroke="{color}" stroke-width="7"
                stroke-dasharray="{stroke_dasharray}" stroke-dashoffset="{stroke_dashoffset}"
                style="transform: rotate(-90deg); transform-origin: center;"></circle>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
              style="fill: black; font-size: {fontsize_num}px; font-family: Arial;" transform="translate({radius+5}, ${radius+10})">{value}</text>
    </svg>
    '''

    encoded_svg = f"data:image/svg+xml;base64,{base64.b64encode(svg_circle.encode()).decode()}"

    img_style = {"width": f"{2*radius+10}px", "height": f"{2*radius+10}px"}

    text_div_style = {'fontSize': f'{fontsize_text}px', 'textAlign': 'center', 'margin': '0'}

    # Adjust styles based on layout direction
    if layout_direction == 'below':
        container_style = {"display": "inline-flex", "flexDirection": "column", "alignItems": "center", "padding": "0"}
        text_div_style.update({'marginTop': '5px'})  # Reduce space between circle and text
    elif layout_direction == 'right':
        container_style = {"display": "flex", "alignItems": "center", "padding": "0"}
        img_style.update({'marginRight': '10px'})  # Reduce space between circle and text

    return html.Div([
        html.Img(src=encoded_svg, style=img_style),
        html.Div(f"{unit} {description}", style=text_div_style)
    ], style=container_style)



def create_nutrition_display(selected_date_input):

    df = load_and_filter_df(selected_date_input)

    protein, fat, calories, carbs, sugar = calculate_todays_nutrition(df)

    nutrition_values = [
        create_circular_progress(protein, 140, "g", "Protein", "#ff6384"),
        create_circular_progress(fat, 100, "g", "Fat", "#36a2eb"),
        create_circular_progress(calories, 3500, "", "Calories", "#ffcd56", radius=60),
        create_circular_progress(carbs, 200, "g", "Carbohydrates", "#4bc0c0"),
        create_circular_progress(sugar, 70, "g", "Sugar", "#9966ff")
    ]

    container = html.Div(nutrition_values, style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'})
    return container
