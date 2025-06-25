# **Airbnb Data ETL Pipeline on Google Cloud**

This repository contains an ETL pipeline that processes Airbnb CSV data in Google Cloud Platform (GCP) using Cloud Storage, Cloud Functions, and BigQuery.

It reads raw CSV files dropped into a GCS bucket, cleans and transforms them, writes cleaned CSVs to a separate bucket, and loads the data into BigQuery with automatic schema updates.

## Table of Contents

Prerequisites

Setup

Terraform Infrastructure

Deploying Cloud Function

Testing the Pipeline

BigQuery Table Management

Running Locally

IAM Roles

Useful GCP Documentation

Important Notes

## Prerequisites

Google Cloud SDK installed and configured (Installation guide)

Terraform installed (Installation guide)

Python 3.10+

GCP Project with billing enabled

Service Account with the necessary permissions (see IAM Roles)

# Setup

### Clone this repository

```bash
git clone https://github.com/your-repo/airbnb-etl-gcp.git
cd airbnb-etl-gcp
```
## Configure your environment variables

### Create a .env file in the project root (optional but recommended):

```
PROJECT_ID=your-gcp-project-id
REGION=europe-west2
RAW_BUCKET_NAME=airbnb-data-raw
CLEAN_BUCKET_NAME=airbnb-data-clean
BIGQUERY_DATASET=your_bigquery_dataset
BIGQUERY_TABLE=your_bigquery_table
```

### Load variables (example for macOS/Linux):
```
export $(grep -v '^#' .env | xargs)
```

# **Initialise Terraform**

```
terraform init
```

**Apply Terraform to create buckets**

````
terraform apply
````
Follow prompts to confirm.

Terraform Infrastructure
Two GCS buckets created:

Raw bucket for landing raw CSVs

Clean bucket for storing cleaned CSVs

Buckets have versioning and uniform bucket-level access enabled

## **Deploying Cloud Function**

Deploy your transformation Cloud Function (Python 3.10 runtime, 2nd gen):

```
gcloud functions deploy clean_airbnb_data \
  --gen2 \
  --runtime python310 \
  --region $REGION \
  --entry-point main \
  --trigger-event google.cloud.storage.object.v1.finalized \
  --trigger-resource $RAW_BUCKET_NAME \
  --set-env-vars CLEAN_BUCKET=$CLEAN_BUCKET_NAME,BQ_DATASET=$BIGQUERY_DATASET,BQ_TABLE=$BIGQUERY_TABLE
  ```
The function triggers on any new object in the raw bucket.

It runs the cleaning pipeline, writes cleaned CSV to the clean bucket, then loads the data into BigQuery.

## **Testing the Pipeline**

Upload a CSV file to the raw bucket:

````
gsutil cp path/to/your-file.csv gs://$RAW_BUCKET_NAME/
````

Monitor logs to ensure processing:

````
gcloud functions logs read clean_airbnb_data --gen2 --region $REGION --limit 20
````

Verify the cleaned CSV appears in the clean bucket:

````
gsutil ls gs://$CLEAN_BUCKET_NAME/
````

Verify BigQuery table is created or updated with data:

````
bq show $BIGQUERY_DATASET.$BIGQUERY_TABLE
bq head --max_rows=10 $BIGQUERY_DATASET.$BIGQUERY_TABLE
````

BigQuery Table Management

The Cloud Function will create the BigQuery table if it does not exist, inferring schema from CSV.

Each new processed CSV replaces the table (WRITE_TRUNCATE).

Schema drift is handled by allowing new columns to be added dynamically (ALLOW_FIELD_ADDITION).

Running Locally
You can also run the cleaning pipeline locally for testing:

````
python pipeline.py --input path/to/raw.csv --output path/to/clean.csv
````

IAM Roles
Ensure the Cloud Function’s service account (and your user account if applicable) have these roles assigned:

Role Name	Purpose	GCP Documentation Link
Storage Admin	Manage Cloud Storage buckets and objects	https://cloud.google.com/storage/docs/access-control/iam-roles
Cloud Functions Developer	Deploy and manage Cloud Functions	https://cloud.google.com/functions/docs/securing/managing-access#roles
BigQuery Admin or BigQuery Data Editor	Create and modify BigQuery datasets and tables, load data	https://cloud.google.com/bigquery/docs/access-control#roles

You can assign roles via the Cloud Console IAM page or use gcloud CLI, e.g.:

```
gcloud projects add-iam-policy-binding your-project-id \
  --member=serviceAccount:your-function-sa@your-project-id.iam.gserviceaccount.com \
  --role=roles/storage.admin
  ```

Useful GCP Documentation
Cloud Storage IAM Roles:
https://cloud.google.com/storage/docs/access-control/iam-roles

Cloud Functions IAM Roles and Permissions:
https://cloud.google.com/functions/docs/securing/managing-access#roles

BigQuery IAM Roles:
https://cloud.google.com/bigquery/docs/access-control#roles

Deploying 2nd Gen Cloud Functions:
https://cloud.google.com/functions/docs/concepts/2nd-gen

BigQuery Load Job Reference:
https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs#configuration.load

Important Notes
Make sure your Cloud Function service account has the necessary IAM roles.

This pipeline is designed to run on any OS (Windows, macOS, Linux). Ensure environment variables and SDKs are set accordingly.

Logs are essential for debugging — use gcloud functions logs read to monitor.

If schema changes happen often, validate BigQuery schema after each load.

Feel free to open issues or reach out for help!
Happy data cleaning and analyzing! 🚀

