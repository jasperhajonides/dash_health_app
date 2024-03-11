# user_data.py
import sqlite3

class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_info = self.fetch_user_info()
        self.nutritional_info = self.fetch_nutritional_info()


    
    def fetch_user_info(self):
        # Placeholder for database fetching logic
        # In a real scenario, you would connect to your SQL database and fetch the user data
        # For demonstration, we'll return a static dictionary
        return {
            "user_profile": {"name": "John Doe",
                            "weight": 70, 
                            "height": 175, 
                            "dob": "1990-01-01",
                            "location": "New York",
                            "member_since": "2023-01-01"},
            "activity_profile": {"sports": "Running, Cycling, Swimming", 'activity_level': 3},  # kg
        }
    
    def fetch_nutritional_info(self):
        # Placeholder for nutritional info fetching logic
        # This should ideally fetch data from a database or another persistent storage
        return {
            "daily_macros": {"Calories": "2000 kcal", "Protein": "150 g", "Carbs": "250 g", "Fats": "70 g"},
            "vitamins": {"Vitamin A": "900 mcg", "Vitamin C": "90 mg"},
            "amino_acids": {"Leucine": "42 mg"},
            "minerals": {"Calcium": "1000 mg"},
            "sugars_fibers": {"Sugar": "N/A", "Fiber": "N/A"},
            "fats": {"Saturated Fat": "N/A", 
                     "Unsaturated Fat": 20}
        }
    
    def get_nutritional_info(self):
        return self.nutritional_info
    
    def update_user_info_bulk(self, updates):
        # Updates should be a dictionary {field: new_value}
        for field, value in updates.items():
            if field in self.user_info:
                self.user_info[field] = value
                # Update logic for the database goes here
                print(f"Updated {field} to {value}")
            else:
                print(f"Field {field} not recognized.")

    def update_nutritional_info_bulk(self, updates):
        # Updates should be a dictionary {category: {field: new_value}}
        for category, category_updates in updates.items():
            if category in self.nutritional_info:
                for field, value in category_updates.items():
                    if field in self.nutritional_info[category]:
                        self.nutritional_info[category][field] = value
                        print(f"Updated {category} - {field} to {value}")
                    else:
                        print(f"Field {field} not recognized in {category}.")
            else:
                print(f"Category {category} not recognized.")

    def print_user_info(self):
        print("User Info:", self.user_info)

    def print_nutrition_info(self):
        print("Nutrition Info:", self.nutritional_info)
