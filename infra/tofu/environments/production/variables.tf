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
  default     = "daverck/health-kicks-ecosystem"
}

variable "enable_app_runner" {
  type        = bool
  description = "Enable AWS App Runner backend service"
  default     = true
}

variable "app_runner_image_tag" {
  type        = string
  description = "Docker image tag for App Runner backend"
  default     = "latest"
}

variable "app_runner_cpu" {
  type        = string
  description = "CPU allocated to App Runner (256, 512, 1024, 2048)"
  default     = "512"
}

variable "app_runner_memory" {
  type        = string
  description = "Memory allocated to App Runner (1024, 2048, 4096)"
  default     = "1024"
}

variable "app_runner_max_concurrency" {
  type        = number
  description = "Max concurrent requests per instance"
  default     = 100
}

variable "app_runner_min_size" {
  type        = number
  description = "Minimum warm instances for App Runner"
  default     = 1
}

variable "app_runner_max_size" {
  type        = number
  description = "Maximum instances for App Runner during peaks"
  default     = 5
}

variable "app_runner_enable_custom_domain" {
  type        = bool
  description = "Whether to configure custom domain association for App Runner"
  default     = false
}

variable "database_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for VPC Connector (database subnets)"
  default     = ["subnet-017411c8be32a97d6"]
}
