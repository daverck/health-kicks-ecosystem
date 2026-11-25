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
  default     = "vpc-0c7bae52bbf409873"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

# ------------------------------------------------------------------------------
# Web Security Group (Ports 80, 443, 22)
# ------------------------------------------------------------------------------

resource "aws_security_group" "web_sg" {
  name        = "launch-wizard-1"
  description = "launch-wizard-1 created 2026-08-31T15:23:26.922Z"
  vpc_id      = var.vpc_id

  lifecycle {
    ignore_changes = [description]
  }

  ingress {
    description = "Allow HTTP inbound from anywhere (Cloudflare and Lets Encrypt)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS inbound from anywhere (Cloudflare & direct clients)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow SSH administration inbound"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic (ECR pull, package downloads, API external integrations)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "launch-wizard-1"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

output "web_security_group_id" {
  description = "Security Group ID for the EC2 Web host"
  value       = aws_security_group.web_sg.id
}

# ------------------------------------------------------------------------------
# 2. App Runner Egress Security Group (VPC Connector)
# ------------------------------------------------------------------------------

resource "aws_security_group" "apprunner_egress_sg" {
  name        = "healthkicks-apprunner-egress-sg"
  description = "Security Group for AWS App Runner VPC Connector egress"
  vpc_id      = var.vpc_id

  egress {
    description = "Allow all outbound traffic from App Runner through VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "healthkicks-apprunner-egress-sg"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

output "apprunner_security_group_id" {
  description = "Security Group ID for App Runner VPC Connector"
  value       = aws_security_group.apprunner_egress_sg.id
}
