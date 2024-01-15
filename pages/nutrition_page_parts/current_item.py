
import dash
from dash import html

def collate_current_item(json_entry, 
                         weight_input, meal_type):



    essential_amino_acids = [
        "histidine",
        "isoleucine",
        "leucine",
        "lysine",
        "methionine",
        "phenylalanine",
        "threonine",
        "tryptophan",
        "valine"
    ]

    recommended_intakes = {
        "histidine": 14,        # Estimated at 0.2g per kg of body weight
        "isoleucine": 20,       # Estimated at 1g per kg of body weight
        "leucine": 42,         # Estimated at 2g per kg of body weight
        "lysine": 38,           # Estimated at 1g per kg of body weight
        "methionine": 19,       # Estimated at 0.5g per kg of body weight (together with cysteine)
        "phenylalanine": 33,    # Estimated at 1g per kg of body weight (together with tyrosine)
        "threonine": 20,        # Estimated at 0.8g per kg of body weight
        "tryptophan": 5,       # Estimated at 0.2g per kg of body weight
        "valine": 26,            # Estimated at 1g per kg of body weight
    }
    # Convert from grams to milligrams
    recommended_intakes_mg = {key: value * 70 for key, value in recommended_intakes.items()}
    def create_amino_acid_progress_bar(amino_acid):
        if amino_acid in json_entry:
            max_amount = recommended_intakes_mg[amino_acid]
            actual_amount = json_entry[amino_acid]
            progress = actual_amount / max_amount
            progress_percentage = f"{progress * 100:.2f}%"
            amount_display = f"{actual_amount} mg ({progress_percentage})"

            if 'name' not in json_entry:
                json_entry['name'] = 'Name not found.'

            return html.Div([
                html.Div(f"{amino_acid.capitalize()}: ", style={'padding': '0', 'display': 'inline-block', 'width': '15%'}),
                html.Div([
                    html.Div(style={'width': progress_percentage, 'height': '3px', 'backgroundColor': 'lightblue'}),
                    html.Div(style={'width': f"{100 - progress * 100:.2f}%", 'height': '3px', 'backgroundColor': 'grey'})
                ], style={'display': 'flex', 'width': '45%', 'alignItems': 'center', 'margin': '0'}),
                html.Div(amount_display, style={'padding': '0', 'display': 'inline-block', 'fontSize': 'smaller'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'margin': '0'})
        else:
            print(f'{amino_acid} not found.')








    print('json_entry in current item', json_entry)

    layout = html.Div([
            # Name of the food item
            html.H4(json_entry['name'], style={'textAlign': 'center', 'paddingBottom': '10px'}),
            html.H5(meal_type, style={'textAlign': 'center', 'paddingBottom': '10px'}),

            # First row for main macros
            html.Div([
                html.Div(f"Calories: {json_entry['calories']:.2f} kcal", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Carbohydrates: {json_entry['carbohydrates']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Fat: {json_entry['total fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Protein: {json_entry['protein']:.2f} g", style={'padding': '5px', 'display': 'inline-block'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '10px'}),

            # Second row for additional info
            html.Div([
                html.Div(f"Sugar: {json_entry['sugar']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Saturated Fat: {json_entry['saturated fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Unsaturated Fat: {json_entry['unsaturated fat']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),
                html.Div(f"Fiber: {json_entry['fiber']:.2f} g", style={'padding': '5px', 'display': 'inline-block'}),

            ], style={'display': 'flex', 'justifyContent': 'space-around'}),


            html.Div([    
                html.Div(f"Glycemic Index: {json_entry['GI']:.2f} ", style={'padding': '5px', 'display': 'inline-block'}),
                ], style={'display': 'flex', 'justifyContent': 'space-around'}),

            html.Div([create_amino_acid_progress_bar(amino_acid) for amino_acid in essential_amino_acids], style={'marginBottom': '10px'}),



        ])
    
    return layout