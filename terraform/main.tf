resource "google_storage_bucket" "raw_bucket" {
  name     = var.raw_bucket_name
  project  = var.project_id
  location = var.region
}

resource "google_storage_bucket" "clean_bucket" {
  name     = var.clean_bucket_name
  project  = var.project_id
  location = var.region
}

