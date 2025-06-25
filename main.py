import os
from google.cloud import storage
from google.cloud import bigquery
from pipeline import run_pipeline  # from your existing code


def load_csv_to_bigquery(uri: str, dataset_id: str, table_id: str, project_id: str):
    client = bigquery.Client(project=project_id)

    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
        autodetect=True,
    )

    load_job = client.load_table_from_uri(
        uri,
        table_ref,
        job_config=job_config
    )
    load_job.result()

    destination_table = client.get_table(table_ref)
    print(f"Loaded {destination_table.num_rows} rows into {dataset_id}:{table_id}.")


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

    cleaned_gcs_uri = f"gs://{clean_bucket_name}/{file_name}"
    load_csv_to_bigquery(
        uri=cleaned_gcs_uri,
        dataset_id=os.environ.get("BQ_DATASET"),
        table_id=os.environ.get("BQ_TABLE"),
        project_id=os.environ.get("GCP_PROJECT")  # or set your project ID some other way
    )
