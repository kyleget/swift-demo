# Swift Demo

## Local Development

### Prerequisites

- Python v3.10
- NodeJS v18
- [Poetry](poetry)

### Running Development Backend

1. Request backend development environment variables, and create a `.env` file.

```
~ cp backend/.env.template backend/.env
```

2. Install required Python packages.

```
~ cd backend/
~ poetry install
```

3. Run development server.

```
~ source backend/.venv/bin/activate
~ uvicorn swift_demo.main:app --reload --env-file=backend/.env
```

### Running Development Frontend

1. Install NPM packages.

```
~ cd frontend/
~ yarn install
```

2. Run development server.

```
~ yarn dev
```

[poetry]: https://python-poetry.org/docs/

## Google Cloud Setup

### Build & Run

1.  Create a new Google Cloud Project (or select an existing project) and
    [enable the Cloud Build and Cloud Build APIs][cloud-enable-apis].

1.  [Create a Google Cloud service account][cloud-create-sa] .

1.  Add the following [`Cloud IAM roles`][cloud-roles] to your service account:

    - **Cloud Build Service Account** - allows for execution of builds on your behalf

    - **Cloud Run Service Agent** - allows for running Docker container on compute engine

    - **Cloud Run Developer** - allows for creating a Cloud Run instance

    - **Viewer** - allows for Cloud Build log storage

    - **Secret Manager Secret Accessor** - allows for accessing secrets from Secret Manager

1.  [`Create a JSON service account key`][create-key] for the service account.

1.  Add the following secrets to your repository's environment secrets:

    - **GCLOUD_RUN_SA_KEY** - the content of the service account JSON file

    - **GCLOUD_PROJECT_ID** - the Google Cloud Project ID

1.  After initial deploy, allow all incoming requests by going to Cloud Run > blackbird-dash > Triggers and checking "Allow unauthenticated invocations".

[cloud-enable-apis]: https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com,run.googleapis.com,secret-manager
[cloud-create-sa]: https://cloud.google.com/iam/docs/creating-managing-service-accounts
[cloud-roles]: https://cloud.google.com/iam/docs/roles-overview
