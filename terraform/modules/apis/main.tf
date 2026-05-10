// Module: apis
// Enables GCP APIs required by KickLoad.
//
// WHY THIS MODULE EXISTS:
// GCP does not enable APIs by default. If you provision a Pub/Sub topic
// without enabling the Pub/Sub API first, Terraform fails with a cryptic
// permission error. Enabling APIs here makes the dependency explicit.
//
// BETTER SOLUTION IN THE FUTURE:
// At a larger org, API enablement lives in a separate "foundation" layer
// managed by a platform team. Individual product teams never touch it.
// Tools: Google Cloud Foundation Toolkit or Fabric FAST.

resource "google_project_service" "apis" {
  for_each = toset(var.apis)

  project                    = var.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
  // disable_on_destroy = false because disabling an API affects all resources
  // using it — dangerous in a shared project. Never set this to true in prod.
}
