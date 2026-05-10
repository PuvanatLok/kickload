variable "project_id" {
  description = "GCP project ID — find this in GCP Console → Project Info"
  type        = string
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "GCP region — asia-southeast1 is Singapore, lowest latency from Thailand"
  type        = string
  default     = "asia-southeast1"
}
