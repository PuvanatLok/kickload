variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "env" {
  description = "Environment name: dev or prod"
  type        = string
}

variable "region" {
  description = "GCP region for the bucket"
  type        = string
  default     = "asia-southeast1"
}
