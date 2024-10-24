import random

def generate_colors(num_colors):
    """ 
    when drawing sub-bars for the current item layout we need a variability of colours.
     This function creates these colours.
      
    """
    colors = []
    for _ in range(num_colors):
        # Generate a random colour in hex format
        colors.append('#%06X' % random.randint(0, 0xFFFFFF))
    return colors