// Module: pubsub
// Creates the app-events topic, dead letter topic, and BigQuery subscription.
//
// WHY ONE TOPIC FOR ALL EVENTS (not one topic per event type):
// At KickLoad's scale, a single topic with event_type in the payload is
// simpler to manage. Subscribers filter by event_type in their query.
// One topic per event type (e.g., match_created, player_joined) is better
// at massive scale (millions of events/sec) where you need independent
// scaling per event type — not needed here.
//
// WHY A DEAD LETTER TOPIC:
// Without a DLT, a message that repeatedly fails delivery is retried forever
// (burning cost) or dropped silently (data loss). The DLT catches it after
// max_delivery_attempts and holds it for you to inspect and reprocess.
// This is the Pub/Sub implementation of the outbox pattern's safety net.
//
// WHY BIGQUERY SUBSCRIPTION (not Dataflow):
// A BigQuery subscription is a native GCP connector — zero code, zero ops.
// It writes every Pub/Sub message directly into a BigQuery table.
// Dataflow (Apache Beam) gives more control (transformations, windowing) but
// costs more and requires code to maintain.
// Use Dataflow when you need to transform events before storing them.
// Use BigQuery subscription when raw storage is enough — which it is here,
// because dbt handles transformations after the fact.
//
// BETTER SOLUTION IN THE FUTURE:
// Add a schema to the topic (Pub/Sub Schemas with Avro or Protobuf).
// This enforces that producers send valid events — a bad payload is rejected
// at the topic, not silently stored as garbage in BigQuery.

resource "google_pubsub_topic" "app_events" {
  name    = "kickload-app-events-${var.env}"
  project = var.project_id

  message_retention_duration = "604800s" // 7 days (maximum for free tier)
  // FUTURE: upgrade to 2678400s (31 days) on paid plan when you need
  // longer replay windows for analytics recovery.
}

resource "google_pubsub_topic" "app_events_dead_letter" {
  name    = "kickload-app-events-dead-letter-${var.env}"
  project = var.project_id
}

resource "google_pubsub_subscription" "bigquery_sink" {
  name    = "kickload-app-events-bq-sink-${var.env}"
  project = var.project_id
  topic   = google_pubsub_topic.app_events.name

  bigquery_config {
    table            = "${var.project_id}:${var.bigquery_dataset}.raw_app_events"
    use_topic_schema = false
    write_metadata   = true
    // write_metadata = true adds columns: subscription_name, message_id,
    // publish_time, attributes. Useful for deduplication and debugging.
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.app_events_dead_letter.id
    max_delivery_attempts = 5
    // After 5 failed delivery attempts, message moves to dead letter topic.
    // You get an alert, inspect the message, fix the issue, reprocess.
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
    // Exponential backoff between retries — prevents hammering a recovering
    // BigQuery with rapid retries.
  }
}
