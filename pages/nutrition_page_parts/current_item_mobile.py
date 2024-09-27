
import dash
from dash import html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import base64


# Function to create the circular progress circles

# Function to create the circular progress circles
def create_circular_progress(value, target, unit, description, color, layout_direction='below',
                              radius=45, fontsize_text=16, fontsize_num=36, stroke_width_backgr=4, 
                              stroke_width_complete=7, stroke_dashoffset=0):
    value = round(value)  # Round the value to an integer
    percentage = min(value / target, 1)  # Ensure percentage doesn't exceed 100%
    circumference = 2 * 3.14 * radius  # Circumference of the circle
    stroke_length = percentage * circumference

    # The dash array creates the stroke length
    stroke_dasharray = f"{stroke_length} {circumference}"

    svg_circle = f'''
    <svg width="{2*radius+10}" height="{2*radius+10}" viewBox="0 0 {2*radius+10} {2*radius+10}" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{radius+5}" cy="{radius+5}" r="{radius}" fill="transparent" stroke="#ddd" stroke-width="{stroke_width_backgr}"></circle>
        <circle cx="{radius+5}" cy="{radius+5}" r="{radius}" fill="transparent" stroke="{color}" stroke-width="{stroke_width_complete}"
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


# Utility function for rendering the nutrition content below circles
def render_nutrition_list(nutrition_list, color='black'):
    return html.Ul([html.Li(f"{name}: {value}g", style={'color': color}) for name, value in nutrition_list])



# def collate_current_item(json_entry, weight_input, meal_type):
#     body_weight_kg = 70

#     # Macros and colors for stacked bar chart
#     macros = ['carbohydrates', 'protein', 'fat']
#     values = [json_entry.get(macro, 0) for macro in macros]
#     colors = ['#ff9999', '#66b3ff', '#99ff99']  # Pastel colors

#     # Create traces for stacked bar chart
#     traces = [
#         go.Bar(name=macro, x=[values[i]], y=["Nutrients"], orientation='h', marker=dict(color=colors[i]))
#         for i, macro in enumerate(macros)
#     ]

#     stacked_bar_chart = dcc.Graph(
#         figure={
#             'data': traces,
#             'layout': go.Layout(
#                 barmode='stack',  
#                 xaxis=dict(showticklabels=False, zeroline=False),
#                 yaxis=dict(showticklabels=False),
#                 showlegend=False,
#                 font=dict(family='Libre Franklin Light'),
#                 margin=dict(l=30, r=30, t=10, b=10),
#                 height=30,  # Mobile-friendly height
#                 autosize=True,
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 plot_bgcolor='rgba(0,0,0,0)'
#             )
#         },
#         config={'displayModeBar': False}
#     )







#     # Labels for each segment
#     labels = ["Protein", "Carbohydrates", "Total Fat", 
#         "Sugar", 
#           "Fiber", 
#         "Saturated Fat", "Unsaturated Fat", 
#         "Essential", "Conditionally Essential", "Nonessential",
#         "Glucose", "Fructose", "Galactose", "Lactose",
#         "Soluble Fiber", "Insoluble Fiber",
#         # Essential Amino Acids
#         "Histidine", "Isoleucine", "Leucine", "Lysine", "Methionine", "Phenylalanine", "Threonine", "Tryptophan", "Valine",
#         # Conditionally Essential Amino Acids
#         "Arginine", "Cysteine", "Glutamine", "Glycine", "Proline", "Tyrosine",
#         # Nonessential Amino Acids
#         "Alanine", "Aspartic Acid", "Asparagine", "Glutamic Acid", "Serine", "Selenocysteine", "Pyrrolysine"
#     ]

#     # Parents for each segment
#     parents = [ None, None, None,
#         "Carbohydrates", 
#         "Carbohydrates", 
#         "Total Fat", "Total Fat",
#         "Protein", "Protein", "Protein",
#         "Sugar", "Sugar", "Sugar", "Sugar",
#         "Fiber", "Fiber",
#         # Essential Amino Acids
#         "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential", "Essential",
#         # Conditionally Essential Amino Acids
#         "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential", "Conditionally Essential",
#         # Nonessential Amino Acids
#         "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential", "Nonessential"
#     ]

#     # Values for each segment (example values, replace with your actual data) #json_entry.get('calories', 0),
#     values = [
#         json_entry.get('protein', 0),
#         json_entry.get('carbohydrates', 0), 
#         json_entry.get('fat', 0),
#         json_entry.get('sugar', 0), 
#         json_entry.get('fiber', 0), 
#         json_entry.get('saturated fat', 0), 
#         json_entry.get('unsaturated fat', 0), 
#         # Sum of essential amino acids values
#         sum([json_entry.get(aa, 0) for aa in ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine']]),
#         # Sum of conditionally essential amino acids values
#         sum([json_entry.get(aa, 0) for aa in ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine']]),
#         # Sum of nonessential amino acids values
#         sum([json_entry.get(aa, 0) for aa in ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine']]),
#         json_entry.get('glucose', 0), 
#         json_entry.get('fructose', 0), 
#         json_entry.get('galactose', 0), 
#         json_entry.get('lactose', 0),
#         json_entry.get('soluble fiber', 0), 
#         json_entry.get('insoluble fiber', 0),
#         # Essential Amino Acids
#         json_entry.get('histidine', 0), 
#         json_entry.get('isoleucine', 0), 
#         json_entry.get('leucine', 0), 
#         json_entry.get('lysine', 0), 
#         json_entry.get('methionine', 0), 
#         json_entry.get('phenylalanine', 0), 
#         json_entry.get('threonine', 0), 
#         json_entry.get('tryptophan', 0), 
#         json_entry.get('valine', 0),
#         # Conditionally Essential Amino Acids
#         json_entry.get('arginine', 0), 
#         json_entry.get('cysteine', 0), 
#         json_entry.get('glutamine', 0), 
#         json_entry.get('glycine', 0), 
#         json_entry.get('proline', 0), 
#         json_entry.get('tyrosine', 0),
#         # Nonessential Amino Acids
#         json_entry.get('alanine', 0), 
#         json_entry.get('aspartic acid', 0), 
#         json_entry.get('asparagine', 0), 
#         json_entry.get('glutamic acid', 0), 
#         json_entry.get('serine', 0), 
#         json_entry.get('selenocysteine', 0), 
#         json_entry.get('pyrrolysine', 0)
#     ]

#     print("LENGTHS: ", len(labels), len(parents), len(values))

#     sunburst_chart = dcc.Graph(
#         figure=go.Figure(
#             go.Sunburst(
#                 labels=labels, #["Protein", "Carbs", "Fat"],
#                 parents=parents,#["", "", ""],
#                 values=values, #[json_entry.get('protein', 0), json_entry.get('carbohydrates', 0), json_entry.get('fat', 0)],
#                 branchvalues="total",
#                 hoverinfo="label+value+percent parent"
#             ),
#             layout=go.Layout(
#                 margin=dict(t=0, l=0, r=0, b=0),
#                 height=300,
#                 width=300,
#                 font=dict(family='Libre Franklin Light'),
#             )
#         ),
#         style={'width': '300px', 'height': '300px'},
#         config={'responsive': False}
#     )

#     layout = html.Div([

#         dbc.Row([
#             dbc.Col([
#                 html.Div([
#                     html.H4(json_entry.get('name', ''), style={'fontSize': '22px', 'textAlign': 'center'}),
#                     html.P(f"{json_entry.get('calories', 0)} kcal", style={'fontSize': '24px', 'textAlign': 'center'}),
#                     html.H5(meal_type, style={'textAlign': 'center', 'paddingBottom': '10px'}),
#                 ]),
#                 html.Div([
#                     stacked_bar_chart
#                 ], style={'padding': '10px'}),
#             ], width=12),
#         ], style={'padding': '10px'}),

#         dbc.Row([
#             dbc.Col([
#                 sunburst_chart
#             ], width=12),
#         ]),

#         dbc.Row([
#             dbc.Col([
#                 html.P(f"Glycemic Index: {json_entry.get('glycemic_index', 'N/A')}", style={'fontSize': '18px'})
#             ], width=12),
#         ], style={'textAlign': 'center', 'marginTop': '20px'}),
#     ], style={'padding': '10px'})

#     return layout


# Updated collate_current_item function
def collate_current_item(json_entry, weight_input, meal_type):
    # Creating the circular progress circles
    calories_circle = create_circular_progress(json_entry.get('calories', 0), 2000, "", "Calories", "#4CAF50", 
                                               layout_direction='below', radius=65, fontsize_text=16, fontsize_num=30, 
                                               stroke_width_backgr=8, stroke_width_complete=12, stroke_dashoffset=0)
    glycemic_index = html.P(f"Glycemic Index: {json_entry.get('glycemic_index', 'N/A')}", style={'fontSize': '20px', 'textAlign': 'center', 'marginBottom': '20px'})

    carbs_circle = create_circular_progress(json_entry.get('carbohydrates', 0), 300, "g", "Carbs", "#ff9999", 
                                            layout_direction='below', radius=45, fontsize_text=14, fontsize_num=24)

    protein_circle = create_circular_progress(json_entry.get('protein', 0), 150, "g", "Protein", "#66b3ff", 
                                              layout_direction='below', radius=45, fontsize_text=14, fontsize_num=24)

    fat_circle = create_circular_progress(json_entry.get('fat', 0), 70, "g", "Fat", "#99ff99", 
                                          layout_direction='below', radius=45, fontsize_text=14, fontsize_num=24)

    # Carbs details
    carbs_details = html.Div([
        html.P(f"Sugar: {json_entry.get('sugar', 0)}g", style={'color': 'black'}),
        html.P(f"Glucose: {json_entry.get('glucose', 0)}g", style={'color': 'grey'}),
        html.P(f"Fructose: {json_entry.get('fructose', 0)}g", style={'color': 'grey'}),
        html.P(f"Galactose: {json_entry.get('galactose', 0)}g", style={'color': 'grey'}),
        html.P(f"Lactose: {json_entry.get('lactose', 0)}g", style={'color': 'grey'}),
        html.P(f"Fiber: {json_entry.get('fiber', 0)}g", style={'color': 'black'}),
        html.P(f"Soluble Fiber: {json_entry.get('soluble_fiber', 0)}g", style={'color': 'grey'}),
        html.P(f"Insoluble Fiber: {json_entry.get('insoluble_fiber', 0)}g", style={'color': 'grey'}),
    ])

    # Fat details
    fat_details = html.Div([
        html.P(f"Fat: {json_entry.get('fat', 0)}g", style={'color': 'black'}),
        html.P(f"Saturated Fat: {json_entry.get('saturated_fat', 0)}g", style={'color': 'grey'}),
        html.P(f"Unsaturated Fat: {json_entry.get('unsaturated_fat', 0)}g", style={'color': 'grey'}),
    ])

    # Protein details
    protein_details = html.Div([
        # Essential Amino Acids
        html.P(f"Essential Amino Acids: {sum([json_entry.get(aa, 0) for aa in ['histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 'tryptophan', 'valine']])}g", style={'color': 'black'}),
        html.P(f"Histidine: {json_entry.get('histidine', 0)}g", style={'color': 'grey'}),
        html.P(f"Isoleucine: {json_entry.get('isoleucine', 0)}g", style={'color': 'grey'}),
        html.P(f"Leucine: {json_entry.get('leucine', 0)}g", style={'color': 'grey'}),
        html.P(f"Lysine: {json_entry.get('lysine', 0)}g", style={'color': 'grey'}),
        html.P(f"Methionine: {json_entry.get('methionine', 0)}g", style={'color': 'grey'}),
        html.P(f"Phenylalanine: {json_entry.get('phenylalanine', 0)}g", style={'color': 'grey'}),
        html.P(f"Threonine: {json_entry.get('threonine', 0)}g", style={'color': 'grey'}),
        html.P(f"Tryptophan: {json_entry.get('tryptophan', 0)}g", style={'color': 'grey'}),
        html.P(f"Valine: {json_entry.get('valine', 0)}g", style={'color': 'grey'}),
        
        # Conditionally Essential Amino Acids
        html.P(f"Conditionally Essential Amino Acids: {sum([json_entry.get(aa, 0) for aa in ['arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine']])}g", style={'color': 'black'}),
        html.P(f"Arginine: {json_entry.get('arginine', 0)}g", style={'color': 'grey'}),
        html.P(f"Cysteine: {json_entry.get('cysteine', 0)}g", style={'color': 'grey'}),
        html.P(f"Glutamine: {json_entry.get('glutamine', 0)}g", style={'color': 'grey'}),
        html.P(f"Glycine: {json_entry.get('glycine', 0)}g", style={'color': 'grey'}),
        html.P(f"Proline: {json_entry.get('proline', 0)}g", style={'color': 'grey'}),
        html.P(f"Tyrosine: {json_entry.get('tyrosine', 0)}g", style={'color': 'grey'}),

        # Nonessential Amino Acids
        html.P(f"Nonessential Amino Acids: {sum([json_entry.get(aa, 0) for aa in ['alanine', 'aspartic acid', 'asparagine', 'glutamic acid', 'serine', 'selenocysteine', 'pyrrolysine']])}g", style={'color': 'black'}),
        html.P(f"Alanine: {json_entry.get('alanine', 0)}g", style={'color': 'grey'}),
        html.P(f"Aspartic Acid: {json_entry.get('aspartic acid', 0)}g", style={'color': 'grey'}),
        html.P(f"Asparagine: {json_entry.get('asparagine', 0)}g", style={'color': 'grey'}),
        html.P(f"Glutamic Acid: {json_entry.get('glutamic acid', 0)}g", style={'color': 'grey'}),
        html.P(f"Serine: {json_entry.get('serine', 0)}g", style={'color': 'grey'}),
        html.P(f"Selenocysteine: {json_entry.get('selenocysteine', 0)}g", style={'color': 'grey'}),
        html.P(f"Pyrrolysine: {json_entry.get('pyrrolysine', 0)}g", style={'color': 'grey'}),
    ])


    # Define the layout
    layout = html.Div([

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(json_entry.get('name', ''), style={'fontSize': '22px', 'textAlign': 'center'}),
                    html.P(f"{json_entry.get('calories', 0)} kcal", style={'fontSize': '24px', 'textAlign': 'center'}),
                    html.H5(meal_type, style={'textAlign': 'center', 'paddingBottom': '10px'}),
                ]),
            ], width=12),
        ], style={'padding': '10px'}),

    # Circular progress bars for Calories, Glycemic Index, Carbs, Protein, and Fat
    dbc.Row([
        dbc.Col([calories_circle], width=12, style={'textAlign': 'center', 'paddingBottom': '10px'}),
        
        # Glycemic Index below the Calories circle
        dbc.Col([
            html.P(f"Glycemic Index: {json_entry.get('glycemic_index', 'N/A')}", 
                style={'fontSize': '20px', 'textAlign': 'center', 'marginBottom': '20px'})
        ], width=12),
        
        # Carbs, Protein, and Fat circles
        dbc.Col([
            html.Div([
                carbs_circle, 
                protein_circle, 
                fat_circle
            ], style={'display': 'flex', 'justify-content': 'space-around'}),
        ], width=12),
    ]),

        # Three columns for additional information
        dbc.Row([
            dbc.Col([carbs_details], width=4),
            dbc.Col([protein_details], width=4),
            dbc.Col([fat_details], width=4),
        ]),

    ], style={'padding': '10px'})

    return layout
