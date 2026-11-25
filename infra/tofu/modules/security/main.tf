terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

variable "vpc_id" {
  type        = string
  description = "Target VPC ID"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "allow_direct_http_port_8000" {
  type        = bool
  description = "Allow direct inbound TCP 8000 (disable once Cloudflare Tunnel is active)"
  default     = true
}

# ------------------------------------------------------------------------------
# 1. ECS Fargate Tasks Security Group
# ------------------------------------------------------------------------------

resource "aws_security_group" "ecs_tasks_sg" {
  name        = "healthkicks-ecs-tasks-sg"
  description = "Security Group for HealthKicks ECS Fargate tasks"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.allow_direct_http_port_8000 ? [1] : []
    content {
      description = "Temporary direct HTTP port 8000 access before Cloudflare Tunnel cutover"
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    description = "Allow all outbound traffic (ECR pull, SSM, Cloudflare Tunnel, Aurora, DynamoDB, IoT)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "healthkicks-ecs-tasks-sg"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 2. Aurora PostgreSQL Security Group (Allows Port 5432 from ECS Fargate Tasks)
# ------------------------------------------------------------------------------

resource "aws_security_group" "aurora_sg" {
  name        = "healthkicks-aurora-sg"
  description = "Security Group for Aurora PostgreSQL allowing ECS Fargate access"
  vpc_id      = var.vpc_id

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [description]
  }

  ingress {
    description     = "Allow PostgreSQL inbound from ECS Fargate tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks_sg.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "healthkicks-aurora-sg"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

output "ecs_tasks_security_group_id" {
  description = "Security Group ID for ECS Fargate tasks"
  value       = aws_security_group.ecs_tasks_sg.id
}

output "aurora_security_group_id" {
  description = "Security Group ID for Aurora PostgreSQL Cluster"
  value       = aws_security_group.aurora_sg.id
}
