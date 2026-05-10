output "raw_dataset_id" {
  value = google_bigquery_dataset.raw.dataset_id
}

output "mart_dataset_id" {
  value = google_bigquery_dataset.mart.dataset_id
}

output "raw_events_table_id" {
  value = "${var.project_id}:${google_bigquery_dataset.raw.dataset_id}.raw_app_events"
}
