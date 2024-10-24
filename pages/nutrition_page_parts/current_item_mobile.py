# current_item_mobile.py

import dash
from dash import html, dcc, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import circlify
import random

def create_header(json_entry):
    """
    Create the header section with the item name, description, and glycemic index.
    """
    name = json_entry.get('name', 'Unknown Item')
    description = json_entry.get('description', '')
    glycemic_index = json_entry.get('glycemic_index', None)

    header_children = [
        html.H4(name, style={'font-weight': 'bold'}),
        html.P(description, style={'font-weight': 'normal', 'font-style': 'italic'}),
    ]

    if glycemic_index is not None:
        header_children.append(
            html.P(f"Glycemic Index: {glycemic_index}", style={'font-weight': 'normal', 'font-style': 'italic'})
        )

    header = html.Div(
        header_children,
        style={'text-align': 'center', 'margin-bottom': '20px'}
    )
    return header

def create_info_icon(info_id, info_text):
    """
    Create an information icon with a popover for additional information.
    """
    icon = html.Span(
        "ℹ️",
        id=info_id,
        style={'cursor': 'pointer', 'margin-left': '5px', 'font-size': '16px'}
    )
    popover = dbc.Popover(
        [
            dbc.PopoverBody(info_text)
        ],
        id=f"popover-{info_id}",
        target=info_id,
        trigger="click",
        placement="top",
    )
    return html.Span([icon, popover])

def create_macro_bar(nutrient, actual_value, recommended_value, nutrient_colors):
    """
    Create the macro nutrient progress bar with a toggle button for sub-bars.
    """
    percentage = (actual_value / recommended_value) * 100 if recommended_value else 0
    percentage = min(percentage, 100)  # Cap at 100%

    # Format the nutrient name
    nutrient_name = nutrient.capitalize()

    # Determine the unit
    unit = 'g' if nutrient != 'calories' else 'kcal'

    # Text to display on the right side
    display_text = f"{actual_value:.1f} / {recommended_value} {unit}"

    # Create the information icon
    info_icon = create_info_icon(f"info-{nutrient}", f"More information about {nutrient_name}")

    # Create the progress bar
    bar_style = {
        'height': '30px' if nutrient == 'calories' else '20px',
        'border-radius': '10px',
    }

    label_style = {
        'flex': '1',
        'font-weight': 'bold',
        'font-size': '18px' if nutrient == 'calories' else '16px',
        'margin-left': '5%',
        'display': 'flex',
        'align-items': 'center',
    }

    value_style = {
        'flex': '1',
        'text-align': 'right',
        'font-size': '16px' if nutrient == 'calories' else '14px',
        'margin-right': '5%',
    }

    # Toggle button ID
    toggle_button_id = {'type': 'toggle-button', 'index': nutrient}

    # Create the macro bar with a toggle button
    macro_bar = html.Div([
        html.Div([
            html.Span([nutrient_name, info_icon], style=label_style),
            html.Span(display_text, style=value_style),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '5px'}),
        dbc.Progress(
            value=percentage,
            max=100,
            style=bar_style,
            color=nutrient_colors.get(nutrient, 'primary'),
            striped=False,
        ),
        # Add the toggle button
        dbc.Button(
            f"Show {nutrient_name} breakdown",
            id=toggle_button_id,
            color="link",
            style={'margin-left': '5%'},
        ),
    ], style={'margin-bottom': '15px'})

    return macro_bar

def create_stacked_bar(name, total_value, components, color_list, info_id_prefix):
    """
    Create a stacked progress bar for sub-nutrients.
    """
    # Scale components if necessary
    total_components = sum(components.values())
    if total_components > total_value:
        scale_factor = total_value / total_components if total_components != 0 else 0
        for comp in components:
            components[comp] *= scale_factor
    elif total_components < total_value:
        components['Other'] = total_value - total_components

    # Create segments for the stacked progress bar
    bar_segments = []
    num_components = len(components)
    # Generate lighter shades of the nutrient color
    color_list = color_list[:num_components]

    for idx, (comp_name, comp_value) in enumerate(components.items()):
        comp_percentage = (comp_value / total_value) * 100 if total_value != 0 else 0
        color = color_list[idx % len(color_list)]
        bar_segments.append(
            dbc.Progress(
                value=comp_percentage,
                color=color,
                label=f"{comp_name}: {comp_value:.1f}g",
                bar=True,
                style={'color': 'black'}  # Labels in black
            )
        )

    # Sub-bar styles
    sub_bar_style = {
        'height': '30px',
        'border-radius': '10px',
        'margin-left': '10%',
        'margin-right': '10%',
    }

    sub_label_style = {
        'flex': '1',
        'font-weight': 'bold',
        'font-size': '14px',
        'margin-left': '5%',
        'display': 'flex',
        'align-items': 'center',
    }

    sub_value_style = {
        'flex': '1',
        'text-align': 'right',
        'font-size': '12px',
        'margin-right': '5%',
    }

    # Text to display on the right side
    display_text = f"{total_value:.1f} g"

    # Create the information icon
    info_icon = create_info_icon(f"{info_id_prefix}-{name}", f"More information about {name}")

    # Create the sub-bar
    sub_bar = html.Div([
        html.Div([
            html.Span([name, info_icon], style=sub_label_style),
            html.Span(display_text, style=sub_value_style),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '5px'}),
        dbc.Progress(
            bar_segments,
            style=sub_bar_style,
        ),
    ], style={'margin-bottom': '10px'})
    return sub_bar

def create_sub_bars(nutrient, json_entry, sub_nutrient_colors):
    """
    Create sub-bars for a given macro nutrient.
    """
    sub_bars = []

    if nutrient == 'carbohydrates':
        # Define sub-nutrient colors (lighter hues)
        color_list = sub_nutrient_colors['carbohydrates']
        info_id_prefix = 'info-carb'

        # Sugar
        sugar_value = json_entry.get('sugar', 0)
        monosaccharides = ['glucose', 'fructose', 'galactose', 'lactose']
        sugar_components = {mono.capitalize(): json_entry.get(mono, 0) for mono in monosaccharides}
        if sugar_value > 0:
            sugar_bar = create_stacked_bar(
                'Sugar',
                sugar_value,
                sugar_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(sugar_bar)

        # Fiber
        fiber_value = json_entry.get('fiber', 0)
        fiber_types = ['soluble_fiber', 'insoluble_fiber']
        fiber_components = {ft.replace('_', ' ').capitalize(): json_entry.get(ft, 0) for ft in fiber_types}
        if fiber_value > 0:
            fiber_bar = create_stacked_bar(
                'Fiber',
                fiber_value,
                fiber_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(fiber_bar)

        # Complex carbohydrates
        complex_value = json_entry.get('carbohydrates', 0) - sugar_value - fiber_value
        if complex_value < 0:
            complex_value = 0  # Avoid negative values

        complex_types = ['oligosaccharides', 'polysaccharides']
        complex_components = {ct.capitalize(): json_entry.get(ct, 0) for ct in complex_types}
        if complex_value > 0:
            complex_bar = create_stacked_bar(
                'Complex Carbs',
                complex_value,
                complex_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(complex_bar)

    elif nutrient == 'fat':
        # Define sub-nutrient colors (lighter hues)
        color_list = sub_nutrient_colors['fat']
        info_id_prefix = 'info-fat'

        # Triglycerides
        triglycerides_components = {
            'Unsaturated Fat': json_entry.get('unsaturated_fat', 0),
            'Saturated Fat': json_entry.get('saturated_fat', 0)
        }
        triglycerides_value = sum(triglycerides_components.values())
        if triglycerides_value > 0:
            triglycerides_bar = create_stacked_bar(
                'Triglycerides',
                triglycerides_value,
                triglycerides_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(triglycerides_bar)

        # Phospholipids
        phospholipids_value = json_entry.get('phospholipids', 0)
        if phospholipids_value > 0:
            phospholipids_bar = create_stacked_bar(
                'Phospholipids',
                phospholipids_value,
                {'Phospholipids': phospholipids_value},
                color_list,
                info_id_prefix
            )
            sub_bars.append(phospholipids_bar)

        # Sterols
        sterols_value = json_entry.get('sterols', 0)
        if sterols_value > 0:
            sterols_bar = create_stacked_bar(
                'Sterols',
                sterols_value,
                {'Sterols': sterols_value},
                color_list,
                info_id_prefix
            )
            sub_bars.append(sterols_bar)

    elif nutrient == 'protein':
        # Define sub-nutrient colors (lighter hues)
        color_list = sub_nutrient_colors['protein']
        info_id_prefix = 'info-protein'

        # Essential Amino Acids
        essential_aa_list = ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine',
                             'phenylalanine', 'threonine', 'tryptophan', 'valine']
        essential_aa_components = {aa.capitalize(): json_entry.get(aa, 0) for aa in essential_aa_list}
        essential_total = sum(essential_aa_components.values())
        if essential_total > 0:
            essential_bar = create_stacked_bar(
                'Essential Amino Acids',
                essential_total,
                essential_aa_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(essential_bar)

        # Conditionally Essential Amino Acids
        cond_essential_aa_list = ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine']
        cond_essential_aa_components = {aa.capitalize(): json_entry.get(aa, 0) for aa in cond_essential_aa_list}
        cond_essential_total = sum(cond_essential_aa_components.values())
        if cond_essential_total > 0:
            cond_essential_bar = create_stacked_bar(
                'Conditionally Essential Amino Acids',
                cond_essential_total,
                cond_essential_aa_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(cond_essential_bar)

        # Nonessential Amino Acids
        nonessential_aa_list = ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid',
                                'serine', 'selenocysteine', 'pyrrolysine']
        nonessential_aa_components = {aa.capitalize(): json_entry.get(aa, 0) for aa in nonessential_aa_list}
        nonessential_total = sum(nonessential_aa_components.values())
        if nonessential_total > 0:
            nonessential_bar = create_stacked_bar(
                'Nonessential Amino Acids',
                nonessential_total,
                nonessential_aa_components,
                color_list,
                info_id_prefix
            )
            sub_bars.append(nonessential_bar)

    return sub_bars

def create_nutrient_bubbles(json_entry):
    """
    Create nutrient bubbles for minerals and vitamins using circlify.
    """
    # Define nutrients and their groups
    nutrients_info = [
        {
            'nutrients': ['iron', 'magnesium', 'zinc', 'calcium', 'potassium', 'sodium'],
            'group': 'Minerals',
            'color': 'darkgrey',
        },
        {
            'nutrients': ['phosphorus', 'copper', 'manganese', 'selenium', 'chromium', 'molybdenum', 'iodine'],
            'group': 'Detailed Minerals',
            'color': 'lightgrey',
        },
        {
            'nutrients': ['vitamin a', 'vitamin c', 'vitamin d', 'vitamin e', 'vitamin k', 'vitamin b'],
            'group': 'Vitamins',
            'color': 'firebrick',
        },
        {
            'nutrients': ['thiamin (b1)', 'riboflavin (b2)', 'niacin (b3)', 'vitamin b6', 'folate (b9)', 'vitamin b12', 'biotin', 'pantothenic acid (b5)'],
            'group': 'Detailed Vitamins',
            'color': 'coral',
        },
    ]

    # Collect nutrient data
    nutrient_data = []
    for info in nutrients_info:
        for nutrient in info['nutrients']:
            key = nutrient.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').lower()

            # Safely convert the value to a float, or use 0 if conversion fails
            value = json_entry.get(key, 0)
            try:
                value = float(value)  # Attempt to convert to float
            except ValueError:
                value = 0  # Default to 0 if the conversion fails

            if value > 0:
                nutrient_data.append({
                    'id': nutrient.capitalize(),
                    'datum': value,
                    'group': info['group'],
                    'color': info['color'],
                })

    if nutrient_data:
        # Prepare data for circlify
        total_value = sum(item['datum'] for item in nutrient_data)
        circles = circlify.circlify(
            [item['datum'] for item in nutrient_data],
            show_enclosure=False,
            target_enclosure=circlify.Circle(x=0, y=0, r=1)
        )

        # Create a DataFrame with circle positions
        for i, circle in enumerate(circles):
            nutrient_data[i]['x'] = circle.x
            nutrient_data[i]['y'] = circle.y
            nutrient_data[i]['r'] = circle.r

        df = pd.DataFrame(nutrient_data)

        # Determine which labels to show based on minimum radius
        min_radius_for_label = 0.05  # Adjust as needed
        df['show_label'] = df['r'] >= min_radius_for_label

        # Create bubble chart
        fig = px.scatter(df, x='x', y='y',
                         size='r', color='group', hover_name='id',
                         color_discrete_map={
                             'Minerals': 'darkgrey',
                             'Detailed Minerals': 'lightgrey',
                             'Vitamins': 'firebrick',
                             'Detailed Vitamins': 'coral'
                         },
                         size_max=60,
                         labels={'group': 'Category'}
                         )

        # Add labels for larger bubbles
        for _, row in df.iterrows():
            if row['show_label']:
                fig.add_annotation(
                    x=row['x'],
                    y=row['y'],
                    text=row['id'],
                    showarrow=False,
                    font_size=12,
                    font_color='white' if row['color'] in ['firebrick', 'coral'] else 'black',
                )

        fig.update_traces(mode='markers', marker=dict(sizemode='area', sizeref=2.*max(df['r'])/(60.**2)))
        fig.update_layout(showlegend=True, xaxis={'visible': False}, yaxis={'visible': False},
                          margin=dict(l=20, r=20, t=20, b=20), height=400)
        fig.update_layout(plot_bgcolor='white')

        bubble_chart = dcc.Graph(figure=fig)
        return bubble_chart
    else:
        return html.Div("No minerals or vitamins data available.")

def collate_current_item(json_entry, weight_input, meal_type, recommended_intakes):
    """
    Collate the current item into a layout with macro and sub-nutrient progress bars.
    """
    # Colors for each nutrient (pastel colors as specified)
    nutrient_colors = {
        'calories': '#ff9999',        # Pastel red
        'carbohydrates': '#6699cc',   # Darker blue
        'fat': '#ffcc99',             # Yellow-orange
        'protein': '#99cc99',         # Pastel green
    }

    # Sub-colors for each nutrient (lighter hues)
    sub_nutrient_colors = {
        'carbohydrates': ['#cce0ff', '#d9e6f2', '#e6f2ff', '#f2f9ff', '#f9fcff'],
        'fat': ['#fff2e6', '#fff7eb', '#fffbf2', '#fff0e6', '#ffe6d9'],
        'protein': ['#e6ffe6', '#f2fff2', '#f9fff9', '#e6ffe6', '#ccffcc'],
    }

    header = create_header(json_entry)
    progress_bars = []
    sub_bars_list = []  # To store sub-bars and their associated toggles

    for nutrient, recommended_value in recommended_intakes.items():
        actual_value = json_entry.get(nutrient, 0)
        macro_bar = create_macro_bar(nutrient, actual_value, recommended_value, nutrient_colors)
        progress_bars.append(macro_bar)

        # Create sub-bars
        sub_bars = create_sub_bars(nutrient, json_entry, sub_nutrient_colors)

        if sub_bars:
            # Wrap sub-bars in a Collapse component
            collapse = dbc.Collapse(
                sub_bars,
                id={'type': 'collapse', 'index': nutrient},
                is_open=False,
            )
            sub_bars_list.append(collapse)
        else:
            sub_bars_list.append(html.Div())  # Placeholder if no sub-bars

    # Create nutrient bubbles
    nutrient_bubbles = create_nutrient_bubbles(json_entry)

    # Combine all parts into a layout
    layout = html.Div([
        header,
        html.Div([
            item for pair in zip(progress_bars, sub_bars_list) for item in pair
        ]),
        html.Hr(),
        html.Div([
            html.H4("Minerals and Vitamins", style={'text-align': 'center', 'margin-top': '20px'}),
            nutrient_bubbles
        ])
    ], style={'padding': '10px'})

    return layout
