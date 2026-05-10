output "uploads_bucket_name" {
  value = google_storage_bucket.app_uploads.name
}

output "uploads_bucket_url" {
  value = "gs://${google_storage_bucket.app_uploads.name}"
}
