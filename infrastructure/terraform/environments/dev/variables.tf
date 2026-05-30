variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region."
  type        = string
  default     = "us-central1"
}

variable "server_image" {
  description = "Server container image (e.g. us-central1-docker.pkg.dev/<proj>/lumidoc-dev-images/server:<tag>)."
  type        = string
}

variable "client_image" {
  description = "Client container image."
  type        = string
}
