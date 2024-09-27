from PIL import Image, ExifTags
import base64
import io

def process_image(image_contents):
    """Process the uploaded image: auto-rotate, crop to square, resize to 512x512, and return base64."""
    # Extract base64 image content
    content_type, content_string = image_contents.split(',')
    decoded_image = base64.b64decode(content_string)
    
    # Open the image
    image = Image.open(io.BytesIO(decoded_image))

    # Correct orientation based on EXIF data (for iOS devices)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()

        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Handle case when EXIF data is not available
        pass

    # Crop the image to a square centered on the image
    width, height = image.size
    new_edge = min(width, height)
    left = (width - new_edge) // 2
    top = (height - new_edge) // 2
    right = (width + new_edge) // 2
    bottom = (height + new_edge) // 2
    image = image.crop((left, top, right, bottom))

    # Resize the image to 512x512 pixels
    image = image.resize((512, 512))

    # Convert the image back to base64 for display
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Return the base64-encoded image string with the appropriate prefix
    return f"data:image/png;base64,{img_str}", img_str  # Note: Return the image data without re-encoding
