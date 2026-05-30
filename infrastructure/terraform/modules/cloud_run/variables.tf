variable "project_id" {
  description = "GCP project ID to deploy into."
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run + Artifact Registry."
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment name (dev | staging | prod)."
  type        = string
}

variable "server_image" {
  description = "Fully-qualified container image for the FastAPI server."
  type        = string
}

variable "client_image" {
  description = "Fully-qualified container image for the React client (nginx)."
  type        = string
}

variable "server_port" {
  description = "Port the FastAPI container listens on."
  type        = number
  default     = 8000
}

variable "client_port" {
  description = "Port the nginx client container listens on."
  type        = number
  default     = 80
}

variable "min_instances" {
  description = "Minimum Cloud Run instances (set >0 to avoid cold starts)."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum Cloud Run instances for autoscaling."
  type        = number
  default     = 4
}

variable "server_cpu" {
  description = "vCPU allocation for the server service."
  type        = string
  default     = "1"
}

variable "server_memory" {
  description = "Memory allocation for the server service."
  type        = string
  default     = "1Gi"
}

variable "server_env" {
  description = "Non-secret environment variables passed to the server (e.g. APP_ENV, MONGODB_DB_NAME)."
  type        = map(string)
  default     = {}
}

variable "server_secrets" {
  description = "Map of env var name -> Secret Manager secret ID. Mounted as env vars on the server."
  type        = map(string)
  default     = {}
}

variable "allow_unauthenticated" {
  description = "Whether the services are publicly invokable. The client is always public; gate the API in prod."
  type        = bool
  default     = true
}
