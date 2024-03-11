
import dash
from dash import html
import plotly.graph_objs as go
from dash import dcc

from functions.nutrition_plots import *


def format_value(value, format_str='{:.2f}'):
    """Formats the value using the given format string if it's a number, otherwise returns it as is."""
    try:
        # Check if value is a number and format it
        return format_str.format(value)
    except (ValueError, TypeError):
        # Return the value as is if it's not a number
        return value
    

def collate_current_item(json_entry, 
                         weight_input, meal_type):

    body_weight_kg = 70

    print(json_entry)
    print('PUTTING TOGETHER CURRENT ITEM',json_entry )
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

    recommended_minerals = {
        "calcium": 1000,          # mg
        "iron": 8,                # mg
        "magnesium": 420,         # mg
        "phosphorus": 700,        # mg
        "potassium": 3400,        # mg
        "sodium": 1500,           # mg
        "zinc": 11,               # mg
        "copper": 900,            # mcg to mg
        "manganese": 2.3,         # mg
        "selenium": 55 * 1000,    # mcg to mg
        "chromium": 35 * 1000,    # mcg to mg
        "molybdenum": 45 * 1000,  # mcg to mg
        "iodine": 150 * 1000      # mcg to mg
    }
    recommended_vitamins = {
        "vitamin a": 900 * 1000,  # mcg to mg
        "vitamin c": 90,          # mg
        "vitamin d": 20 * 1000,   # mcg to mg
        "vitamin e": 15,          # mg
        "vitamin k": 120 * 1000,  # mcg to mg
        "thiamin (b1)": 1.2,      # mg
        "riboflavin (b2)": 1.3,   # mg
        "niacin (b3)": 16,        # mg
        "vitamin b6": 1.7,        # mg
        "folate (b9)": 400 * 1000, # mcg to mg
        "vitamin b12": 2.4 * 1000, # mcg to mg
        "biotin": 30 * 1000,      # mcg to mg
        "pantothenic acid (b5)": 5 # mg
    }

    # Convert from grams to milligrams 
    recommended_intakes_mg = {key: value * body_weight_kg for key, value in recommended_intakes.items()}

    def create_stacked_amino_acid_plot(json_entry, recommended_intakes_mg):
        amino_acid_names = list(recommended_intakes_mg.keys())
        completed_percentages = []
        remaining_percentages = []
        hover_texts = []

        for amino_acid in amino_acid_names:
            actual_amount = json_entry.get(amino_acid, 0)
            recommended_amount = recommended_intakes_mg[amino_acid]
            completed_percentage = (actual_amount / recommended_amount) * 100*1000
            remaining_percentage = 100 - completed_percentage
            
            completed_percentages.append(completed_percentage)
            remaining_percentages.append(remaining_percentage)
            
            hover_text = f"{amino_acid}: {actual_amount}mg ({completed_percentage:.0f}%)"
            hover_texts.append(hover_text)

        return amino_acid_names, completed_percentages, remaining_percentages, hover_texts



    def plot_stacked_amino_acid_chart(json_entry, recommended_intakes_mg):
        amino_acid_names, completed_percentages, remaining_percentages, _ = create_stacked_amino_acid_plot(json_entry, recommended_intakes_mg)
        # Setting up custom hover text for both parts
        custom_hover_texts = [f"{round(json_entry.get(amino_acid, 0))}mg<br>({round((json_entry.get(amino_acid, 0) / recommended_intakes_mg[amino_acid]) * 100)}%)" for amino_acid in amino_acid_names]
        
        # Pastel colors
        pastel_blue = 'rgba(173, 216, 230, 0.6)'
        pastel_grey = 'rgba(220, 220, 220, 0.6)'
        
        fig = go.Figure(data=[
            go.Bar(name='Completed', x=amino_acid_names, y=completed_percentages, marker_color=pastel_blue, hoverinfo='text', hovertext=custom_hover_texts),
            go.Bar(name='Remaining', x=amino_acid_names, y=remaining_percentages, marker_color=pastel_grey, hoverinfo='text', hovertext=custom_hover_texts)
        ])
        
        fig.update_layout(
            barmode='stack',
            plot_bgcolor='white',
            showlegend=False,
            width=300,  # Adjusting the width to 50%
            height=200,  # Reducing the height
            xaxis=dict(tickangle=-90),  # Vertical x-axis labels
            yaxis=dict(showticklabels=False),  # Remove y-axis labels
            margin=dict(l=20, r=20, t=20, b=20)  # Adjust margins to reduce white space
        )
        
        return fig



    # Define your macros and values
    macros = ['carbohydrates', 'protein', 'fat']
    values = [json_entry.get(macro, 0) for macro in macros]
    colors = ['#ff9999', '#66b3ff', '#99ff99']  # Pastel colors

    # Create traces for each macro
    traces = []
    for i, macro in enumerate(macros):
        traces.append(go.Bar(
            name=macro,
            x=[values[i]],
            y=["Nutrients"],
            orientation='h',
            marker=dict(color=colors[i])
        ))

    # Create the stacked horizontal bar chart
    stacked_bar_chart = dcc.Graph(
        figure={
            'data': traces,
            'layout': go.Layout(
                barmode='stack',  # Stacked mode
                xaxis=dict(showticklabels=False, zeroline=False),  # Hide x-axis labels
                yaxis=dict(showticklabels=False),  # Hide y-axis labels
                showlegend=False,  # Optionally hide the legend
                font=dict(family='Libre Franklin Light'),
                margin=dict(l=30, r=30, t=10, b=10),  # Adjust margins (30px padding on the sides)
                height=30,  # Adjust height
                autosize=True,  # Enable autosizing to fill width
                paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
                plot_bgcolor='rgba(0,0,0,0)'  # Transparent background
            )
        },
        config={
            'displayModeBar': False  # Optionally hide the mode bar
        }
    )



    # Labels for each segment
    labels = ["Protein", "Carbohydrates", "Total Fat", 
        "Sugar", "Fiber", "Saturated Fat", "Unsaturated Fat", "Cholesterol",
        "Essential", "Conditionally Essential", "Nonessential",
        "Glucose", "Fructose", "Galactose", "Lactose",
        "Soluble Fiber", "Insoluble Fiber",
        # Essential Amino Acids
        "Histidine", "Isoleucine", "Leucine", "Lysine", "Methionine", "Phenylalanine", "Threonine", "Tryptophan", "Valine",
        # Conditionally Essential Amino Acids
        "Arginine", "Cysteine", "Glutamine", "Glycine", "Proline", "Tyrosine",
        # Nonessential Amino Acids
        "Alanine", "Aspartic Acid", "Asparagine", "Glutamic Acid", "Serine", "Selenocysteine", "Pyrrolysine"
    ]

    # Parents for each segment
    parents = [ None, None, None,
        "Carbohydrates", "Carbohydrates", "Total Fat", "Total Fat", "Total Fat",
        "Protein", "Protein", "Protein",
        "Sugar", "Sugar", "Sugar", "Sugar",
        "Fiber", "Fiber",
        # Essential Amino Acids
        "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential",
        # Conditionally Essential Amino Acids
        "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential",
        # Nonessential Amino Acids
        "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential"
    ]

    # Values for each segment (example values, replace with your actual data) #json_entry.get('calories', 0),
    values = [
        json_entry.get('protein', 0),
        json_entry.get('carbohydrates', 0), 
        json_entry.get('fat', 0),
        json_entry.get('sugar', 0), 
        json_entry.get('fiber', 0), 
        json_entry.get('saturated fat', 0), 
        json_entry.get('unsaturated fat', 0), 
        json_entry.get('cholesterol', 0),
        # Sum of essential amino acids values
        sum([json_entry.get(aa, 0) for aa in ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine']]),
        # Sum of conditionally essential amino acids values
        sum([json_entry.get(aa, 0) for aa in ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine']]),
        # Sum of nonessential amino acids values
        sum([json_entry.get(aa, 0) for aa in ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine']]),
        json_entry.get('glucose', 0), 
        json_entry.get('fructose', 0), 
        json_entry.get('galactose', 0), 
        json_entry.get('lactose', 0),
        json_entry.get('soluble fiber', 0), 
        json_entry.get('insoluble fiber', 0),
        # Essential Amino Acids
        json_entry.get('histidine', 0), 
        json_entry.get('isoleucine', 0), 
        json_entry.get('leucine', 0), 
        json_entry.get('lysine', 0), 
        json_entry.get('methionine', 0), 
        json_entry.get('phenylalanine', 0), 
        json_entry.get('threonine', 0), 
        json_entry.get('tryptophan', 0), 
        json_entry.get('valine', 0),
        # Conditionally Essential Amino Acids
        json_entry.get('arginine', 0), 
        json_entry.get('cysteine', 0), 
        json_entry.get('glutamine', 0), 
        json_entry.get('glycine', 0), 
        json_entry.get('proline', 0), 
        json_entry.get('tyrosine', 0),
        # Nonessential Amino Acids
        json_entry.get('alanine', 0), 
        json_entry.get('aspartic acid', 0), 
        json_entry.get('asparagine', 0), 
        json_entry.get('glutamic acid', 0), 
        json_entry.get('serine', 0), 
        json_entry.get('selenocysteine', 0), 
        json_entry.get('pyrrolysine', 0)
    ]

    print("LENGTHS: ", len(labels), len(parents), len(values))

    
# Preparing data for the sunburst chart
    # labels = ["Carbohydrates", "Protein", "Total Fat", "Sugar", "Fiber", "Saturated Fat", "Unsaturated Fat",
    #            "Cholesterol"
    #            ] #, "Essential Amino Acids", "Non-Essential Amino Acids", "Valine"]
    # parents = ["Calories", "Calories", "Calories", "Carbohydrates", "Carbohydrates", "Total Fat", "Total Fat",
    #             "Total Fat"
    #             ] #, "Protein" #, "Protein", "Essential Amino Acids"]
    # values = [json_entry['carbohydrates'], json_entry['protein'], json_entry['fat'],
    #            json_entry.get('sugar', 0), json_entry.get('fiber', 0), 
    #            json_entry.get('saturated fat', 0),
    #            json_entry.get('unsaturated fat', 0),
    #            1,
    #         #    json_entry.get('cholesterol', 0)
    #            ] 

    # labels =["Protein", "Carbohydrates", "Total Fat", 
    #     # "Sugar", "Fiber", "Saturated Fat", "Unsaturated Fat", "Cholesterol",
    #     # "Essential", "Conditionally Essential", "Nonessential",
    #     # "Glucose", "Fructose", "Galactose", "Lactose",
    #     # "Soluble Fiber", "Insoluble Fiber"
    #     ]
    # parents = ["Calories", "Calories", "Calories",
    #     # "Carbohydrates", "Carbohydrates", "Total Fat", "Total Fat", "Total Fat",
    #     # "Protein", "Protein", "Protein",
    #     # "Sugar", "Sugar", "Sugar", "Sugar",
    #     # "Fiber", "Fiber"
    #            ]
    # parents = [
    #    json_entry['carbohydrates'], json_entry['protein'], json_entry['fat']
    #     # json_entry.get('sugar', 0), 
    #     # json_entry.get('fiber', 0), 
    #     # json_entry.get('saturated fat', 0), 
    #     # json_entry.get('unsaturated fat', 0), 
    #     # json_entry.get('cholesterol', 0),
    #     # # Sum of essential amino acids values
    #     # sum([json_entry.get(aa, 0) for aa in ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine']]),
    #     # # Sum of conditionally essential amino acids values
    #     # sum([json_entry.get(aa, 0) for aa in ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine']]),
    #     # # Sum of nonessential amino acids values
    #     # sum([json_entry.get(aa, 0) for aa in ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine']]),
    #     # json_entry.get('glucose', 0), 
    #     # json_entry.get('fructose', 0), 
    #     # json_entry.get('galactose', 0), 
    #     # json_entry.get('lactose', 0),
    #     # json_entry.get('soluble fiber', 0), 
    #     # json_entry.get('insoluble fiber', 0),
    #     ]



    sunburst_chart = dcc.Graph(
            figure=go.Figure(
                go.Sunburst(
                    labels=labels,
                    parents=parents,
                    values=values,
                    branchvalues="total",
                    hoverinfo="label+value+percent parent"
                ),
                layout=go.Layout(
                    margin=dict(t=0, l=0, r=0, b=0),
                    # Make sure to set a fixed height and width in the layout
                    height=300,  # Define the fixed height
                    width=300,   # Define the fixed width
                    extendpiecolors=True,  # Optional: Extend colorway for depth
                    font=dict(family='Libre Franklin Light'),  # Assuming this font is loaded
                )
            ),
            style={'width': '300px', 'height': '300px', 'padding': '0px'},
            config={'responsive': False}  # Prevent the chart from being responsive
        )



    # Formatting values with superscript labels
    def format_macros(label, value):
        return html.Div([html.Span(label, style={'fontSize': '14px'}), f" {value:.2f} g"], style={'fontSize': '22px'})

    # define values for circular progress
    nutrition_values = [
        create_circular_progress(json_entry.get('protein', 0), 140, "", "Protein", "#ff6384", radius=45, fontsize_text=16, fontsize_num=24, layout_direction='below'),
        create_circular_progress(json_entry.get('fat', 0), 100, "", "Fat", "#36a2eb", radius=45, fontsize_text=16, fontsize_num=24),
        create_circular_progress(json_entry.get('carbohydrates', 0), 250, "", "Carbohydrates", "#4bc0c0", radius=45, fontsize_text=16, fontsize_num=24)]
    # Additional values for Carbs, Protein, Fat
    additional_values = {
        'carbs': [
            create_circular_progress(json_entry.get('sugar', 0), 100, "g", "Sugar", "#ff9f40", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 ),
            create_circular_progress(json_entry.get('fiber', 0), 30, "g", "Fiber", "#ffcd56", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 )
        ],
        'protein': [
            create_circular_progress(json_entry.get('essential amino acids', 0), 50, "g", "Essential Amino Acids", "#9966ff", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 ),
            create_circular_progress(json_entry.get('nonessential amino acids', 0), 50, "g", "Nonessential Amino Acids", "#c9cbcf", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 )
        ],
        'fat': [
            create_circular_progress(json_entry.get('saturated fat', 0), 20, "g", "Saturated Fat", "#ff6384", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 ),
            create_circular_progress(json_entry.get('unsaturated fat', 0), 30, "g", "Unsaturated Fat", "#36a2eb", layout_direction='right', radius=20, fontsize_num=18, fontsize_text=14 )
        ]
    }





    layout = html.Div([


        # Main horizontal layout
        html.Div([
            # Circular progress on the left, adjusted to align bottom with the right side elements
            html.Div([
                create_circular_progress(json_entry.get('calories', 0), 3400, " ", "Daily Calories", "#4CAF50", 
                                        layout_direction='below', radius=65, fontsize_text=16, fontsize_num=30, 
                                        stroke_width_backgr=8, stroke_width_complete=12, stroke_dashoffset=0),
            ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'alignItems': 'flex-end'}),

            # Right side vertical layout
            html.Div([
                # Food name and calories
                html.Div([
                    html.H4(json_entry.get('name', ''), style={'fontSize': '22px', 'textAlign': 'center'}),
                    html.P([f"{json_entry.get('calories', '')} ", html.Sub("kcal")], style={'fontSize': '24px', 'textAlign': 'center'}),
                    html.H5(meal_type, style={'textAlign': 'center', 'paddingBottom': '10px'}),
                ], style={'paddingBottom': '20px'}),
                
                # Horizontal layout for the three nutritional values, closer together
                html.Div([
                    create_longitudinal_box_with_progress(
                        json_entry.get('carbohydrates', 0), 350, "Carbs", "#0b67b5", 
                        box_color="#2678bf", gradient_color_start="#83B3DB", gradient_color_end="#99c4e8", 
                        layout_direction='below', radius=20, fontsize_text=13, fontsize_num=20, 
                        stroke_width_backgr=2.5, stroke_width_complete=5, stroke_dashoffset=0
                    ),
                    create_longitudinal_box_with_progress(
                        json_entry.get('protein', 0), 250, "Protein", "#0c96a8", 
                        box_color="#42b4c2", gradient_color_start="#8CD3DB", gradient_color_end="#b0e2e8", 
                        layout_direction='below', radius=20, fontsize_text=13, fontsize_num=20, 
                        stroke_width_backgr=2.5, stroke_width_complete=5, stroke_dashoffset=0
                    ),
                    create_longitudinal_box_with_progress(
                        json_entry.get('fat', 0), 120, "Fat", "#1fab69", 
                        box_color="#5dc795", gradient_color_start="#A0DBBF", gradient_color_end="#b8e0cd", 
                        layout_direction='below', radius=20, fontsize_text=13, fontsize_num=20, 
                        stroke_width_backgr=2.5, stroke_width_complete=5, stroke_dashoffset=0
                    ),
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '10px'}),  # Adjusted for closer elements
            ], style={'flex': '2', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between'}),

        ], style={'display': 'flex', 'flexDirection': 'row'}),


        html.Div(
            [sunburst_chart], 
            className='custom-sunburst', 
            style={
                'padding': '20px', 
                'display': 'flex', 
                'justify-content': 'center'  # This will center the chart horizontally
            }
        ),

        # Main circular progress indicators in a row
        html.Div([
            html.Div(nutrition_values[0], className="column"),  # Carbs
            html.Div(nutrition_values[1], className="column"),  # Protein
            html.Div(nutrition_values[2], className="column")   # Fat
        ], style={'display': 'flex', 'justify-content': 'space-around', 'text-align': 'center'}),

        # Additional values below main indicators
        html.Div([
            # Carbs additional values
            html.Div([
                html.Div(additional_values['carbs'], className="column")
            ], className="column"),
            # Protein additional values
            html.Div([
                html.Div(additional_values['protein'], className="column")
            ], className="column"),
            # Fat additional values
            html.Div([
                html.Div(additional_values['fat'], className="column")
            ], className="column")
        ], style={'display': 'flex', 'justify-content': 'space-around', 'text-align': 'center', 'margin-top': '20px'}),
        

        # Glycemic Index
        html.Div([
            html.Div(f"Glycemic Index: {format_value(json_entry.get('glycemic index', ''))}", style={'padding': '5px', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'justifyContent': 'space-around'}),


        dcc.Graph(figure=plot_stacked_amino_acid_chart(json_entry, recommended_intakes_mg)),



        ])
    
    return layout