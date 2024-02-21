import pandas as pd
import os
import glob
import fitparse
import ipywidgets as widgets
from IPython.display import display

from tqdm import tqdm

class LoadFitFiles:
    """
    This class is for loading .fit files from a directory into dataframes using the fitparse library.
    """

    def __init__(self, directory, list_fit_files = None, fromSQL: bool = False):
        """
        Initialize the LoadFitFiles class.

        Parameters:
            directory (str): The directory where the .fit files are stored.
        """
        self.directory = directory
        self.df_subset = None
        self.list_fit_files = list_fit_files
        self.fromSQL = fromSQL

    @staticmethod
    def load_fit_file(file_path):
        """
        Load a .fit file using fitparse library.

        Parameters:
            file_path (str): Path to the .fit file.

        Returns:
            pd.DataFrame: A DataFrame with fit data.
        """
        fitfile = fitparse.FitFile(file_path)
        data = []
        # Iterate through all the messages in the fit file
        for dictionary in fitfile.messages:
            # Extract the values from each message and append to the data list
            values = dictionary.get_values()
            data.append(values)

        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(data)

        # Filter out columns with names that start with 'unknown'
        df = df.filter(regex=r'^(?!unknown)')

        # Obtain the sport from the sport column and add to the file name
        sport = next(item for item in df.sport.unique() if isinstance(item, str))
        df['file'] = sport + '_' + os.path.basename(file_path)

        return df

    def get_fit_data(self):
        """
        Load fit data from files in the specified directory.

        Parameters:
            single_file (bool): A flag to specify whether to return data from a single file.

        Returns:
            pd.DataFrame: A DataFrame containing the fit data.
        """

        # read all files
        fit_files_list = self.list_fit_files or glob.glob(self.directory + "/*.fit")
        if not fit_files_list:
            raise ValueError("No .fit files found in the specified directory")

        df_all_fits = pd.DataFrame()
        for fit_file in fit_files_list:
            # load the data from fit file into dataframe
            df = self.load_fit_file(fit_file)
            # combine all dataframes
            df_all_fits = pd.concat([df_all_fits, df])

        # Convert the start_time column to datetime
        df_all_fits['timestamp'] = pd.to_datetime(df_all_fits['timestamp'])

        # Calculate elapsed time in seconds since the start of the set
        df_all_fits['elapsed_time'] = (df_all_fits['timestamp'] - df_all_fits['timestamp'].min()).dt.total_seconds()

        return df_all_fits


    def dropdown_selection(self, df_all_fits):
        """
        Initialize a dropdown menu that allows the user to select a file name from the DataFrame.
        Filter the DataFrame based on the selected file name and store it in an instance variable.

        Parameters:
            df_all_fits (pd.DataFrame): DataFrame to select files from.
        """

        # Get unique file names from the DataFrame
        unique_files = df_all_fits['file'].unique()

        # Create a dropdown menu with unique file names
        dropdown = widgets.Dropdown(options=unique_files)

        # Display the dropdown menu
        display(dropdown)

        # Wait for user interaction
        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                # When user selects a file name, filter the DataFrame
                self.df_subset = df_all_fits[df_all_fits['file'] == change['new']]

        dropdown.observe(on_change)