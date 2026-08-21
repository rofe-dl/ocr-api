# ocr-api

This is a REST API written in Python/FastAPI that can be used for OCR(Optical Character Recognition). It uses Google Vision Cloud for OCR services.

The Swagger documentation page can be found at `<API_URL>/redoc` or `<API_URL>/docs`.

## Local Setup

1. You will need your own Google Cloud account, the free tier will work as long as you have a billing account linked to it.
1. Enable the Cloud Vision API, then go to IAM and create a service account with `.json` credentials and owner permissions. It will download a `.json` file, rename it to `credentials.json` and place it in the project folder.
1. Create a `.env` file in the project, with the same values given in `sample.env`.
1. Install Docker with Docker Compose if you don't have it installed.
1. Finally, just run `docker compose up`.

## Features Implemented & Testing Instructions

1. The API has 2 endpoints:

- `POST /api/v1/text-extraction`

  This will extract text from one image and **supports caching**. It takes in an `image` as `multipart/form-data`.

  It has a rate limit of `10 reqs/minute`.

  ```bash
  # curl command
  curl -i -X POST -w "\n" -F "image=@sample_images/simple.jpeg" http://localhost:8000/api/v1/text-extraction
  ```

- `POST /api/v1/batch-text-extraction`

  This is for batch extraction from images. It only supports up to 10 images at once. Note that the field name is `images` for this endpoint.

  It has a rate limit of `5 reqs/minute`.

  ```bash
  # curl command
  curl -i -X POST -w "\n" -F "images=@sample_images/simple.jpeg" -F "images=@sample_images/rotated.png" http://localhost:8000/api/v1/batch-text-extraction
  ```

2. Image formats supported are: `JPG, PNG, GIF`
3. File size limit of 10 MB
4. Image metadata extraction
5. Caching using Redis so cache does not disappear in serverless environments if the instance stops. Images are identified by their hashed value
6. Confidence scores of the whole extraction calculated from the average of the extraction confidence of all words
7. Error handling functions to catch unhandled errors and return generic messages
8. Rate limiting using Redis as the store.

## Project Architecture

- The project is divided into:
  - `services`: Core text extraction logic
  - `routes`: The API endpoints (also acts like a controller layer)
  - `models`: The response schemas
  - `utils`: Helper functions

- `uv` is the package manager used
- Ruff is used along with git hooks to automatically format and style the code when `git commit` is used
- Type hinting used for all functions
- Sample images provided in the repo for testing

## Response Formats

`POST /api/v1/text-extraction`

```json
{
  "success": true,
  "text": "Further information may be obtained\nM.A., Fellow and Lecturer in Chemistry, H\nfrom Prof. A. Gilligan, D.Sc., Department\nLeeds, and from Mr. A. H. Worrall, M.A.,\nCollege, Jersey.",
  "confidence": 0.95,
  "processing_time_ms": 640.74,
  "cached": false,
  "metadata": {
    "filename": "simple.jpeg",
    "size_bytes": 24203,
    "width": 690,
    "height": 289,
    "image_format": "JPEG"
  }
}
```

`POST /api/v1/batch-text-extraction`

```json
{
  "success": true,
  "total_images": 2,
  "results": [
    {
      "filename": "small.png",
      "success": true,
      "text": "Cedric\nhimself knew\nnothing\nwhatever about it. It had never been\neven mentioned to him. He knew that\nhis papa had been an Englishman,\nbecause his mamma had told him so;\nbut then his papa had died when he\nwas so little a boy that he could not\nremember very much about him,\nexcept that he was big, and had blue\neyes and a long mustache, and that it\nwas a splendid thing to be carried\naround the room on his shoulder.",
      "confidence": 0.98,
      "metadata": {
        "filename": "small.png",
        "size_bytes": 133161,
        "width": 486,
        "height": 423,
        "image_format": "PNG"
      },
      "error": null
    },
    {
      "filename": "Rafidul_Islam_Resume.jpg",
      "success": false,
      "text": "",
      "confidence": 0,
      "metadata": {
        "filename": "Rafidul_Islam_Resume.jpg",
        "size_bytes": 87283,
        "width": null,
        "height": null,
        "image_format": null
      },
      "error": "500: Bad image data."
    }
  ],
  "processing_time_ms": 703.33
}
```

## Error Formats

Possible error codes:

- `400`: Invalid request
- `413`: Image size is too big
- `422`: Invalid file format
- `500`: Internal Server Error

Example format

```json
{
  "success": false,
  "error": "Too many requests. Please try again later."
}
```

## Google Cloud Run Deployment Steps

1. Install Google Cloud CLI, go through the initialization process and select the right project.
2. Enable Cloud Run, Artifact Registry, Cloud Build and Secrets Manager.

   ```bash
   glcoud services enable run.googleapis.com artifactregistry.googleapis.com \
   cloudbuild.googleapis.com secretmanager.googleapis.com
   ```

3. Create a repo in Artifact Registry.

   ```bash
   gcloud artifacts repositories create ocr-api-repo \
   --repository-format=docker \
   --location=asia-southeast1
   ```

4. Push the Docker image to Artifact Registry by building the image on the cloud.

   ```bash
   gcloud builds submit --tag asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/ocr-api-repo/ocr-api:<LATEST_GIT_COMMIT_HASH> .
   ```

5. Create a Google Secret for the `REDIS_URL`.

   ```bash
   gcloud secrets create redis-url --replication-policy="automatic"
   ```

6. Store the secret value.

   ```bash
   echo -n "rediss://:your_password@your-redis-host:port" | \
     gcloud secrets versions add redis-url --data-file=-
   ```

7. Give the default Cloud Run service account access to the new secret. To get your project number, run `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`

   ```bash
   gcloud secrets add-iam-policy-binding redis-url \
     --member="serviceAccount:<YOUR_PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

8. Finally deploy using:

   ```bash
   gcloud run deploy ocr-api \
     --image asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/ocr-api-repo/ocr-api:<LATEST_GIT_COMMIT_HASH> \
     --region asia-southeast1 \
     --allow-unauthenticated \
     --set-secrets REDIS_URL="redis-url:latest"
   ```

### Re-deploy

1. Tag the new build like before and upload it:

   ```bash
   gcloud builds submit --tag asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/ocr-api-repo/ocr-api:<LATEST_GIT_COMMIT_HASH> .
   ```

2. Deploy the new image:

   ```bash
   gcloud run deploy ocr-api \
    --image asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/ocr-api-repo/ocr-api:<LATEST_GIT_COMMIT_HASH> \
    --region asia-southeast1
   ```

3. If you have to change a secret:

   ```bash
   echo -n "rediss://:your_password@your-redis-host:port" | \
     gcloud secrets versions add redis-url --data-file=-

   # then
   gcloud run services update ocr-api \
     --region asia-southeast1 \
     --update-secrets REDIS_URL="redis-url:latest"
   ```

   As it points to the `latest` version of the variable, it'll pick up the new value.
