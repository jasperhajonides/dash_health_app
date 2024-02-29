[![pipeline status](https://gitlab.com/jasperhajonides/dash_health_app/badges/main/pipeline.svg)](https://gitlab.com/jasperhajonides/dash_health_app/-/pipelines)

[![coverage report](https://gitlab.com/jasperhajonides/dash_health_app/badges/main/coverage.svg)](https://gitlab.com/jasperhajonides/dash_health_app/-/commits/main)


# Dash Health App

## Project Overview

Logging and analysing nutritional, exercise, and physiological data. 

## Approach

A dash frontend built to enable users to interactively view and edit their data. 

1. **Nutritional information**: We use OpenAI api's to estimate nutritional content from images or text input in conjunction with other nutritional databases.

2. **Exercise data**: .fit files are obtained from Garmin and logged into a local database. We then extract trends within and between exercises.

3. **Physiological metrics**: t.b.d.

The dashboard is designed to be intuitive and insightful

## How to Run the Code

To run the application, follow these steps:

1. **Clone the Repository**:
    ```
   git clone [repository-url]
    ```

2. **Build the Docker Image**:
    ```
   docker build -t dash_health_app  -f Dockerfile .
    ```

3. **Run the Docker Container**:
    ```
   docker run -v .:/code -p 80:8050 dash_health_app
    ```

4. **Access the Dashboard**:
   Open your web browser and navigate to `http://0.0.0.0:80/`. Follow the on-screen instructions to proceed.

## File Structure

Below is the basic structure of the project:

```
dash_health_app/
│
├── app/               # Application code
│   ├── data/          # uploaded .pdf files.
│   ├── functions/     # Function modules
│   │   ├── llm_output_functions.py  # functions to process mistral output
│   │   ├── medical_assessment.py    # asking all the questions
│   │   └── styling_functions.py     # page styling
│   └── main.py        # Main application script
│
├── Dockerfile         # Dockerfile for setting up the application environment
├── requirements.txt   # List of package dependencies
└── README.md          # Documentation (this file)
```

**Note**: Replace `[repository-url]` with the actual URL of your Git repository.