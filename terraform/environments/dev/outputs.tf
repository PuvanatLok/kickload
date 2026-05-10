output "pubsub_topic" {
  value       = module.pubsub.topic_name
  description = "Pub/Sub topic name — set this in your FastAPI .env"
}

output "uploads_bucket" {
  value       = module.storage.uploads_bucket_name
  description = "GCS bucket name for file uploads"
}

output "raw_events_table" {
  value       = module.bigquery.raw_events_table_id
  description = "BigQuery table receiving raw Pub/Sub events"
}

output "backend_service_account" {
  value       = module.iam.backend_api_service_account
  description = "Service account email for Cloud Run — set this when deploying"
}
