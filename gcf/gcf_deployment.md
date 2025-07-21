gcloud functions deploy clean_airbnb_data \
  --gen2 \
  --runtime python310 \
  --region <REGION> \
  --entry-point main \
  --trigger-event google.cloud.storage.object.v1.finalized \
  --trigger-resource <RAW_BUCKET_NAME> \
  --set-env-vars CLEAN_BUCKET=<CLEAN_BUCKET_NAME>,BQ_DATASET=<BQ_DATASET_NAME>,BQ_TABLE=<BQ_TABLE_NAME>,GCP_PROJECT=<GCP_PROJECT_ID>
