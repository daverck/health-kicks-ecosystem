variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "service_name" {
  type        = string
  description = "ECS service and task family base name"
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

variable "execution_role_arn" {
  type        = string
  description = "IAM Role ARN for ECS task execution (ECR pull, CloudWatch logs, SSM secrets)"
}

variable "task_role_arn" {
  type        = string
  description = "IAM Role ARN assumed by the application containers at runtime"
}

variable "subnet_ids" {
  type        = list(string)
  description = "VPC Subnet IDs for ECS Fargate tasks"
}

variable "security_group_id" {
  type        = string
  description = "Security Group ID attached to ECS Fargate tasks"
}

variable "cpu" {
  type        = string
  description = "Fargate task CPU units (e.g. 256, 512, 1024)"
  default     = "512"
}

variable "memory" {
  type        = string
  description = "Fargate task memory in MiB (e.g. 512, 1024, 2048)"
  default     = "1024"
}

variable "desired_count" {
  type        = number
  description = "Number of running Fargate tasks (set to 0 to pause and pay $0/month)"
  default     = 1
}

variable "use_spot" {
  type        = bool
  description = "Run on Fargate Spot (~70% discount) instead of On-Demand Fargate"
  default     = true
}

variable "environment_variables" {
  type        = map(string)
  description = "Plain environment variables passed to the backend container"
  default     = {}
}

variable "environment_secrets" {
  type        = map(string)
  description = "Map of environment variable names to SSM Parameter Store ARNs"
  default     = {}
}

variable "enable_cloudflare_tunnel" {
  type        = bool
  description = "Attach cloudflared sidecar container for zero-cost HTTPS ingress without ALB"
  default     = false
}

variable "cloudflare_tunnel_token_ssm_arn" {
  type        = string
  description = "SSM Parameter Store ARN holding CLOUDFLARE_TUNNEL_TOKEN"
  default     = ""
}
