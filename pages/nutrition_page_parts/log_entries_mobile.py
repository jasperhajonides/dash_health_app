# log_entries_mobile.py

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px
from datetime import datetime

def create_todays_entries_layout(todays_nutritional_data):
    """
    Create a layout displaying today's food entries.

    Parameters:
    - todays_nutritional_data: List of dictionaries containing today's food entries.
    """

        # Parse created_at strings into datetime objects
    for entry in todays_nutritional_data:
        created_at_str = entry.get('created_at', '')
        if created_at_str:
            try:
                entry['created_at_datetime'] = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except ValueError:
                entry['created_at_datetime'] = datetime.min  # Default to the earliest possible time
        else:
            entry['created_at_datetime'] = datetime.min


    # Sort entries by created_at in ascending order (earliest first)
    sorted_entries = sorted(
        todays_nutritional_data,
        key=lambda x: x.get('created_at', ''),
        reverse=False  # Set to True if you want latest entries first
    )

    # Title
    section = [
        html.H4("Today's Entries", style={'margin-top': '30px', 'text-align': 'center'})
    ]

    # Styles
    entry_row_style = {
        'display': 'flex',
        'align-items': 'center',
        'padding': '10px 0',
        'border-bottom': '1px solid #ddd',
    }

    for entry in sorted_entries:
        entry_id = entry.get('id')
        name = entry.get('name', 'Unknown Item')
        description = entry.get('description', '')
        calories = entry.get('calories', 0)
        carbohydrates = entry.get('carbohydrates', 0)
        fat = entry.get('fat', 0)
        protein = entry.get('protein', 0)

        # Calculate total macronutrients
        total_macros = carbohydrates + fat + protein
        if total_macros == 0:
            total_macros = 1  # To avoid division by zero

        # Calculate percentages
        carbs_percentage = (carbohydrates / total_macros) * 100
        fat_percentage = (fat / total_macros) * 100
        protein_percentage = (protein / total_macros) * 100

        # Delete button (Leftmost cell)
        delete_button = dbc.Button(
            "✖",
            id={'type': 'delete-button', 'index': entry_id},
            color="link",
            size="sm",
            style={'margin-left': '5px', 'color': 'red'}
        )

        # Macronutrient bar
        macro_bar = dbc.Progress(
            [
                dbc.Progress(value=carbs_percentage, color='info', bar=True),
                dbc.Progress(value=fat_percentage, color='danger', bar=True),
                dbc.Progress(value=protein_percentage, color='success', bar=True),
            ],
            style={'height': '8px', 'margin-top': '5px', 'margin-bottom': '5px'},
            className="w-100"
        )

        # Middle section with name and description
        middle_section = html.Div(
            [
                html.Div(html.Span(name, style={'font-weight': 'bold'})),
                html.Div(html.Span(description, style={'font-style': 'italic', 'color': 'gray'})),
                macro_bar,
            ],
            style={'flex': '1', 'padding': '0 10px'}
        )

        # Calories (Rightmost cell)
        calories_section = html.Div(
            html.Span(f"{calories} kcal"),
            style={'flex': '0 0 auto', 'display': 'flex', 'align-items': 'center', 'margin-right': '5px'}
        )

        # Entry row
        entry_row = html.Div(
            [
                # Leftmost delete button
                html.Div(delete_button, style={'flex': '0 0 auto', 'display': 'flex', 'align-items': 'center'}),
                # Middle section
                middle_section,
                # Rightmost calories
                calories_section,
            ],
            style=entry_row_style
        )

        section.append(entry_row)

    return html.Div(section, style={'padding': '10px'})
