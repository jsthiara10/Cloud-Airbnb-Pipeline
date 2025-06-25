variable "project_id" {
        type = string
        description = "The GCP project ID"
}

variable "raw_bucket_name" {
        type = string
        description = "The name of the GCS bucket where raw CSVs are dropped"
}

variable "clean_bucket_name" {
        type = string
        description = "The name of the GCS bucket for cleaned CSVs"
}

variable "region" {
        description = "GCP Region"
        type = string
        default = "europe-west2"
}

