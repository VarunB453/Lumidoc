output "server_url" {
  description = "Public URL of the FastAPI server service."
  value       = google_cloud_run_v2_service.server.uri
}

output "client_url" {
  description = "Public URL of the client service."
  value       = google_cloud_run_v2_service.client.uri
}

output "artifact_registry" {
  description = "Artifact Registry repository for pushing images."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}

output "runtime_service_account" {
  description = "Email of the runtime service account."
  value       = google_service_account.runtime.email
}
