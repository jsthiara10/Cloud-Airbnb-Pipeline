# 🏡 Airbnb NYC Data Pipeline – GCP Production Rollout #

This project delivers a scalable, modular data pipeline to clean and load NYC Airbnb listings into Google BigQuery. It supports both local testing and production-grade GCP deployment.

### 📁 Project Structure
```
.
├── pipeline.py               # Main data cleaning logic
├── main.py                   # GCP Cloud Function entrypoint
├── utils.py                  # Reusable helpers (validation, quoting, etc.)
├── requirements.txt          # Python dependencies
├── /data/
│   ├── raw/                  # Local raw CSV files
│   └── cleaned/              # Locally cleaned output files
├── /logs/                    # Local run logs
├── /gcf/                     # GCP deployment config
└── README.md                 # This file
```

## ✅ Key Features
🔄 End-to-end CSV ingestion, cleaning, and BigQuery loading

🔍 Cleans name and host_name fields and safely encloses them in double quotes

📦 Prevents column shifting by quoting all values

## 🧼 Removes:

Duplicate rows

Null values

Listings with 0 reviews

🧠 Validates DataFrame to remove rogue index-like columns

🧪 Fully testable on-premises, deployable to GCP

## 🛠️ Infrastructure:
### This project assumes you have:

A raw GCS bucket (for unprocessed files)

A clean GCS bucket (for cleaned files)

A BigQuery dataset and table for loading cleaned data

✅ Optional: Buckets and other resources can be provisioned using Terraform (terraform/) or manually created in the GCP Console.

### ⚙️ Local Usage
### Step 1: Run the cleaning pipeline locally
```
python pipeline.py \
  --input data/raw/AB_NYC_2019.csv \
  --output data/cleaned/AB_NYC_2019_cleaned.csv
```

### This will:

Remove duplicates and nulls

Enclose key fields in double quotes

Quote all fields

Save to data/cleaned/

Step 2: Upload to GCS (Raw Bucket)
```
gsutil cp data/cleaned/AB_NYC_2019_cleaned.csv gs://your-raw-bucket-name/
```

### If deployed, this triggers the Cloud Function automatically.

## ☁️ GCP Cloud Function
When triggered, main.py:

Downloads the CSV from the raw bucket

Cleans the data via AirbnbCleaner

Uploads the result to the clean bucket

Loads the cleaned file into BigQuery

## 🔄 BigQuery LoadJobConfig (Used in main.py)
```
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    autodetect=True,
    quote_character='"',
    max_bad_records=1000
)
```

## 🔐 IAM Permissions
Ensure your Cloud Function service account has:

Role & Purpose:
roles/storage.objectViewer Read from raw bucket
roles/storage.objectCreator	Write to clean bucket
roles/bigquery.dataEditor	Load data into BigQuery

## 🛠️ Manual Import into BigQuery
Use the bq CLI if you want to load the cleaned CSV manually:

```
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --replace \
  --quote='"' \
  --max_bad_records=1000 \
  project_id:dataset.table \
  ./data/cleaned/AB_NYC_2019_cleaned.csv
```

## 📌 Common Issues Solved
Problem	Solution
Shifting columns / wrong data alignment	Use quotechar='"' and quoting=csv.QUOTE_ALL
Broken rows / too many values	Enclose name and host_name in quotes
Rogue index columns	Utility added to drop index-like or unnamed columns
Encoding problems	Ensured consistent UTF-8 encoding

## 🧰 Future Improvements
 Add unit tests (pytest)

 Add DAG scheduling with Cloud Composer or Scheduler

 Add monitoring & alerting (Cloud Monitoring)

 Support for JSON and semi-structured formats

## 🙌 Acknowledgments
Thanks to everyone who contributed ideas, tests, and bugs during the pipeline’s PoC phase! Suggestions for improvement are welcome.

