// Module: bigquery
// Creates the analytics warehouse datasets and the raw events table
// that Pub/Sub writes into.
//
// WHY TWO DATASETS (raw vs mart):
// raw_kickload  — append-only, untouched data exactly as received from Pub/Sub.
//                 Never modified. This is your source of truth.
// mart_kickload — dbt-managed, clean models built from raw. These are what
//                 dashboards and analysts query.
// Separating them means a broken dbt model never corrupts your raw data.
// You can always rebuild the mart by re-running dbt from scratch.
//
// WHY PARTITION raw_app_events BY DATE:
// BigQuery charges per byte scanned. Without partitioning, "show me all
// match_created events this week" scans every event since day 1.
// With date partitioning, it scans only this week's partition — 99% cheaper
// at scale. Always partition event tables by ingestion date.
//
// WHY CLUSTER BY event_type:
// Clustering physically co-locates rows with the same event_type on disk.
// Queries filtering by event_type (the most common filter) read far less data.
// Clustering is free and should always be applied to high-cardinality columns
// you filter on often.
//
// BETTER SOLUTION IN THE FUTURE:
// Add column-level access controls — analysts can query event data but cannot
// see user_id or location columns without explicit permission.
// Use BigQuery authorized views for this pattern.

resource "google_bigquery_dataset" "raw" {
  dataset_id                 = "raw_kickload_${var.env}"
  project                    = var.project_id
  location                   = var.region
  description                = "Raw events from Pub/Sub — append only, never modified"
  delete_contents_on_destroy = var.env == "dev" ? true : false
  // delete_contents_on_destroy = true in dev only.
  // In prod, Terraform will refuse to destroy a non-empty dataset by default.
  // This is intentional — production data should never be deleted by infra code.
}

resource "google_bigquery_dataset" "mart" {
  dataset_id                 = "mart_kickload_${var.env}"
  project                    = var.project_id
  location                   = var.region
  description                = "dbt-managed analytical models — rebuilt from raw on each dbt run"
  delete_contents_on_destroy = var.env == "dev" ? true : false
}

resource "google_bigquery_table" "raw_app_events" {
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "raw_app_events"
  project             = var.project_id
  deletion_protection = var.env == "prod" ? true : false

  time_partitioning {
    type  = "DAY"
    field = null
    // null = partition by _PARTITIONTIME (BigQuery ingestion time).
    // FUTURE: switch to field = "created_at" (event time) when your app
    // reliably populates that field. Event time partitioning is more accurate
    // for analytics than ingestion time.
  }

  clustering = ["event_type", "user_id"]
  // Order matters: put the column you filter most often first.
  // event_type is almost always in WHERE clause → goes first.

  schema = jsonencode([
    { name = "subscription_name", type = "STRING", mode = "NULLABLE" },
    { name = "message_id",        type = "STRING", mode = "NULLABLE" },
    { name = "publish_time",      type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "data",              type = "STRING", mode = "NULLABLE" },
    // data is base64-encoded JSON payload from the app.
    // dbt will decode and parse this in the staging layer.
    { name = "attributes",        type = "STRING", mode = "NULLABLE" }
  ])
}
