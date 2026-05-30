# Terraform Infrastructure

Infrastructure as Code for deploying Lumidoc to **Google Cloud Run** — a
container-native, autoscaling target that maps cleanly onto the project's
existing Docker images.

## Structure
```
terraform/
├── modules/
│   └── cloud_run/        # Reusable module: Artifact Registry + 2 Cloud Run services
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/              # Implemented (server + client + secrets wiring)
│   ├── staging/
│   └── prod/
└── README.md
```

## What the `cloud_run` module provisions
- An **Artifact Registry** Docker repository for the server and client images.
- A least-privilege **runtime service account**.
- A **server** Cloud Run service (FastAPI) with autoscaling, CPU/memory limits,
  plain env vars, and Secret Manager-backed env vars.
- A **client** Cloud Run service (nginx serving the built SPA).
- IAM bindings: the client is always public; the API is public only when
  `allow_unauthenticated = true` (gate it behind IAP or a gateway in prod).

## Prerequisites
- Terraform >= 1.5
- `gcloud` authenticated against the target project
- Server/client images pushed to Artifact Registry (the CD workflows build and
  push images; retag/push them to the Artifact Registry path output by this
  module, or point `*_image` at your registry)
- Secret Manager secrets created for the values referenced in
  `environments/dev/main.tf` (`server_secrets`), e.g.:
  ```bash
  printf '%s' "$MONGODB_URL" | gcloud secrets create lumidoc-dev-mongodb-url --data-file=-
  ```

## Usage
```bash
cd environments/dev
cp terraform.tfvars.example terraform.tfvars   # fill in project_id + image URLs
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Outputs include the public `server_url`, `client_url`, and the
`artifact_registry` path to push images to.

## State management
Uncomment and configure the `gcs` backend block in
`environments/dev/main.tf` to store state remotely (GCS provides state locking
natively). Use a distinct `prefix` per environment.

## Other environments
`staging/` and `prod/` are intentionally left to be created by copying `dev/`
and adjusting `min_instances`, `max_instances`, `allow_unauthenticated`, and the
secret IDs. Production should set `allow_unauthenticated = false` and front the
API with IAP or an API gateway.

## Other clouds
The Docker images are provider-agnostic. To target AWS instead, the equivalent
landing zone is ECS Fargate + ECR + ALB; for Azure, Container Apps + ACR.
