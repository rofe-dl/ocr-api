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

- This will extract text from one image and supports caching. It takes in an `image` as `multipart/form-data`.

  ```bash
  POST /api/v1/text-extraction

  # curl command
  curl -X POST -w "\n" -F "image=@sample_images/simple.jpeg" http://localhost:8000/api/v1/text-extraction
  ```

- This is for batch extraction from images. It only supports up to 10 images at once. Note that the field name is `images` for this endpoint.

  ```bash
  POST /api/v1/batch-text-extraction

  # curl command
  curl -X POST -w "\n" -F "images=@sample_images/simple.jpeg" -F "images=@sample_images/rotated.png" http://localhost:8000/api/v1/batch-text-extraction
  ```

2. Image formats supported are: `JPG, PNG, GIF`
3. File size limit of 10 MB
4. Image metadata extraction
5. Caching using Redis so cache does not disappear in serverless environments if the instance stops. Images are identified by their hashed value
6. Confidence scores of the whole extraction calculated from the average of the extraction confidence of all words
7. Error handling functions to catch unhandled errors and return generic messages

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
