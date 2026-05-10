output "topic_name" {
  value = google_pubsub_topic.app_events.name
}

output "topic_id" {
  value = google_pubsub_topic.app_events.id
}

output "dead_letter_topic_name" {
  value = google_pubsub_topic.app_events_dead_letter.name
}
