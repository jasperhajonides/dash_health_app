import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pytz
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils_gc.supabase_utils import get_supabase_client
from pages.nutrition_page_parts.log_entries_mobile import create_todays_entries_layout

def register_visualisation_callbacks(app):
    """
    Registers all callbacks related to visualizations on the main page.
    """
    @app.callback(
        [
            Output('calorie-history-data', 'data'),
            Output('cumulative-calories-data', 'data')
        ],
        Input('interval-startup', 'n_intervals'),
        [
            State('session-store', 'data'),
            State('selected-date-store', 'data')
        ],
        prevent_initial_call=True
    )
    def preload_data(n_intervals, session_data, selected_date):
        """
        Preloads necessary data for visualizations when the app starts.
        Fetches today's entries and past 14 days data.
        """
        if not session_data or 'username' not in session_data:
            return None, None, None

        username = session_data['username']

        # Fetch past 14 days data (used for both calorie history and cumulative calories)
        past_14_days_data = fetch_past_14_days_data(username, selected_date)

        # Use the same data for both calorie history and cumulative calories
        return past_14_days_data, past_14_days_data

    # Callback to update the active button state
    @app.callback(
        Output('active-button', 'data'),
        [
            Input('btn-todays-entries', 'n_clicks'),
            Input('btn-calorie-history', 'n_clicks'),
            Input('btn-cumulative-calories', 'n_clicks'),
        ],
        State('active-button', 'data'),
    )
    def update_active_button(n1, n2, n3, active_button):
        """
        Updates the 'active-button' store based on which button was clicked.
        """
        ctx = dash.callback_context
        if not ctx.triggered:
            # No button has been clicked yet
            return active_button
        else:
            # Identify which button was clicked
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            return button_id

    # Callback to update button styles based on the active button
    @app.callback(
        [
            Output('btn-todays-entries', 'color'),
            Output('btn-todays-entries', 'outline'),
            Output('btn-calorie-history', 'color'),
            Output('btn-calorie-history', 'outline'),
            Output('btn-cumulative-calories', 'color'),
            Output('btn-cumulative-calories', 'outline'),
        ],
        Input('active-button', 'data'),
    )
    def update_button_styles(active_button):
        """
        Updates the styles of the buttons to reflect which one is active.
        """
        buttons = ['btn-todays-entries', 'btn-calorie-history', 'btn-cumulative-calories']
        colors = {}
        for btn in buttons:
            if btn == active_button:
                # Active button: solid primary color
                colors[btn] = ('primary', False)
            else:
                # Inactive buttons: outlined secondary color
                colors[btn] = ('secondary', True)
        return (
            colors['btn-todays-entries'][0], colors['btn-todays-entries'][1],
            colors['btn-calorie-history'][0], colors['btn-calorie-history'][1],
            colors['btn-cumulative-calories'][0], colors['btn-cumulative-calories'][1],
        )

    # Callback to display content based on the active button
    @app.callback(
        Output('content-container', 'children'),
        Input('active-button', 'data'),
        [
            State('session-store', 'data'),
            State('selected-date-store', 'data'),
            State('todays_nutritional_data', 'data'),  # Updated store ID
            State('calorie-history-data', 'data'),
            State('cumulative-calories-data', 'data')
        ],
        prevent_initial_call=True
    )
    def display_content(active_button, session_data, selected_date,
                        todays_nutritional_data, calorie_history_data, cumulative_calories_data):
        """
        Displays the appropriate content based on the active button.
        Uses preloaded data for faster responsiveness.
        """
        if not session_data or 'username' not in session_data:
            return html.Div("Please log in to view content.")

        if active_button == 'btn-todays-entries':
            return create_todays_entries_layout(todays_nutritional_data)
        elif active_button == 'btn-calorie-history':
            return display_calorie_history(calorie_history_data, selected_date)
        elif active_button == 'btn-cumulative-calories':
            return display_cumulative_calories(cumulative_calories_data, selected_date)
        else:
            return html.Div("Select an option to view content.")


    # Additional callbacks and functions can be added here for new buttons and visualizations

def fetch_todays_entries(username, selected_date):
    """
    Fetches today's entries from the database for the given username and selected date.
    """
    # Convert selected date to datetime object
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Define start and end datetime for the selected date
    start_datetime = datetime.datetime.combine(selected_date_obj, datetime.datetime.min.time())
    end_datetime = datetime.datetime.combine(selected_date_obj, datetime.datetime.max.time())

    # Convert to UTC timestamps for Supabase query
    local_tz = pytz.timezone('Europe/London')  # Adjust timezone as needed
    start_of_day_local = local_tz.localize(start_datetime)
    end_of_day_local = local_tz.localize(end_datetime)
    start_utc = start_of_day_local.astimezone(pytz.utc).isoformat()
    end_utc = end_of_day_local.astimezone(pytz.utc).isoformat()

    # Query Supabase for entries within the date range
    supabase_client = get_supabase_client()
    try:
        response = supabase_client.table('sandbox_nutrition')\
            .select("*")\
            .eq('username', username)\
            .gte('created_at', start_utc)\
            .lte('created_at', end_utc)\
            .execute()
        
        data = response.data
    except Exception as e:
        print(f"Error fetching today's data from Supabase: {str(e)}")
        data = []
    
    return data

def fetch_past_14_days_data(username, selected_date):
    """
    Fetches the past 14 days of data up to the selected date for the given username.
    """
    # Convert selected date to date object
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Define the date range for the past 14 days up to the selected date
    end_datetime = datetime.datetime.combine(selected_date_obj, datetime.datetime.max.time())
    start_datetime = end_datetime - datetime.timedelta(days=13)

    # Convert to UTC timestamps for Supabase query
    local_tz = pytz.timezone('Europe/London')  # Adjust timezone as needed
    start_of_day_local = local_tz.localize(start_datetime)
    end_of_day_local = local_tz.localize(end_datetime)
    start_utc = start_of_day_local.astimezone(pytz.utc).isoformat()
    end_utc = end_of_day_local.astimezone(pytz.utc).isoformat()

    # Query Supabase for entries within the date range
    supabase_client = get_supabase_client()
    try:
        response = supabase_client.table('sandbox_nutrition')\
            .select("*")\
            .eq('username', username)\
            .gte('created_at', start_utc)\
            .lte('created_at', end_utc)\
            .execute()
        
        data = response.data
    except Exception as e:
        print(f"Error fetching past 14 days data from Supabase: {str(e)}")
        data = []
    
    return data

def display_calorie_history(data, selected_date):
    """
    Generates a bar chart displaying calories over the past 14 days.
    """
    if not data:
        return html.Div("No data available.")

    # Prepare data
    df = pd.DataFrame(data)
    
    # Check if required columns exist
    required_columns = ['created_at', 'calories']
    if not all(col in df.columns for col in required_columns):
        return html.Div("Data missing required fields.")

    # Convert 'created_at' to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Drop rows with invalid 'created_at'
    df = df.dropna(subset=['created_at'])

    # Extract date part
    df['date'] = df['created_at'].dt.date

    # Convert 'calories' to numeric
    df['calories'] = pd.to_numeric(df['calories'], errors='coerce').fillna(0)

    # Aggregate calories per day
    df_daily = df.groupby('date')['calories'].sum().reset_index()

    # Create a complete list of dates for the past 14 days
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    start_date = selected_date_obj - datetime.timedelta(days=13)
    all_dates = [start_date + datetime.timedelta(days=i) for i in range(14)]
    df_daily_complete = pd.DataFrame({'date': all_dates})

    # Merge with the aggregated data to fill missing dates with zero
    df_daily_complete = df_daily_complete.merge(df_daily, on='date', how='left').fillna({'calories': 0})

    # Create bar chart
    fig = px.bar(
        df_daily_complete,
        x='date',
        y='calories',
        title='Calories Over the Past 14 Days',
        labels={'calories': 'Total Calories', 'date': 'Date'},
        color_discrete_sequence=['lightsalmon']
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Total Calories',
        xaxis_tickformat='%Y-%m-%d',
        xaxis_tickangle=45,
        bargap=0.2
    )
    fig.update_traces(marker_line_width=1, marker_line_color='black')

    return dcc.Graph(figure=fig)

def display_cumulative_calories(data, selected_date):
    """
    Generates a line chart displaying cumulative calories throughout the day over the past 14 days.
    """
    if not data:
        return html.Div("No data available.")

    # Prepare data
    df = pd.DataFrame(data)
    
    # Check if required columns exist
    required_columns = ['created_at', 'calories']
    if not all(col in df.columns for col in required_columns):
        return html.Div("Data missing required fields.")

    # Convert 'created_at' to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Drop rows with invalid 'created_at'
    df = df.dropna(subset=['created_at'])

    # Extract date and time
    df['date'] = df['created_at'].dt.date
    df['time'] = df['created_at'].dt.time

    # Convert 'calories' to numeric
    df['calories'] = pd.to_numeric(df['calories'], errors='coerce').fillna(0)

    # Sort data by date and time
    df = df.sort_values(['date', 'created_at'])

    # Calculate cumulative calories
    df['cumulative_calories'] = df.groupby('date')['calories'].cumsum()

    # Create a common time base (e.g., datetime objects on a dummy date)
    common_date = datetime.datetime(2000, 1, 1)
    df['time_of_day_dt'] = df['time'].apply(lambda x: datetime.datetime.combine(common_date, x))

    # Initialize figure
    fig = go.Figure()

    # Convert selected_date to date object
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Plot cumulative calories for each day
    unique_dates = df['date'].unique()
    for date in unique_dates:
        df_day = df[df['date'] == date].sort_values('created_at')
        if df_day.empty:
            continue

        # Plotting all previous days in gray
        if date != selected_date_obj:
            fig.add_trace(go.Scatter(
                x=df_day['time_of_day_dt'],
                y=df_day['cumulative_calories'],
                mode='lines',
                line=dict(width=1, color='gray'),
                name=date.strftime('%Y-%m-%d'),
                showlegend=False
            ))
        else:
            # Highlight selected day's data
            fig.add_trace(go.Scatter(
                x=df_day['time_of_day_dt'],
                y=df_day['cumulative_calories'],
                mode='lines',
                line=dict(width=3, color='blue'),
                name='Selected Day',
                hoverinfo='name+x+y'
            ))

    # Update layout
    fig.update_layout(
        title='Cumulative Calories Throughout the Day (Past 14 Days)',
        xaxis_title='Time of Day',
        yaxis_title='Cumulative Calories',
        xaxis=dict(
            tickformat='%H:%M',
            range=[common_date, common_date + datetime.timedelta(hours=24)],
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )

    return dcc.Graph(figure=fig)

# Additional visualization functions can be added below
# Each new visualization function should accept preloaded data and selected date as arguments
# For example:

# def display_new_visualization(data, selected_date):
#     """
#     Generates a new visualization based on the provided data and selected date.
#     """
#     # Implementation of the new visualization
#     pass  # Replace with actual code

# Similarly, you can add more buttons and their corresponding content generation functions
