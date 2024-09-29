# You've specified "FROM ubuntu:latest" and "FROM python:3.11", which are two different base images.
# Since you're using Python 3.11 for your project, let's consolidate to a single base image.
FROM python:3.10-slim

# The WORKDIR was correctly set to "/code", which is a common convention.
WORKDIR /code

# Combine system package updates, installations, and clean-up to reduce image layers and size.
# Besides ImageMagick, the 'libde265-dev' and 'libheif-dev' packages are installed for the 'pyheif' Python library.
# 'gcc' and 'g++' are included in the 'build-essential' package, which are required for Python library compilations.
# Install Python and ImageMagick
RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    libde265-dev \
    libheif-dev \
    build-essential \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copying the Python requirements file into the image first is a more cache-friendly approach for Docker builds.
COPY ./requirements.txt /code/

# Utilize the "--no-cache-dir" option to prevent Python package builds from being cached, useful for keeping the image size down.
# The `-v` (verbose) flag can be omitted for a cleaner log, unless needed for debugging.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set the path for the Google Cloud credentials inside the container
ENV GOOGLE_APPLICATION_CREDENTIALS="/code/dash-health-2024-4b0190c40044.json"

# Set environment variables # add ENV OPENAI_API_KEY;  ENV SUPABASE_URL; ENV SUPABASE_KEY

# Copy the rest of your project's files into the container.
COPY . /code/

# Set up the default port for the container. Adapt it to the port your Dash app actually uses (e.g., 8050 for a default Dash deployment).
EXPOSE 8080

# You do not need to redefine the world environment variable here, unless it serves a clear function in your application.
# This "ENV" instruction was removed for cleanup. You can add your OpenAI API Key or any other keys here as needed but ensure to do so securely.

# Startup command for your application. This assumes your project runs via `app.py` file. Adjust as needed.
# CMD ["python", "app.py"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:server"]
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:server"]
