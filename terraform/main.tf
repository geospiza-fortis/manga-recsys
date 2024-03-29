terraform {
  backend "gcs" {
    bucket = "manga-recsys-tfstate"
    prefix = "manga-recsys"
  }
}

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
  required_version = ">= 0.13"
}


locals {
  project_id = "manga-recsys"
  region     = "us-central1"
  repo_name  = "manga-recsys"
}

provider "google" {
  project = local.project_id
  region  = local.region
}

data "google_project" "project" {}

resource "google_storage_bucket" "default" {
  name                        = local.repo_name
  location                    = "US"
  uniform_bucket_level_access = true
  cors {
    origin          = ["*"]
    method          = ["GET"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

// make a non-public bucket that we use for caching static files; we can remove
// files after a while; we also don't need cors headers
resource "google_storage_bucket" "cache" {
  name                        = "${local.repo_name}-cache"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "default-public" {
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}


resource "google_project_service" "default" {
  for_each = toset(["run", "cloudbuild", "iam"])
  service  = "${each.key}.googleapis.com"
}

resource "google_container_registry" "registry" {
  location = "US"
}

resource "google_service_account" "cloudbuild" {
  account_id = "cloudbuild-${local.repo_name}"
}

resource "google_project_iam_member" "cloudbuild" {
  for_each = toset([
    "roles/iam.serviceAccountUser",
    "roles/logging.logWriter",
    "roles/run.admin",
    "roles/storage.admin"
  ])
  project = data.google_project.project.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

resource "google_cloudbuild_trigger" "github" {
  github {
    name  = local.repo_name
    owner = "geospiza-fortis"
    push {
      branch       = "^main$"
      invert_regex = false
    }
  }
  substitutions = {
    _REGION            = local.region
    _VITE_STATIC_HOST  = "https://storage.googleapis.com/${google_storage_bucket.default.name}"
    _VITE_CACHE_BUCKET = google_storage_bucket.cache.name
  }
  filename        = "cloudbuild.yaml"
  service_account = google_service_account.cloudbuild.id
  depends_on = [
    google_project_service.default["cloudbuild"],
    google_project_iam_member.cloudbuild["roles/iam.serviceAccountUser"],
    google_project_iam_member.cloudbuild["roles/logging.logWriter"],
  ]
}


resource "google_cloud_run_v2_service" "default" {
  name     = local.repo_name
  location = local.region

  template {
    scaling {
      max_instance_count = 20
    }
    containers {
      image = "gcr.io/${local.project_id}/${local.repo_name}-app:latest"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.default["run"]]
}

resource "google_cloud_run_service_iam_member" "all-users" {
  service  = google_cloud_run_v2_service.default.name
  location = google_cloud_run_v2_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value = google_cloud_run_v2_service.default.uri
}

// add a cloud run job
resource "google_cloud_run_v2_job" "sync-tar-to-gz" {
  name         = "sync-tar-to-gz"
  location     = local.region
  launch_stage = "BETA"

  template {
    parallelism = 1
    task_count  = 1
    template {
      max_retries = 0
      timeout     = "3600s"
      containers {
        image = "gcr.io/${local.project_id}/${local.repo_name}-sys:latest"
        command = [
          "bash", "-c",
        ]
        args = [
          // use a here document to write out the script
          <<EOF
            manga-recsys sync download --path data/tar/ &&
            manga-recsys sync untar-gz --cores 4 &&
            manga-recsys sync upload-gz
          EOF
        ]
        resources {
          limits = {
            cpu    = "8000m"
            memory = "16Gi"
          }
        }
      }
    }
  }
}
