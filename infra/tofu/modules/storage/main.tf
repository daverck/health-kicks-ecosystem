terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g. production, staging)"
  default     = "production"
}

variable "backend_repo_name" {
  type        = string
  description = "ECR repository name for the FastAPI backend"
  default     = "healthkicks-backend"
}

variable "frontend_repo_name" {
  type        = string
  description = "ECR repository name for the Angular frontend"
  default     = "healthkicks-frontend"
}

variable "firmware_bucket_name" {
  type        = string
  description = "S3 bucket for signed OTA firmware binaries"
  default     = "healthkicks-firmware-releases-eu-west-1"
}

variable "telemetry_table_name" {
  type        = string
  description = "DynamoDB table for high-frequency IMU sensor telemetry"
  default     = "healthkicks_telemetry"
}

variable "max_ecr_images_retained" {
  type        = number
  description = "Maximum number of Docker images retained per ECR repository"
  default     = 3
}

# ------------------------------------------------------------------------------
# 1. Amazon ECR Repositories (Backend & Frontend)
# ------------------------------------------------------------------------------

resource "aws_ecr_repository" "backend" {
  name                 = var.backend_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = "HealthKicks"
    Component   = "Backend"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = var.frontend_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = "HealthKicks"
    Component   = "Frontend"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 2. Automated ECR Lifecycle Policies (Keep only last N images)
# ------------------------------------------------------------------------------

locals {
  ecr_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the ${var.max_ecr_images_retained} most recent images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = var.max_ecr_images_retained
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "backend_lifecycle" {
  repository = aws_ecr_repository.backend.name
  policy     = local.ecr_lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "frontend_lifecycle" {
  repository = aws_ecr_repository.frontend.name
  policy     = local.ecr_lifecycle_policy
}

# ------------------------------------------------------------------------------
# 3. Amazon S3 Bucket (Firmware OTA Releases)
# ------------------------------------------------------------------------------

resource "aws_s3_bucket" "firmware_releases" {
  bucket = var.firmware_bucket_name

  tags = {
    Project     = "HealthKicks"
    Component   = "FirmwareOTA"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "firmware_encryption" {
  bucket = aws_s3_bucket.firmware_releases.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "firmware_public_block" {
  bucket = aws_s3_bucket.firmware_releases.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------------------------------------------------------
# 4. Amazon DynamoDB Table (IMU Telemetry)
# ------------------------------------------------------------------------------

resource "aws_dynamodb_table" "telemetry" {
  name             = var.telemetry_table_name
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "device_id"
  range_key        = "timestamp"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  point_in_time_recovery {
    enabled = false
  }

  lifecycle {
    ignore_changes = [replica]
  }

  tags = {
    Project     = "HealthKicks"
    Component   = "Telemetry"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "backend_repo_url" {
  description = "ECR Repository URL for the Backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_repo_url" {
  description = "ECR Repository URL for the Frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "firmware_bucket_name" {
  description = "Name of the firmware releases S3 bucket"
  value       = aws_s3_bucket.firmware_releases.id
}

output "firmware_bucket_arn" {
  description = "ARN of the firmware releases S3 bucket"
  value       = aws_s3_bucket.firmware_releases.arn
}

output "telemetry_table_name" {
  description = "Name of the DynamoDB telemetry table"
  value       = aws_dynamodb_table.telemetry.name
}
