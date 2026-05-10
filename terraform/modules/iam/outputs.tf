output "backend_api_service_account" {
  value = google_service_account.backend_api.email
}

output "dbt_runner_service_account" {
  value = google_service_account.dbt_runner.email
}

output "pubsub_subscriber_service_account" {
  value = google_service_account.pubsub_subscriber.email
}
