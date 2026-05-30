output "server_url" {
  value = module.cloud_run.server_url
}

output "client_url" {
  value = module.cloud_run.client_url
}

output "artifact_registry" {
  value = module.cloud_run.artifact_registry
}
