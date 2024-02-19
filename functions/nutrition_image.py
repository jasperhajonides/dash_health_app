import os
import io
import re
from datetime import datetime
from PIL import Image
import base64
import subprocess
import tempfile
from icecream import ic

def convert_heic_to_jpeg(heic_path, jpeg_path):
    subprocess.run(["convert", heic_path, jpeg_path], check=True)

def is_heic_image(image_data):
    # HEIC files typically contain the string 'ftypheic' somewhere in their first few kilobytes.
    # This is a very rough heuristic and may not work for all HEIC files.
    return b'ftypheic' in image_data[:12] or b'ftypheix' in image_data[:12] or b'ftypmif1' in image_data[:12] or b'ftypmsf1' in image_data[:12]


def save_image(stored_image_data, file_name):
    if (file_name is None) or (len(file_name) <= 1):
        file_name = 'template'
            # Decode the base64 string
    image_data = base64.b64decode(stored_image_data)

    # Create the filename
    today_str = datetime.now().strftime('%Y%m%d')
    item_name = file_name.replace(' ', '_')
    filename = f"{today_str}_{item_name}.png"

    # Define the path to the images folder relative to the root of the project
    script_dir = os.path.dirname(__file__)  # Directory of the current script
    root_dir = os.path.dirname(script_dir)  # Root directory of the project
    images_folder = os.path.join(root_dir, 'assets', 'images')

    # Create the directory if it doesn't exist
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # Full path for the image
    image_path = os.path.join(images_folder, filename)

    # Save the image
    with open(image_path, 'wb') as f:
        f.write(image_data)

    print(f"Image saved as {filename}")



def resize_and_crop_image(base64_images, pixels_size=512):

    # Check if base64_images is a list and extract the first element if true
    if isinstance(base64_images, list):
        if not base64_images:  # Check if the list is empty
            return None  # Or handle this case as appropriate for your application
        base64_image = base64_images[0]  # Use the first image
    else:
        # If base64_images is not a list, assume it's a single image string
        base64_image = base64_images


    # Split the string on the comma to remove the data URI scheme
    # and only keep the actual base64-encoded data.
    if ',' in base64_image:
        _, encoded_image = base64_image.split(',', 1)
    else:
        # If there's no comma found, assume the whole string is the encoded image
        encoded_image = base64_image
        
    image_data = base64.b64decode(encoded_image)

    try:
        image = Image.open(io.BytesIO(image_data))
        # If the format is not directly supported by PIL (Pillow), attempt HEIC detection.
        if image.format not in ['PNG', 'JPEG', 'JPG'] and not is_heic_image(image_data):
            return None, "Unsupported image format. Only PNG, JPG, JPEG, and HEIC are supported."
    except IOError:
        # Attempt to handle HEIC if Pillow fails to recognize the image
        if is_heic_image(image_data):
            with tempfile.NamedTemporaryFile(suffix='.heic', delete=False) as heic_file:
                heic_file.write(image_data)
                heic_file_path = heic_file.name

            jpeg_file_path = tempfile.mktemp(suffix='.jpeg')
            convert_heic_to_jpeg(heic_file_path, jpeg_file_path)

            with open(jpeg_file_path, 'rb') as jpeg_file:
                image_data = jpeg_file.read()

            # Clean up the temporary files
            os.remove(heic_file_path)
            os.remove(jpeg_file_path)
            
            image = Image.open(io.BytesIO(image_data))
        else:
            return None, "Unsupported image format. Only PNG, JPG, JPEG, and HEIC are supported."


    # Pillow can identify the format of the image
    image_format = image.format

    # Proceed with resizing and cropping
    width, height = image.size
    new_size = min(width, height)
    ratio = pixels_size / new_size
    new_width, new_height = int(ratio * width), int(ratio * height)
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - pixels_size) / 2
    top = (new_height - pixels_size) / 2
    right = (new_width + pixels_size) / 2
    bottom = (new_height + pixels_size) / 2
    image = image.crop((left, top, right, bottom))

    # Convert the image to RGB mode if it's in a different mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert the processed image back to binary data for storage
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")  # Save as JPEG or use image_format if appropriate
    processed_image_data = base64.b64encode(buffered.getvalue()).decode()

    # Return the processed image data and the original image format
    return processed_image_data, image_format