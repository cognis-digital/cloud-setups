terraform { required_providers { google = { source = "hashicorp/google" } } }
provider "google" { project = var.project, region = "us-central1" }
variable "project" {}
resource "google_cloud_run_v2_service" "app" {
  name = "cognis-app"; location = "us-central1"
  template { containers { image = "us-central1-docker.pkg.dev/${var.project}/cognis/app:latest" } }
}
