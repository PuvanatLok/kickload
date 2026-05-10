variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "env" {
  description = "Environment name: dev or prod"
  type        = string
}

variable "region" {
  description = "BigQuery dataset location"
  type        = string
  default     = "asia-southeast1"
}
