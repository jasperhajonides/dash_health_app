# # user_data.py
# # import sqlite3
import csv
import os

# class UserData:
#     def __init__(self, user_id):
#         self.user_id = user_id
#         self.csv_file_path = './data/user_data.csv'
#         self.initialize_csv_file()
#         self.user_info = self.fetch_user_info()
#         self.user_profile = {}
#         self.nutritional_info = self.fetch_nutritional_info()
#         self.api_profile = self.fetch_api_profile()
    
#     def initialize_csv_file(self):
#         # Initialize CSV file with headers if it does not exist
#         if not os.path.exists(self.csv_file_path):
#             with open(self.csv_file_path, mode='w', newline='') as csv_file:
#                 fieldnames = ['user_id', 'user_info', 'nutritional_info', 'api_profile']
#                 writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#                 print("Initialized CSV file with headers as ", csv_file)
#                 writer.writeheader()


    
#     def fetch_user_info(self):
#         # Placeholder for database fetching logic
#         # In a real scenario, you would connect to your SQL database and fetch the user data
#         # For demonstration, we'll return a static dictionary
#         return {
#             "user_profile": {"name": "John Doe",
#                             "weight": 70, 
#                             "height": 175, 
#                             "dob": "1990-01-01",
#                             "location": "New York",
#                             "member_since": "2023-01-01"},
#             "activity_profile": {"sports": "Running, Cycling, Swimming", 'activity_level': 'medium'},  # kg
#         }
    
#     def fetch_api_profile(self):
#         # Placeholder for database fetching logic
#         # In a real scenario, you would connect to your SQL database and fetch the user data
#         # For demonstration, we'll return a static dictionary
#         return {
#             "api_profile": {"openai_api_key": "rr22*********xx",
#                             "text_quality_settings": "base", 
#                             "image_quality_settings": "base",},
#         }
    

#     def fetch_nutritional_info(self):
#         # Placeholder for nutritional info fetching logic
#         # This should ideally fetch data from a database or another persistent storage
#         return {
#             "daily_macros": {"Calories": "2000 kcal", "Protein": "150 g", "Carbs": "250 g", "Fats": "70 g"},
#             "vitamins": {"Vitamin A": "900 mcg", "Vitamin C": "90 mg"},
#             "amino_acids": {"Leucine": "42 mg"},
#             "minerals": {"Calcium": "1000 mg"},
#             "sugars_fibers": {"Sugar": "N/A", "Fiber": "N/A"},
#             "fats": {"Saturated Fat": "N/A", 
#                      "Unsaturated Fat": 20}
#         }
    
#     def get_nutritional_info(self):
#         return self.nutritional_info
    
#     def update_csv_user_data(self):
#         # Read all data from CSV to find the relevant user
#         rows = []
#         updated = False
#         with open(self.csv_file_path, mode='r', newline='') as csv_file:
#             reader = csv.DictReader(csv_file)
#             for row in reader:
#                 if row['user_id'] == self.user_id:
#                     row['user_info'] = str(self.user_info)
#                     row['nutritional_info'] = str(self.nutritional_info)
#                     row['api_profile'] = str(self.api_profile)
#                     updated = True
#                 rows.append(row)
        
#         if not updated:
#             # Append new user if not found
#             rows.append({
#                 'user_id': self.user_id,
#                 'user_info': str(self.user_info),
#                 'nutritional_info': str(self.nutritional_info),
#                 'api_profile': str(self.api_profile)
#             })
        
#         # Write updated data back to CSV
#         with open(self.csv_file_path, mode='w', newline='') as csv_file:
#             fieldnames = ['user_id', 'user_info', 'nutritional_info', 'api_profile']
#             writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(rows)


#     def update_user_info_bulk(self, updates):
#         # Updates should be a dictionary {field: new_value}
#         for field, value in updates.items():
#             if field in self.user_info:
#                 self.user_info[field] = value
#                 # Update logic for the database goes here
#                 print(f"Updated {field} to {value}")
#             else:
#                 print(f"Field {field} not recognized.")

#     def update_api_profile_bulk(self, updates):
#         # Updates should be a dictionary {field: new_value}
#         for field, value in updates.items():
#             if field in self.api_profile:
#                 self.api_profile[field] = value
#                 # Update logic for the database goes here
#                 print(f"Updated {field} to {value}")
#             else:
#                 print(f"Field {field} not recognized.")

#     def update_nutritional_info_bulk(self, updates):
#         # Updates should be a dictionary {category: {field: new_value}}
#         for category, category_updates in updates.items():
#             if category in self.nutritional_info:
#                 for field, value in category_updates.items():
#                     if field in self.nutritional_info[category]:
#                         self.nutritional_info[category][field] = value
#                         print(f"Updated {category} - {field} to {value}")
#                     else:
#                         print(f"Field {field} not recognized in {category}.")
#             else:
#                 print(f"Category {category} not recognized.")

#     def print_user_info(self):
#         print("User Info:", self.user_info)

#     def print_user_info(self):
#         print("API profile:", self.api_profile)

#     def print_nutrition_info(self):
#         print("Nutrition Info:", self.nutritional_info)
import csv
import os
import json

class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.csv_file_path = './data/user_data.csv'
        self.initialize_csv_file()
        self.user_profile = self.fetch_user_profile()  # Renamed for consistency
        self.nutritional_info = self.fetch_nutritional_info()
        self.api_profile = self.fetch_api_profile()

    def initialize_csv_file(self):
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='') as csv_file:
                fieldnames = ['user_id', 'user_profile', 'nutritional_info', 'api_profile']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

    def fetch_user_profile(self):
        return self.fetch_data_from_csv('user_profile')

    def fetch_api_profile(self):
        return self.fetch_data_from_csv('api_profile')

    def fetch_nutritional_info(self):
        return self.fetch_data_from_csv('nutritional_info')

    def fetch_data_from_csv(self, data_type):
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['user_id'] == self.user_id:
                    if row[data_type]:
                        return json.loads(row[data_type])
            return {}

    def update_csv_user_data(self):
        rows = []
        updated = False
        with open(self.csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['user_id'] == self.user_id:
                    row['user_profile'] = json.dumps(self.user_profile)
                    row['nutritional_info'] = json.dumps(self.nutritional_info)
                    row['api_profile'] = json.dumps(self.api_profile)
                    updated = True
                    print('going to update user settings', self.user_profile)
                rows.append(row)

        if not updated:
            rows.append({
                'user_id': self.user_id,
                'user_profile': json.dumps(self.user_profile),
                'nutritional_info': json.dumps(self.nutritional_info),
                'api_profile': json.dumps(self.api_profile)
            })

        with open(self.csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ['user_id', 'user_profile', 'nutritional_info', 'api_profile']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # Ensure the update methods are adapted to reflect these changes.
