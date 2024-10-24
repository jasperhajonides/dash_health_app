# utils/gcp_utils.py
import os
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Path to your service account key file
# CREDENTIALS_FILE = '/Users/jasperhajonides/Documents/Projects/website/dash_health_app/dash-health-2024-b00c57d8f7b9.json'

# Use the environment variable for the credentials file
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# If the environment variable is not set, print an error.
if not CREDENTIALS_FILE:
    ValueError("Could not find a Google Credential File (.json), please correct its path.")


# Create credentials object from service account key file
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)

# Initialize the storage client with credentials
client = storage.Client(credentials=credentials)

# Function to upload the file to Google Cloud Storage
def upload_image_to_gcs(bucket_name, file_name, file_content):
    try:
        print(f'Using bucket name: "{bucket_name}"')

        bucket = client.get_bucket(bucket_name)  # Ensures the bucket exists
        blob = bucket.blob(file_name)

        # Upload the file content as bytes
        blob.upload_from_string(file_content, content_type='image/png')
        print(f'File "{file_name}" uploaded successfully.')

    except Exception as e:
        print(f'Error uploading file to GCS: {str(e)}')

# Function to retrieve the image URL from Google Cloud Storage
def get_image_url_from_gcs(bucket_name, file_name):
    try:
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Generate a signed URL valid for one hour
        url = blob.generate_signed_url(version="v4", expiration=3600)
        print(f'Generated signed URL for file "{file_name}": {url}')
        return url
    except Exception as e:
        print(f'Error generating signed URL for file "{file_name}": {str(e)}')
        return None

# Function to list the files in the Google Cloud Storage bucket
def list_files_in_gcs(bucket_name):
    try:
        bucket = client.get_bucket(bucket_name)
        
        # List all blobs in the bucket
        blobs = bucket.list_blobs()
        file_list = [blob.name for blob in blobs]
        
        print("Files in Google Cloud Storage bucket:")
        for file_name in file_list:
            print(file_name)
        
        return file_list
    except Exception as e:
        print(f"Error listing files in GCS: {str(e)}")
        return []
    
import datetime
import pytz

def generate_id_and_custom_timestamp(selected_date=None):
    # Get the current time in UTC
    now_utc = datetime.datetime.now(pytz.utc)
    
    if selected_date:
        try:
            # Parse the selected date
            date_part = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Use the current time
            time_part = now_utc.time()
            # Combine date and time
            custom_datetime = datetime.datetime.combine(date_part, time_part)
            # Set timezone to UTC
            custom_datetime = custom_datetime.replace(tzinfo=pytz.utc)
        except ValueError:
            raise ValueError("Please provide the date in 'YYYY-MM-DD' format.")
    else:
        custom_datetime = now_utc
    
    # Generate id_str in 'yyyymmddHHMMSS' format
    id_str = custom_datetime.strftime('%Y%m%d%H%M%S')
    
    # Format timestamp with timezone
    custom_timestamp = custom_datetime.isoformat()
    
    return id_str, custom_timestamp
