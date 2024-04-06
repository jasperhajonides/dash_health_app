from dash import html, dcc, Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate

import dash
import dash_bootstrap_components as dbc
import dash_iconify as di
from datetime import datetime, timedelta
import pandas as pd
import os
import json

from pages.nutrition_page_parts.daily_overview import create_daily_feed
from functions.nutrition_plots import *
from functions.nutrition_df_helper_functions import load_and_filter_df


import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env


from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_iconify as di
import os

# custom_js = html.Script(src='/assets/datatable_logging.js')


def combined_plots_layout():
    # Create a layout that contains both the nutrient pie chart and the calories line plot side-by-side
    return html.Div([
        dcc.Graph(figure=create_nutrient_pie_chart(), style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(figure=create_calories_line_plot(), style={'width': '50%', 'display': 'inline-block'})
    ])

def get_nutrition_display_args(selected_date):
    # This function returns the arguments for create_nutrition_display based on the selected date
    # You can include logic here to determine the arguments based on the selected date
    return (selected_date,)


# List of carousel item functions
carousel_items = [
    create_nutrition_display,
    # combined_plots_layout
]






def create_daily_feed(df, images_folder, selected_date):
    """
    Generates a scrollable table container for daily nutrition entries.

    Parameters:
    - df: DataFrame containing nutrition entries.
    - images_folder: Path to the directory containing images.
    - selected_date: Selected date for which to display entries.
    """
    # Convert selected_date from string format to datetime.date object if it's not already
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    if df.empty:
        return "No entries found for this date."
    

    # Filter DataFrame for entries matching the selected date
    # df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure 'date' column is in datetime.date format
    # df_filtered = df[df['date'] == selected_date]

    # Custom sort the DataFrame by 'meal_type'
    meal_order = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Other']
    df['meal_type'] = pd.Categorical(df['meal_type'], categories=meal_order, ordered=True)
    df_sorted = df.sort_values(['meal_type', 'date'])

    # Generating table content
    table_header = html.Thead(
        html.Tr([
            # html.Th("Meal Type", style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '16px'}),
            html.Th("Quantity"),
            html.Th("Image"),
            html.Th("Name"),
            html.Th("kcal"),
            html.Th("Carbs (g)"),
            html.Th("Fat (g)"),
            html.Th("Protein (g)"),
        ])
    )

    table_body_rows = []
    current_meal_type = None
    for index, row in df_sorted.iterrows():
        # Check if the meal type has changed
        if row['meal_type'] != current_meal_type:
            # Insert a header row for the new meal type
            table_body_rows.append(html.Tr([
                html.Td(row['meal_type'], colSpan="8", style={'fontWeight': 'bold', 'fontSize': '18px', 'textAlign': 'center', 'backgroundColor': '#e9ecef'}),
            ]))
            current_meal_type = row['meal_type']

        # Insert row for the current entry
        units = row.get('units', 1)
        calories = row.get('calories', 'N/A') * units if row.get('calories', 'N/A') != 'N/A' else 'N/A'
        carbohydrates = row.get('carbs', 'N/A') * units if row.get('carbs', 'N/A') != 'N/A' else 'N/A'
        fat = row.get('fat', 'N/A') * units if row.get('fat', 'N/A') != 'N/A' else 'N/A'
        protein = row.get('protein', 'N/A') * units if row.get('protein', 'N/A') != 'N/A' else 'N/A'
        image_filename = row.get('file_name', 'default_file_name.png')
        image_path = f"{images_folder}/{image_filename}"

        table_body_rows.append(html.Tr([
            html.Td([  # Include buttons for increasing or decreasing the unit count
                html.Button('-', id={'type': 'unit-decrease', 'index': index}, 
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 
                                'box-shadow': '0 2px 4px rgba(0,0,0,0.2)', 'margin-right': '5px'}),
                html.Span(f"{units:.1f}"),  # Display units rounded to one decimal point
                html.Button('+', id={'type': 'unit-increase', 'index': index}, 
                            style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                                'background-color': 'lightblue', 'border': 'none', 
                                'box-shadow': '0 2px 4px rgba(0,0,0,0.2)', 'margin-left': '5px'}),
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
            html.Td(html.Img(src=image_path, style={'width': '50px', 'height': '50px'}), style={'textAlign': 'center'}),
            html.Td(row['name']),
            html.Td(f"{calories * units:.1f}" if calories != 'N/A' else 'N/A'),
            html.Td(f"{carbohydrates * units:.1f} g" if carbohydrates != 'N/A' else 'N/A'),
            html.Td(f"{fat * units:.1f} g" if fat != 'N/A' else 'N/A'),
            html.Td(f"{protein * units:.1f} g" if protein != 'N/A' else 'N/A'),
        ]))

    table_body = html.Tbody(table_body_rows)

    # Combine header and body to create the table
    scrollable_table_container = html.Div(
        dbc.Table([table_header, table_body], bordered=False, hover=True, responsive=True, className="mt-4"),
                    style={
            'maxHeight': '400px',  # Adjust based on your needs
            'overflowY': 'scroll',
            'width': '100%',
            'position': 'relative'
        }
    )
    return scrollable_table_container





def prepare_logbook_panel_contents(footer):

    # Assuming 'df' is your DataFrame and 'images_folder' is the path to your images directory
    # df = pd.read_csv('data/nutrition_entries.csv')  # Adjust path as necessary
    images_folder = '/assets/images'

    # Assuming 'selected_date' is obtained from dcc.DatePickerSingle or similar
    selected_date = datetime.today().date()  # Default to today, but can be any date you choose

    # Ensure selected_date is a string in 'YYYY-MM-DD' format
    selected_date_str = selected_date.strftime('%Y-%m-%d')

    # Now pass this string to load_and_filter_df
    df = load_and_filter_df(selected_date_str)

    # create daily feed for the sected day
    feed_content_for_today = create_daily_feed(df, images_folder, selected_date)

    # date for visualisation
    formatted_date_initial = datetime.today().strftime("%A, %B %d, %Y")  # Example: "Monday, January 01, 2023"

    panel_contents = html.Div([
            html.Div(),  # Empty line for spacing            
            html.Div(),  # Empty line for spacing
            html.Div([
                html.Button('←', id='prev-day-button', className="date-nav-btn", style={
                'background-color': 'white', 'border': '1px solid lightgrey', 'color': 'grey',
                'cursor': 'pointer', 'marginRight': '5px'
                }),
                html.Span(formatted_date_initial, id='formatted-date-display', style={
                    'font-weight': 'bold', 'font-size': '20px', 'margin': '0 10px'
                }),
                html.Button('→', id='next-day-button', className="date-nav-btn", style={
                'background-color': 'white', 'border': '1px solid lightgrey', 'color': 'grey',
                'cursor': 'pointer', 'marginLeft': '5px'
                }),
            ], style={
                'position': 'relative', 'padding': '20px 0'
            }),
            dcc.DatePickerSingle(
                id='selected-date',
                date=datetime.today().date(),
                style={'display': 'none'}  # Hide the actual DatePicker but keep it for functionality
            ),

            # -=---- CAROUSEL ----=-
            html.Div([
                # Left navigation button
                html.Div(
                    dbc.Button('<', id='carousel-left-btn', color='light', className='carousel-btn', 
                                style={'height': '80px', 'width': '40px'}),
                    style={'position': 'absolute', 'left': '0', 'top': '50%', 'transform': 'translateY(-50%)'}
                ),

                # Carousel content container
                html.Div(id='carousel-content', className='carousel-content', 
                            style={'height': '180px', 'overflow': 'hidden'}),

                # Right navigation button
                html.Div(
                    dbc.Button('>', id='carousel-right-btn', color='light', className='carousel-btn', 
                                style={'height': '80px', 'width': '40px'}),
                    style={'position': 'absolute', 'right': '0', 'top': '50%', 'transform': 'translateY(-50%)'}
                ),
            ], style={'position': 'relative', 'height': '180px', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '100%'}),



            html.Div(id='daily-feed-table-container', children=feed_content_for_today),  # Include the feed content directly
            footer,
        ], style={'textAlign': 'center', 'padding': '10px'})
    return panel_contents


def create_logbook_panel():
    panel_style_initial = {
        "position": "fixed",
        "bottom": "-65%",  # Adjust based on your UI
        "left": 0,
        "right": 0,
        "height": "70%",  # Panel fills a portion of the screen height
        "background": "#fff",
        "transition": "bottom 0.5s ease-out",  # Smooth transition for sliding
        "box-shadow": "0 -2px 5px rgba(0,0,0,0.3)",
        "zIndex": "1029",
        "overflow": "hidden",  # Prevent scrolling outside the scrollable container
    }

    # Toggle button to open/close the logbook panel
    button = html.Button(
        children=[
            di.DashIconify(icon="mdi:book-open-page-variant", width=30, height=30, style={"verticalAlign": "middle"}),
            " Daily Overview"
        ],
        id="toggle-settings",
        style={
            "position": "fixed",
            "bottom": "20px",
            "left": "50%",
            "transform": "translateX(-50%)",
            "transition": "bottom 0.5s ease-out",
            "zIndex": "1030",
            "background": "linear-gradient(90deg, rgba(0,77,64,1) 0%, rgba(45,105,94,1) 100%)",
            "border": "none",
            "color": "white",
            "padding": "10px 20px",
            "borderRadius": "30px",
            "cursor": "pointer",
        }
    )

    # Footer content
    footer = html.Div(
        [
            html.P(" ", style={'text-align': 'center'}),
            # Add more content here as needed
        ],
        style={
            'height': '300px',
            'background-color': 'white',
            'color': 'black',
            'text-align': 'center',
            'padding': '10px',
        }
    )

    # Content of the logbook panel
    logbook_content = prepare_logbook_panel_contents(footer)

    # Wrap the logbook content in a scrollable container
    scrollable_section = html.Div(
        id="scrollable-section",
        children=logbook_content,
        style={
            "overflowY": "auto",  # Enable vertical scrolling
            "height": "calc(100% - 60px)",  # Adjust height to allow space for fixed elements
        }
    )

    return dbc.Container([
        button,
        html.Div(
            id="settings-panel",
            children=[
                # Fixed elements (e.g., date display, navigation buttons) go here, outside the scrollable_section
                scrollable_section  # Include the scrollable section
            ],
            style=panel_style_initial
        )
    ], style={"position": "relative", "padding": "2rem"})




# Callbacks related to the logbook panel
def register_callbacks_logbook(app):

    @app.callback(
        [
            Output("settings-panel", "style"),
            Output("toggle-settings", "style")
        ],
        [Input("toggle-settings", "n_clicks")],
        [
            State("settings-panel", "style"),
            State("toggle-settings", "style")
        ],
    )
    def toggle_settings_panel(n_clicks, panel_style, button_style):
        """ Open and close the daily logging panel!"""
        if n_clicks:
            if panel_style["bottom"] == "0%":
                # Panel is open; move it to "closed" state, leaving a small part visible
                panel_style["bottom"] = "-65%"  # Adjust as needed
                button_style["bottom"] = "2.5%"  # Adjust to align with the visible part of the panel
            else:
                # Panel is "closed"; open it fully, but ensure it slides just below half the button
                panel_style["bottom"] = "0%"
                button_style["bottom"] = "67.5%"  # Adjust so the panel goes slightly under the button
            return panel_style, button_style
        return panel_style, button_style




    @app.callback(
        [Output('selected-date', 'date'),
        Output('formatted-date-display', 'children')],
        [Input('prev-day-button', 'n_clicks'),
        Input('next-day-button', 'n_clicks')],
        [State('selected-date', 'date')]
    )
    def change_date(prev_clicks, next_clicks, current_date):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        date = datetime.strptime(current_date, '%Y-%m-%d').date()
        if button_id == 'prev-day-button':
            new_date = date - timedelta(days=1)
        elif button_id == 'next-day-button':
            new_date = date + timedelta(days=1)
        else:
            raise dash.exceptions.PreventUpdate

        # Format the new date to display
        formatted_date = new_date.strftime("%A, %B %d, %Y")

        return new_date.strftime('%Y-%m-%d'), formatted_date

            

    # Assuming the rest of your callback setup is correctly defined

    @app.callback(
        Output('daily-feed-table-container', 'children'),
        [
            Input('selected-date', 'date'),
            Input({'type': 'unit-increase', 'index': ALL}, 'n_clicks'),
            Input({'type': 'unit-decrease', 'index': ALL}, 'n_clicks'),
        ],
        # No need for State if we're just reading the current value of 'selected-date'
    )
    def update_feed_and_units(selected_date_input, inc_clicks, dec_clicks):
        ctx = dash.callback_context

        df = load_and_filter_df(selected_date_input)  # Load and filter the DataFrame based on selected date
        selected_date = datetime.strptime(selected_date_input, '%Y-%m-%d')
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id']
            if "unit-increase" in trigger_id or "unit-decrease" in trigger_id:
                button_info = json.loads(trigger_id.split('.')[0])
                button_type = button_info['type']
                button_index = button_info['index']
                
                # Update units based on the button pressed
                if 'unit-increase' in button_type:
                    df.at[button_index, 'units'] += 1
                elif 'unit-decrease' in button_type:
                    df.at[button_index, 'units'] = max(1, df.at[button_index, 'units'] - 1)

                # Save the updated DataFrame
                df.to_csv('data/nutrition_entries.csv', index=False)

        # Generate and return the updated table based on the selected date
        return create_daily_feed(df, '/assets/images', selected_date)


            
    @app.callback(
        [Output('carousel-content', 'children'),
        Output('carousel-index-store', 'data')],
        [Input('carousel-left-btn', 'n_clicks'),
        Input('carousel-right-btn', 'n_clicks'),
        Input('selected-date', 'date')],
        [State('carousel-index-store', 'data')]
    )
    def update_carousel_content(left_clicks, right_clicks, selected_date, index_data):
        ctx = dash.callback_context
        if not index_data:
            index_data = {'index': 0}  # Initialize if not present
        current_index = index_data['index']

        # Determine if the date has changed or which button was clicked
        triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

        if 'selected-date.date' in triggered_id:
            # The selected date has changed, update content based on the new date
            # No need to change the index since we're updating content for the current index
            pass
        elif 'carousel-left-btn.n_clicks' in triggered_id:
            # Navigate left
            current_index = (current_index - 1) % len(carousel_items)
        elif 'carousel-right-btn.n_clicks' in triggered_id:
            # Navigate right
            current_index = (current_index + 1) % len(carousel_items)

        # Generate content for the current carousel item
        carousel_func = carousel_items[current_index]
        if carousel_func == create_nutrition_display:
            content = carousel_func(selected_date)  # Call with selected_date for functions that need it
        else:
            content = carousel_func()  # Call without arguments for functions that don't need them

        # Update the index in the store for keeping track of the current item
        updated_index_data = {'index': current_index}

        return content, updated_index_data