import os
from google.cloud import storage
from pipeline import run_pipeline  # from your existing code

def main(event, context):
    # Extract file info from the event
    bucket_name = event['bucket']
    file_name = event['name']

    # Only process CSV files
    if not file_name.endswith(".csv"):
        print(f"Skipped non-CSV file: {file_name}")
        return

    # Define input/output paths
    input_path = f"/tmp/{file_name}"
    output_path = f"/tmp/cleaned_{file_name}"

    # Get the clean bucket from environment variable
    clean_bucket_name = os.environ.get("CLEAN_BUCKET")
    if not clean_bucket_name:
        raise Exception("CLEAN_BUCKET environment variable not set.")

    # Set up client
    client = storage.Client()

    # Download file from raw bucket
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(input_path)
    print(f"Downloaded {file_name} from {bucket_name}")

    # Run transformation
    run_pipeline(input_path, output_path)

    # Upload to clean bucket
    clean_bucket = client.bucket(clean_bucket_name)
    clean_blob = clean_bucket.blob(file_name)
    clean_blob.upload_from_filename(output_path)
    print(f"Uploaded cleaned file to {clean_bucket_name}/{file_name}")
