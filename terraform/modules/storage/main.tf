// Module: storage
// GCS buckets for app file uploads (avatars, receipt photos).
//
// WHY GCS OVER STORING FILES IN POSTGRESQL:
// Storing binary files in a database bloats it, slows backups, and makes
// every file read consume a DB connection. GCS is built for object storage —
// unlimited scale, pay per GB, CDN-ready, direct upload from mobile.
//
// WHY UNIFORM BUCKET-LEVEL ACCESS:
// GCP has two access control models: legacy ACLs (per-object) and
// uniform bucket-level access (IAM only). Uniform is simpler, more auditable,
// and Google's recommended default. ACLs are a footgun — easy to accidentally
// make a file public.
//
// WHY LIFECYCLE RULES:
// Receipt photos and match photos are only relevant for ~90 days after a
// match. Keeping them forever wastes money. Lifecycle rules delete or archive
// objects automatically — no manual cleanup.
//
// BETTER SOLUTION IN THE FUTURE:
// Signed URLs — instead of making the bucket public, generate short-lived URLs
// (15 min expiry) that the app gives to users. Files stay private but are
// accessible to authorized users. Essential before going to production.

resource "google_storage_bucket" "app_uploads" {
  name                        = "${var.project_id}-uploads-${var.env}"
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.env == "dev" ? true : false
  // force_destroy = true in dev so you can tear down without manually emptying.
  // NEVER true in prod — prevents accidental deletion of user data.

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
      // After 90 days, move to NEARLINE (cheaper, slightly slower read).
      // NEARLINE is for data accessed less than once per month.
      // COLDLINE (90 day min) and ARCHIVE (365 day min) are cheaper still.
    }
  }

  versioning {
    enabled = var.env == "prod" ? true : false
    // Versioning in prod only — lets you recover accidentally deleted files.
    // Off in dev to keep storage costs minimal.
  }
}
