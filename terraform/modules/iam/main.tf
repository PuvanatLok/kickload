// Module: iam
// Creates service accounts and grants them minimum required roles.
//
// WHY SEPARATE SERVICE ACCOUNTS PER SERVICE:
// Principle of least privilege. If one service is compromised, the attacker
// only gets that service's permissions — not the entire project.
// Example: the backend API can write to Pub/Sub but cannot query BigQuery.
//          the dbt runner can query BigQuery but cannot touch Pub/Sub.
//
// WHY NOT USE THE DEFAULT SERVICE ACCOUNT:
// GCP creates a default Compute service account with Editor role (dangerously
// broad). Using it means a compromised Cloud Run instance can delete your
// entire BigQuery dataset. Always create purpose-built service accounts.
//
// BETTER SOLUTION IN THE FUTURE:
// Workload Identity Federation — instead of service account key files,
// services authenticate directly via their compute identity (no JSON keys
// to manage, rotate, or accidentally commit to git).

resource "google_service_account" "backend_api" {
  project      = var.project_id
  account_id   = "kickload-backend-${var.env}"
  display_name = "KickLoad Backend API (${var.env})"
}

resource "google_service_account" "dbt_runner" {
  project      = var.project_id
  account_id   = "kickload-dbt-${var.env}"
  display_name = "KickLoad dbt Runner (${var.env})"
}

resource "google_service_account" "pubsub_subscriber" {
  project      = var.project_id
  account_id   = "kickload-pubsub-sub-${var.env}"
  display_name = "KickLoad Pub/Sub BigQuery Subscriber (${var.env})"
}

// Backend API: can publish to Pub/Sub only
resource "google_project_iam_member" "backend_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.backend_api.email}"
}

// Backend API: can read/write GCS (for file uploads)
resource "google_project_iam_member" "backend_storage_writer" {
  project = var.project_id
  role    = "roles/storage.objectCreator"
  member  = "serviceAccount:${google_service_account.backend_api.email}"
}

// dbt runner: can run BigQuery jobs and read/write datasets
resource "google_project_iam_member" "dbt_bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt_runner.email}"
}

resource "google_project_iam_member" "dbt_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt_runner.email}"
}

// Pub/Sub → BigQuery subscriber: can write to BigQuery
resource "google_project_iam_member" "pubsub_bigquery_writer" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pubsub_subscriber.email}"
}

resource "google_project_iam_member" "pubsub_subscriber_role" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pubsub_subscriber.email}"
}
