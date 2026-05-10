// Dev environment — wires all modules together.
//
// WHY TERRAFORM BACKEND IN GCS (not local):
// Local state (terraform.tfstate on your laptop) means:
//   - State is lost if your laptop dies
//   - Nobody else can run Terraform on the same project
//   - No state locking — two applies running simultaneously corrupt state
// GCS backend solves all three. The bucket must be created manually ONCE
// before running terraform init. See docs/terraform-bootstrap.md.
//
// WHY A SEPARATE STATE PER ENVIRONMENT:
// If dev and prod share one state file, a mistake in dev configuration
// can trigger prod resource changes on the next apply. Separate backends
// mean dev and prod are completely independent Terraform operations.
//
// BETTER SOLUTION IN THE FUTURE:
// Terraform Cloud or Atlantis — adds a UI, run history, plan approvals,
// and team access control on top of remote state. Use when the team grows
// beyond one person running Terraform locally.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "kickload-tfstate-dev"
    // This bucket must exist before running terraform init.
    // Create it once in GCP Console → Cloud Storage → Create bucket.
    // Name it exactly: kickload-tfstate-dev
    // Region: asia-southeast1, Standard storage, no public access.
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  // Credentials come from gcloud auth application-default login.
  // Never hardcode credentials or commit a service account JSON key.
}

module "apis" {
  source     = "../../modules/apis"
  project_id = var.project_id
  apis = [
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com",          // Cloud Run — for FastAPI backend later
    "sqladmin.googleapis.com",     // Cloud SQL — for PostgreSQL later
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ]
}

module "iam" {
  source     = "../../modules/iam"
  project_id = var.project_id
  env        = var.env

  depends_on = [module.apis]
  // depends_on ensures APIs are enabled before IAM resources are created.
  // Without this, creating a service account might fail if the IAM API
  // isn't enabled yet.
}

module "storage" {
  source     = "../../modules/storage"
  project_id = var.project_id
  env        = var.env
  region     = var.region

  depends_on = [module.apis]
}

module "bigquery" {
  source     = "../../modules/bigquery"
  project_id = var.project_id
  env        = var.env
  region     = var.region

  depends_on = [module.apis]
}

module "pubsub" {
  source           = "../../modules/pubsub"
  project_id       = var.project_id
  env              = var.env
  bigquery_dataset = module.bigquery.raw_dataset_id

  depends_on = [module.apis, module.bigquery]
  // Pub/Sub subscription references the BigQuery table — BigQuery must
  // be created first or Terraform cannot resolve the table reference.
}
