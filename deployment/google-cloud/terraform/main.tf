# Terraform configuration for Astro Engine Google Cloud infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "astro-engine"
}

variable "domain_name" {
  description = "Custom domain name"
  type        = string
  default     = ""
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "storage.googleapis.com"
  ])

  project = var.project_id
  service = each.value
}

# Cloud Storage bucket for ephemeris data
resource "google_storage_bucket" "ephemeris_data" {
  name          = "${var.project_id}-astro-ephemeris"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

# Cloud Memorystore (Redis) instance
resource "google_redis_instance" "cache" {
  name           = "astro-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 1
  region         = var.region
  redis_version  = "REDIS_6_X"

  display_name = "Astro Engine Cache"
  
  depends_on = [google_project_service.apis]
}

# Cloud SQL PostgreSQL instance (optional)
resource "google_sql_database_instance" "postgres" {
  name             = "astro-engine-db"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
  depends_on = [google_project_service.apis]
}

# Cloud SQL database
resource "google_sql_database" "database" {
  name     = "astro_engine"
  instance = google_sql_database_instance.postgres.name
}

# Cloud SQL user
resource "google_sql_user" "user" {
  name     = "astro_user"
  instance = google_sql_database_instance.postgres.name
  password = "changeme123!"
}

# Cloud Run service
resource "google_cloud_run_service" "astro_engine" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/astro-engine:latest"
        
        ports {
          container_port = 5000
        }

        resources {
          limits = {
            memory = "2Gi"
            cpu    = "2"
          }
        }

        env {
          name  = "FLASK_ENV"
          value = "production"
        }

        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:6379/0"
        }

        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database_instance.postgres.connection_name}/${google_sql_database.database.name}"
        }
      }

      container_concurrency = 100
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.apis,
    google_redis_instance.cache
  ]
}

# Allow unauthenticated access to Cloud Run service
resource "google_cloud_run_service_iam_member" "allUsers" {
  service  = google_cloud_run_service.astro_engine.name
  location = google_cloud_run_service.astro_engine.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Monitoring alert policy for high error rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "Astro Engine High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate above 5%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"${var.service_name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Outputs
output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.astro_engine.status[0].url
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.cache.host
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "storage_bucket" {
  description = "Storage bucket name"
  value       = google_storage_bucket.ephemeris_data.name
}
