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

variable "instance_type" {
  type        = string
  description = "EC2 instance type (t3.micro or t3.small)"
  default     = "t3.micro"
}

variable "ami_id" {
  type        = string
  description = "Ubuntu AMI ID in eu-north-1"
  default     = "ami-0aba19e56f3eaec05" # Ubuntu 24.04 LTS
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID for EC2 instance"
  default     = "subnet-017411c8be32a97d6"
}

variable "security_group_id" {
  type        = string
  description = "Security group ID attached to EC2"
}

variable "key_name" {
  type        = string
  description = "SSH key pair name"
  default     = "healthkicks-key"
}

variable "iam_instance_profile_name" {
  type        = string
  description = "IAM instance profile name"
  default     = "EC2ToAuroraInstanceProfile"
}

variable "root_volume_size_gb" {
  type        = number
  description = "Root EBS gp3 volume size in GB"
  default     = 20
}

# ------------------------------------------------------------------------------
# 1. EC2 Instance (Single Host running Docker Blue/Green slots & Nginx)
# ------------------------------------------------------------------------------

resource "aws_instance" "backend_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  key_name               = var.key_name
  iam_instance_profile   = var.iam_instance_profile_name
  vpc_security_group_ids = [var.security_group_id]

  user_data = templatefile("${path.module}/templates/user_data.sh.tpl", {
    nginx_site_conf = file("${path.module}/templates/nginx_healthkicks.conf.tpl")
  })

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_size           = var.root_volume_size_gb
    volume_type           = "gp3"
    delete_on_termination = true

    tags = {
      Name      = "healthkicks-backend-server-root"
      Project   = "HealthKicks"
      ManagedBy = "OpenTofu"
    }
  }

  tags = {
    Name        = "healthkicks-backend-server"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }

  lifecycle {
    ignore_changes = [
      ami,       # Prevent involuntary replacement when canonical publishes new AMI updates
      user_data, # Prevent recreation of the live imported EC2 instance
    ]
  }
}

# ------------------------------------------------------------------------------
# 2. Permanent Elastic IP (Prevents DNS breaking on reboot)
# ------------------------------------------------------------------------------

resource "aws_eip" "web_eip" {
  instance = aws_instance.backend_server.id
  domain   = "vpc"

  tags = {
    Name        = "healthkicks-ec2-eip"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.backend_server.id
}

output "elastic_ip" {
  description = "Static Elastic IP allocated to the EC2 host (target for Cloudflare DNS)"
  value       = aws_eip.web_eip.public_ip
}
