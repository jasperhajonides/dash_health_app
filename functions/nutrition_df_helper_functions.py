from datetime import datetime
import pandas as pd

def load_and_filter_df(selected_date_input):
    """
    Load data from a CSV file and filter it based on a selected date.

    This function automatically handles the selected date whether it's
    provided as a datetime object or a string. It filters the DataFrame
    to include only rows that match the selected date.

    Parameters:
    - selected_date_input: The selected date, can be a datetime object or a string in the format 'YYYY-MM-DD'.

    Returns:
    - filtered_df: A DataFrame filtered to include only the rows from the selected date.
    """
    # Load the DataFrame from a CSV file
    df = pd.read_csv('data/nutrition_entries.csv')

    # Ensure the 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Check the type of the input date and convert it to a datetime object if necessary
    if isinstance(selected_date_input, str):
        # If the input is a string, parse it to a datetime object
        selected_date = datetime.strptime(selected_date_input, '%Y-%m-%d')
    elif isinstance(selected_date_input, datetime):
        # If the input is already a datetime object, use it directly
        selected_date = selected_date_input
    else:
        raise ValueError("The selected date must be a string in the format 'YYYY-MM-DD' or a datetime object.")

    # Filter the DataFrame for entries that match the selected date
    filtered_df = df[df['date'].dt.date == selected_date.date()]

    # Debugging print statement to check the number of entries for the selected date

    return filtered_df