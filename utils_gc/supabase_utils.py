import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("Supabase URL and KEY must be set in environment variables.")
    supabase: Client = create_client(url, key)
    return supabase



def insert_nutrition_data(supabase_client, table_name, data):


    # (Assuming you know your table's schema and columns, you can list them here)
    # (Assuming you know your table's schema and columns, you can list them here)
    valid_columns = [
        'id', 'name', 'username', 'meal_type', 'date', 'created_at', 'llm_output', 'prompt', 'description', 'glycemic_index', 'weight', 'weight_original','calories', 'fat', 'carbohydrates', 'protein', 
        'fiber', 'triglycerides','saturated_fat', 'unsaturated_fat', 'sugar', 'fructose', 'galactose', 'lactose','glucose',
        'soluble_fiber', 'insoluble_fiber', 'sterols', 'phospholipids','oligosaccharides', 'polysaccharides',
        # Essential Amino Acids
        'histidine', 'isoleucine', 'leucine', 'lysine', 'methionine', 'phenylalanine', 'threonine', 
        'tryptophan', 'valine', 
        # Conditionally Essential Amino Acids
        'arginine', 'cysteine', 'glutamine', 'glycine', 'proline', 'tyrosine', 
        # Nonessential Amino Acids
        'alanine', 'aspartic_acid', 'asparagine', 'glutamic_acid', 'serine', 'selenocysteine', 
        'pyrrolysine',
        #minerals
        'iron', 'magnesium', 'zinc', 'calcium', 'potassium', 'sodium',
            
                ]


    # Step 2: Filter the JSON data to include only valid columns
    filtered_data = {key: value for key, value in data.items() if key in valid_columns}
    print(filtered_data)
    print('TYPE CREATED AT', type(filtered_data['created_at']))
    response = supabase_client.table(table_name).insert(filtered_data).execute()
    # Correct handling of the response
    if response.data:  # Directly access 'data' attribute from the response
        print("Row inserted successfully:", response.data)
        return True
    else:
        print(f"Error inserting row: {response}")
        return False
