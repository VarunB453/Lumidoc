terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

locals {
  name_prefix = "lumidoc-${var.environment}"
}

# ---------------------------------------------------------------------------
# Artifact Registry — stores the server + client container images.
# ---------------------------------------------------------------------------
resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = "${local.name_prefix}-images"
  description   = "Lumidoc container images (${var.environment})"
  format        = "DOCKER"
}

# ---------------------------------------------------------------------------
# Runtime service account — least-privilege identity for the Cloud Run services.
# ---------------------------------------------------------------------------
resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = "${local.name_prefix}-run"
  display_name = "Lumidoc Cloud Run runtime (${var.environment})"
}

# Allow the runtime SA to read mounted secrets.
resource "google_project_iam_member" "secret_accessor" {
  for_each = var.server_secrets

  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# ---------------------------------------------------------------------------
# Server service (FastAPI).
# ---------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "server" {
  project  = var.project_id
  name     = "${local.name_prefix}-server"
  location = var.region

  template {
    service_account = google_service_account.runtime.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.server_image

      ports {
        container_port = var.server_port
      }

      resources {
        limits = {
          cpu    = var.server_cpu
          memory = var.server_memory
        }
      }

      dynamic "env" {
        for_each = var.server_env
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.server_secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }
    }
  }
}

# ---------------------------------------------------------------------------
# Client service (nginx serving the built SPA).
# ---------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "client" {
  project  = var.project_id
  name     = "${local.name_prefix}-client"
  location = var.region

  template {
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.client_image

      ports {
        container_port = var.client_port
      }
    }
  }
}

# ---------------------------------------------------------------------------
# Public invoker bindings.
# The client is always public. The API is public only when
# allow_unauthenticated is true (front it with IAP / a gateway in prod).
# ---------------------------------------------------------------------------
resource "google_cloud_run_v2_service_iam_member" "client_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.client.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "server_public" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.server.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
