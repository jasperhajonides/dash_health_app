import os
import io
from datetime import datetime
from PIL import Image
import base64


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


# Function to resize and crop the image
def resize_and_crop_image(image_data, pixels_size = 512):
    # Open the image and determine smaller side
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size
    new_size = min(width, height)

    # Resize with the smaller side being 512 pixels
    ratio = pixels_size / new_size
    new_width, new_height = int(ratio * width), int(ratio * height)
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crop to a 512x512 square
    left = (new_width - pixels_size) / 2
    top = (new_height - pixels_size) / 2
    right = (new_width + pixels_size) / 2
    bottom = (new_height + pixels_size) / 2
    image = image.crop((left, top, right, bottom))

    # Convert the image to binary data for storage
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return buffered.getvalue()
