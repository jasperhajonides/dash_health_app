from dash import html, dcc
import os
from datetime import datetime
import pandas as pd

from functions.nutrition_processing import scale_row

def create_daily_feed(df, images_folder, selected_date):
    # Convert string date back to datetime object
    # selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Filter rows by the selected date
    df_filtered = df[df['date'] == selected_date.strftime('%Y-%m-%d')]

    # Sort by meal_type with a custom order
    meal_order = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Other']

    df_filtered['meal_type'] = pd.Categorical(df_filtered['meal_type'], categories=meal_order, ordered=True)
    df_filtered = df_filtered.sort_values('meal_type')

    entry_boxes = []
    current_meal_type = None
    for index, row in df_filtered.iterrows():
        image_filename = row.get('file_name', 'default_file_name.png')
        image_path = os.path.join(images_folder, image_filename)

        # update with the amount of units indicated
        row = scale_row(row)

        if row['meal_type'] != current_meal_type:
                # Meal type header
                meal_type_header = html.Div(
                    [html.H3(row['meal_type'], style={'color': 'white', 'padding': '10px', 'background-color': 'darkblue', 'margin': '10px 0', 'textAlign': 'center'})],
                    style={'width': '100%'}
                )
                entry_boxes.append(meal_type_header)
                current_meal_type = row['meal_type']

        # Unit Counter Part
            # Unit Counter Part
        unit_counter = html.Div([
            html.Button('+', id={'type': 'unit-increase', 'index': index}, 
                        style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                            'background-color': 'lightblue', 'border': 'none', 'box-shadow': '0 2px 4px rgba(0,0,0,0.2)',
                            'margin-bottom': '5px'}),
            html.Div(str(row.get('units', 1)), style={'text-align': 'center'}),
            html.Button('-', id={'type': 'unit-decrease', 'index': index},
                        style={'width': '30px', 'height': '30px', 'border-radius': '15px', 
                            'background-color': 'lightblue', 'border': 'none', 'box-shadow': '0 2px 4px rgba(0,0,0,0.2)',
                            'margin-top': '5px'})
        ], style={'width': '10%', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})

        # Macros and Additional Nutritional Info Part
        nutritional_info = html.Div([
            html.H4(row.get('name', 'Item Name'), style={'fontSize': '28px'}),  # Title from row['name']
            
            # Serving size and Calories row
            
            # Serving size and Calories row
            html.Div([
                html.Span('🍽️', style={'fontSize': '20px'}),  # Placeholder icon for serving size
                html.Span(f"{row.get('weight', 'N/A')} g", style={'marginLeft': '5px', 'marginRight': '20px'}),
                html.Span('🔥', style={'fontSize': '20px'}),  # Placeholder icon for calories
                html.Span(f"{row.get('calories', 'N/A')} kcal", style={'marginLeft': '5px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

            
            # Two-column layout for macros and additional info
            html.Div([
                # Column 1: Macros
                html.Div([
                    html.Ul([
                        html.Li(f"Fat: {row.get('fat', 'N/A')} g"),
                        html.Li(f"Carbohydrates: {row.get('carbs', 'N/A')} g"),
                        html.Li(f"Protein: {row.get('protein', 'N/A')} g"),
                    ], style={'listStyleType': 'none', 'paddingLeft': '0'}),
                ], style={'width': '50%', 'display': 'inline-block'}),

                # Column 2: Additional Info
                html.Div([
                    html.Ul([
                        html.Li(f"Fiber: {row.get('fiber', 'N/A')} g"),
                        html.Li(f"Sugar: {row.get('sugar', 'N/A')} g"),
                        html.Li(f"Unsaturated Fat: {row.get('unsaturated fat', 'N/A')} g"),
                        html.Li(f"Saturated Fat: {row.get('saturated fat', 'N/A')} g"),
                        html.Li(f"Cholesterol: {row.get('cholesterol', 'N/A')} mg"),
                    ], style={'listStyleType': 'none', 'paddingLeft': '0'}),
                ], style={'width': '50%', 'display': 'inline-block'}),
            ], style={'display': 'flex'}),

        ], style={'width': '65%', 'display': 'inline-block'})

            # Delete Button Layout
        delete_button = html.Div([
            html.Button('×', id={'type': 'delete-button', 'index': index},  # Using the multiply symbol
                        style={
                            'width': '30px', 
                            'height': '30px', 
                            'lineHeight': '30px',  # Adjusted for vertical centering
                            'padding': '0',  # Remove padding to fit symbol within the button
                            'border': '1px solid darkgrey', 
                            'background-color': 'white', 
                            'color': 'darkgrey', 
                            'font-weight': 'bold', 
                            'font-size': '20px',  # Font size for the symbol
                            'text-align': 'center',
                            'cursor': 'pointer',
                            'position': 'absolute', 
                            'top': '10px',  # Positioning the button within the box
                            'right': '10px'
                        })
        ])

        box = html.Div([
            # Unit Counter Part
            unit_counter,
            
            # Image Part
            html.Div([
                html.Img(src=image_path, style={'width': '192px', 'height': '192px'})
            ], style={'width': '25%', 'display': 'inline-block'}),

            # Data Part
            nutritional_info,

            # Delete Button
            delete_button,
            ], style={'display': 'flex', 'border': '1px solid black', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px', 'position': 'relative', 'margin': '10px 0'})
        entry_boxes.append(box)


    # Combine the title, date display, and entry boxes into a single layout
    daily_feed_layout = html.Div([
         html.Div(entry_boxes)
    ])

    return daily_feed_layout