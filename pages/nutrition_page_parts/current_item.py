
import dash
from dash import html

def collate_current_item(json_entry, 
                         weight_input, meal_type):



    layout = html.Div([
            # Name of the food item
            html.H4(json_entry['name'], style={'textAlign': 'center', 'paddingBottom': '10px'}),
            html.H5(meal_type, style={'textAlign': 'center', 'paddingBottom': '10px'}),

            # First row for main macros
            html.Div([
                html.Div(f"Calories: {json_entry['calories']:.2f} kcal", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Carbohydrates: {json_entry['carbohydrates']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Fat: {json_entry['fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Protein: {json_entry['protein']:.2f} g", style={'padding': '5px', 'display': 'inline-block'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '10px'}),

            # Second row for additional info
            html.Div([
                html.Div(f"Sugar: {json_entry['sugar']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Saturated Fat: {json_entry['saturated fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Unsaturated Fat: {json_entry['unsaturated fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Fiber: {json_entry['fiber']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),

            html.Div([    
                html.Div(f"Glycemic Index: {json_entry['GI']:.2f} ", style={'padding': '5px', 'display': 'inline-block'}),
                ]),

            ], style={'display': 'flex', 'justifyContent': 'space-around'})
        ])
    
    return layout