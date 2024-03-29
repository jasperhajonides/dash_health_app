# # user_data.py
# # import sqlite3

import csv
import os
import json

class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.csv_file_path = './data/user_data.csv'
        self.initialize_csv_file()
        self.user_profile = self.fetch_user_profile()  # Renamed for consistency
        print('user profile', self.user_profile)
        self.nutritional_info = self.fetch_nutritional_info()
        self.api_profile = self.fetch_api_profile()
        print('api_profile', self.api_profile)


                    
    def fetch_data_from_csv(self, prefix):
        data_selection = {}
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['user_id'] == self.user_id and row['attribute'].startswith(prefix):
                    # Remove the prefix from the attribute name and any potential additional dot for clarity
                    # Split the attribute by '.' and take the last part, which should be the actual attribute name
                    attribute_name = row['attribute'].split('.')[-1]
                    # Now, attribute_name is without the 'user-info.' or other prefixes
                    data_selection[attribute_name] = row['value']
        return data_selection

                
    def fetch_data(self):
        data = {}
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['user_id'] == self.user_id:
                    attribute_category, attribute_name = row['attribute'].split('.', 1)
                    if attribute_category in ['user_info', 'nutritional_info', 'api_profile']:
                        if attribute_category not in data:
                            data[attribute_category] = {}
                        data[attribute_category][attribute_name] = row['value']  # Assume no units for simplicity
        return data


    def fetch_user_profile(self):
        return self.fetch_data_from_csv('user-info')

    def fetch_api_profile(self):
        return self.fetch_data_from_csv('api-settings')

    def fetch_nutritional_info(self):
        return self.fetch_data_from_csv('nutritional-info')

    def initialize_csv_file(self):
        # Initialize CSV file with headers if it does not exist
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='') as csv_file:
                fieldnames = ['user_id', 'attribute', 'value', 'unit']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

    # def fetch_data(self):
    #     # Fetch and organize user data from CSV
    #     data = {'user_info': {}, 'nutritional_info': {}, 'api_profile': {}}
    #     with open(self.csv_file_path, mode='r', newline='') as csv_file:
    #         reader = csv.DictReader(csv_file)
    #         for row in reader:
    #             if row['user_id'] == self.user_id:
    #                 # Determine which category the attribute belongs to
    #                 if row['attribute'].startswith('user_info_'):
    #                     data_category = 'user_info'
    #                 elif row['attribute'].startswith('nutritional_info_'):
    #                     data_category = 'nutritional_info'
    #                 elif row['attribute'].startswith('api_profile_'):
    #                     data_category = 'api_profile'
    #                 else:
    #                     continue  # Skip unrecognized categories

    #                 # Strip category prefix and store data
    #                 attribute = row['attribute'].split('_', 1)[1]
    #                 data[data_category][attribute] = row['value'] + (' ' + row['unit'] if row['unit'] else '')

    #     return data
    
    def process_updates(self, updates):
        # Read the current data
        existing_data = []
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Exclude rows related to the current user_id to replace them with new updates
                if row['user_id'] != self.user_id:
                    existing_data.append(row)

        # Add the new updates for the current user_id
        for update in updates:
            # Assuming update is a tuple or list: (user_id, attribute, value, unit)
            new_row = {
                'user_id': update[0],
                'attribute': update[1],
                'value': update[2],
                'unit': update[3]  # Ensure unit handling matches your data structure
            }
            existing_data.append(new_row)

        # Write the updated data back to the CSV
        with open(self.csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ['user_id', 'attribute', 'value', 'unit']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data)

    def update_csv_user_data(self, updates):
        # This method needs to be significantly rewritten to accommodate individual attribute updates
        # For demonstration, let's assume updates is a dictionary of dictionaries with the same structure as fetch_data output
        # Example: updates = {'user_profile': {'name': 'Jane Doe', 'age': 30}, 'nutritional_info': {'calories': '2000'}, ...}

        # Read the current data, exclude rows for the current user_id
        rows = []
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['user_id'] != self.user_id:
                    rows.append(row)

        # Append updated data for the current user_id
        for category, attributes in updates.items():
            for attribute, value in attributes.items():
                rows.append({
                    'user_id': self.user_id,
                    'attribute': f'{category}_{attribute}',
                    'value': str(value) if not isinstance(value, tuple) else value[0],
                    'unit': '' if not isinstance(value, tuple) else value[1]
                })

        # Write updated data back to CSV
        with open(self.csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ['user_id', 'attribute', 'value', 'unit']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # Ensure the update methods are adapted to reflect these changes.
