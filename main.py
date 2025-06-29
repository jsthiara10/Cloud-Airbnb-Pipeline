import os
from google.cloud import storage
from pipeline import run_pipeline  # from your existing code
import logging
from google.cloud import bigquery
from google.api_core.exceptions import NotFound


def load_csv_to_bigquery(uri: str, dataset_id: str, table_id: str, project_id: str):
    client = bigquery.Client(project=project_id)

    # Check if dataset exists, create if not
    try:
        dataset = client.get_dataset(dataset_id)
    except NotFound:
        print(f"Dataset {dataset_id} not found. Creating dataset...")
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "EU"  # or your region
        client.create_dataset(dataset)
        print(f"Dataset {dataset_id} created.")

    table_ref = client.dataset(dataset_id).table(table_id)

    # Check if table exists
    try:
        table = client.get_table(table_ref)
        print(f"Table {table_id} exists. Loading data with append & schema update.")
        write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        schema_update_options = [bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
    except NotFound:
        print(f"Table {table_id} not found. Will create the table on load.")
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        schema_update_options = []

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=write_disposition,
        schema_update_options=schema_update_options,
        autodetect=True,
        max_bad_records=1000
    )

    load_job = client.load_table_from_uri(
        uri,
        table_ref,
        job_config=job_config
    )
    load_job.result()

    destination_table = client.get_table(table_ref)
    print(f"✅ Loaded {destination_table.num_rows} rows into {dataset_id}:{table_id}.")


def main(event, context):
    logging.info(f"Function invoked. Event data: {event}")
    # Extract file info from the event
    bucket_name = event['bucket']
    file_name = event['name']

    # Only process CSV files -- THIS MIGHT CHANGE TO ACCOMMODATE FOR ALL FILE TYPES
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
    schema_path = os.getenv("SCHEMA_PATH", "schemas/airbnb.json")
    run_pipeline(input_path, output_path, schema_path=schema_path)

    # Upload to clean bucket
    clean_bucket = client.bucket(clean_bucket_name)
    clean_blob = clean_bucket.blob(file_name)
    clean_blob.upload_from_filename(output_path)
    print(f"Uploaded cleaned file to {clean_bucket_name}/{file_name}")

    cleaned_gcs_uri = f"gs://{clean_bucket_name}/{file_name}"
    load_csv_to_bigquery(
        uri=cleaned_gcs_uri,
        dataset_id=os.environ.get("BQ_DATASET"),
        table_id=os.environ.get("BQ_TABLE"),
        project_id=os.environ.get("GCP_PROJECT")  # or set your project ID some other way
    )
