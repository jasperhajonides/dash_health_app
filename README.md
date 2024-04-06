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



# GCP deployment:

Make sure you create a project on GCP and enable your billing because this does cost a little bit of money (£1-10?)

To host the docker image ensure `gcloud` is installed correctly:


## Installing google cloud sdk

### Download and Install the Google Cloud SDK
You can download and run the Google Cloud SDK installer script with the following command. You'll specify the installation directory using the --install-dir flag:

`curl https://sdk.cloud.google.com | bash -s -- --install-dir="/path/to/folder"`

This command will download the installation script and run it, directing the installation to the folder you specified.

### Initialize the SDK

After the installation process is complete, restart your terminal session to apply changes, or run the following command to reset your terminal's environment variables:

`exec -l $SHELL`



Then, navigate to the installation directory and run the gcloud init command to initialize the SDK:

`cd "/path/to/dir/google-cloud-sdk" ./gcloud init`

If you run into errors you may want to adjsut the permissions:

`chmod +x "./bin/gcloud"`

Then try running ./gcloud init again.



### Add gcloud to Your PATH

To ensure that the gcloud command is available in all terminal sessions without needing to navigate to the installation directory, add the Google Cloud SDK's bin directory to your PATH environment variable. Add the following line to your .zshrc or .bash_profile file, depending on which shell you use:

`export PATH="$PATH:/path/to/dir/google-cloud-sdk/bin"`

After editing the file, apply the changes by running:

`source ~/.zshrc`

or if you use bash:

`source ~/.bash_profile`

## Build the docker image:

1. Make sure you have a Dockerfile in the root directory of your Dash App. This file specifies how to build the Docker image of your app.
2. Open your terminal or command prompt.
3. Navigate to the directory containing your Dash App.
4. Run the following command to build the Docker image, replacing `{IMAGE}` with your desired image name (e.g., `dash-app`) and `{TAG}` with your desired tag (e.g., `v1`):


`docker buildx build --platform linux/amd64 -t gcr.io/dash-health-2024/dash-app:v1 . --push`

This command explicitly targets the linux/amd64 platform for the build and pushes the image to the container registry.

If not working on a MacOS you may want to run 

`docker build -f Dockerfile -t gcr.io/dash-health-2024/dash-app:v1 .`


## Pushing docker images:

Before pushing the Docker image, ensure you have authenticated Docker to access Google Cloud services:

`gcloud auth configure-docker`

Then, push the Docker image to Google Container Registry with:

`docker push gcr.io/dash-health-2024/dash-app:v1`


## Deploying App to Cloud Run 

Finally, deploy your app to Cloud Run using the gcloud command. This will create a new service or update an existing one with your Docker image:


```
gcloud run deploy dash-demo \
      --image=gcr.io/dash-health-2024/dash-app:v1 \
      --platform=managed \
      --region=us-central1 \
      --timeout=60 \
      --concurrency=80 \
      --cpu=1 \
      --memory=256Mi \
      --max-instances=10 \
      --allow-unauthenticated
```

This command deploys your Dash App as a service named dash-demo in the us-central1 region, with specific performance settings. After deployment, the command outputs the URL where your app is publicly available.



## Examining Existing Images 


`gcloud container images list --repository=gcr.io/dash-health-2024`

or list all the tags of an image:

`gcloud container images list-tags gcr.io/dash-health-2024/dash-app`

Now we can delete the desired tag of an image:

`gcloud container images delete gcr.io/dash-health-2024/dash-app:{TAG} --quiet`
