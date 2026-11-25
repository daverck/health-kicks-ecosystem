variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "service_name" {
  type        = string
  description = "App Runner service name"
  default     = "healthkicks-backend"
}

variable "image_repository_url" {
  type        = string
  description = "ECR image repository URL"
}

variable "image_tag" {
  type        = string
  description = "ECR image tag to deploy"
  default     = "latest"
}

variable "access_role_arn" {
  type        = string
  description = "IAM Role ARN for App Runner to pull image from ECR"
}

variable "instance_role_arn" {
  type        = string
  description = "IAM Role ARN for App Runner instance runtime execution"
}

variable "port" {
  type        = string
  description = "Port exposed by the container"
  default     = "8000"
}

variable "cpu" {
  type        = string
  description = "vCPU allocated to container (e.g. 256 for 0.25 vCPU, 512 for 0.5 vCPU, 1024 for 1 vCPU)"
  default     = "512"
}

variable "memory" {
  type        = string
  description = "Memory allocated to container in MB (e.g. 1024 for 1 GB, 2048 for 2 GB)"
  default     = "1024"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for VPC Connector (database subnets)"
}

variable "security_group_id" {
  type        = string
  description = "Security Group ID for VPC Connector egress"
}

variable "max_concurrency" {
  type        = number
  description = "Max concurrent requests per instance before scaling"
  default     = 100
}

variable "min_size" {
  type        = number
  description = "Minimum number of warm instances"
  default     = 1
}

variable "max_size" {
  type        = number
  description = "Maximum number of instances during load peaks"
  default     = 5
}

variable "auto_deployments_enabled" {
  type        = bool
  description = "Whether to automatically deploy new images pushed to ECR"
  default     = false
}

variable "environment_variables" {
  type        = map(string)
  description = "Environment variables passed to the container"
  default     = {}
}

variable "environment_secrets" {
  type        = map(string)
  description = "Environment secrets passed to the container from SSM or Secrets Manager"
  default     = {}
}

variable "custom_domain_name" {
  type        = string
  description = "Custom domain name (e.g. api.healthkicks.eu)"
  default     = ""
}

variable "enable_custom_domain" {
  type        = bool
  description = "Whether to associate custom domain with App Runner"
  default     = false
}
