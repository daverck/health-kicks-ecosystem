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
  description = "Deployment environment"
  default     = "production"
}

variable "cluster_identifier" {
  type        = string
  description = "Aurora Serverless v2 DB cluster identifier"
  default     = "healthkicks-db"
}

variable "instance_identifier" {
  type        = string
  description = "Aurora Serverless v2 DB instance identifier"
  default     = "database-1-instance-1"
}

variable "master_username" {
  type        = string
  description = "Master username for PostgreSQL database"
  default     = "postgres"
}

variable "min_capacity" {
  type        = number
  description = "Minimum Aurora Serverless v2 Capacity Units (ACU)"
  default     = 0.5
}

variable "max_capacity" {
  type        = number
  description = "Maximum Aurora Serverless v2 Capacity Units (ACU)"
  default     = 1.0
}

# ------------------------------------------------------------------------------
# 1. Aurora Serverless v2 Cluster (PostgreSQL 17)
# ------------------------------------------------------------------------------

resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier                  = var.cluster_identifier
  engine                              = "aurora-postgresql"
  engine_version                      = "17.9"
  engine_mode                         = "provisioned" # Required for Serverless v2
  master_username                     = var.master_username
  iam_database_authentication_enabled = true
  backup_retention_period             = 1
  preferred_backup_window             = "00:21-00:51"
  preferred_maintenance_window        = "tue:23:37-wed:00:07"
  skip_final_snapshot                 = true

  serverlessv2_scaling_configuration {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }

  tags = {
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }

  lifecycle {
    ignore_changes = [
      master_password, # Preserves pre-existing live master password without drift
      availability_zones,
    ]
  }
}

# ------------------------------------------------------------------------------
# 2. Aurora Serverless v2 Instance
# ------------------------------------------------------------------------------

resource "aws_rds_cluster_instance" "cluster_instance" {
  identifier                 = var.instance_identifier
  cluster_identifier         = aws_rds_cluster.aurora_cluster.id
  instance_class             = "db.serverless"
  engine                     = aws_rds_cluster.aurora_cluster.engine
  engine_version             = aws_rds_cluster.aurora_cluster.engine_version
  auto_minor_version_upgrade = true
  promotion_tier             = 1

  tags = {
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "cluster_endpoint" {
  description = "Writer endpoint for Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "cluster_reader_endpoint" {
  description = "Reader endpoint for Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.aurora_cluster.reader_endpoint
}

output "cluster_arn" {
  description = "ARN of the Aurora DB cluster"
  value       = aws_rds_cluster.aurora_cluster.arn
}
