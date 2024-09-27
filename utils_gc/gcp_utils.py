# utils/gcp_utils.py
import os
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime

# Path to your service account key file
# CREDENTIALS_FILE = '/Users/jasperhajonides/Documents/Projects/website/dash_health_app/dash-health-2024-b00c57d8f7b9.json'

# Use the environment variable for the credentials file
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# If the environment variable is not set, fall back to a local path
if not CREDENTIALS_FILE:
    CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '../dash-health-2024-b00c57d8f7b9.json')


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
    

def generate_id():
    now = datetime.now()
    id_str = now.strftime('%y%m%d%H%M%S')
    return id_str

