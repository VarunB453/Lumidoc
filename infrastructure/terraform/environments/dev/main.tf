terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Configure a remote state backend before running in CI:
  #
  # backend "gcs" {
  #   bucket = "lumidoc-tfstate"
  #   prefix = "dev"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "cloud_run" {
  source = "../../modules/cloud_run"

  project_id  = var.project_id
  region      = var.region
  environment = "dev"

  server_image = var.server_image
  client_image = var.client_image

  min_instances = 0
  max_instances = 2

  server_env = {
    APP_ENV         = "development"
    MONGODB_DB_NAME = "lumidoc"
    LOG_JSON        = "true"
  }

  # Map env var name -> Secret Manager secret ID. Create these secrets first:
  #   gcloud secrets create lumidoc-dev-mongodb-url --data-file=-
  server_secrets = {
    MONGODB_URL       = "lumidoc-dev-mongodb-url"
    REDIS_URL         = "lumidoc-dev-redis-url"
    OPENROUTER_API_KEY = "lumidoc-dev-openrouter-key"
    OPENAI_API_KEY    = "lumidoc-dev-openai-key"
    GOOGLE_API_KEY    = "lumidoc-dev-google-key"
  }

  allow_unauthenticated = true
}
