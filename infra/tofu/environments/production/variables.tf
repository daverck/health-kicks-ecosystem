variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "eu-north-1"
}

variable "environment" {
  type        = string
  description = "Environment name (production, staging)"
  default     = "production"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "vpc_id" {
  type        = string
  description = "Target AWS VPC ID"
  default     = "vpc-0c7bae52bbf409873"
}

variable "subnet_id" {
  type        = string
  description = "Target public subnet ID for EC2"
  default     = "subnet-017411c8be32a97d6"
}

variable "key_name" {
  type        = string
  description = "EC2 SSH Key Pair name"
  default     = "healthkicks-key"
}

variable "github_repository" {
  type        = string
  description = "GitHub monorepo (owner/repo) for OIDC federation"
  default     = "serckx/healthkicks-ecosystem"
}
