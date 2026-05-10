variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "env" {
  description = "Environment name: dev or prod"
  type        = string
}

variable "bigquery_dataset" {
  description = "BigQuery dataset ID where raw events are written"
  type        = string
}
