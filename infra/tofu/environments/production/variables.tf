variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "eu-west-1"
}

variable "environment" {
  type        = string
  description = "Environment name (production, staging)"
  default     = "production"
}

variable "vpc_id" {
  type        = string
  description = "Target AWS VPC ID"
  default     = "vpc-0e6a06761f32abf4e"
}

variable "database_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for ECS Fargate tasks and Aurora"
  default = [
    "subnet-0c495b2ec4a2ef87b",
    "subnet-077739a80a78095ed",
    "subnet-057349c3160b79da1",
  ]
}

variable "aurora_snapshot_identifier" {
  type        = string
  description = "Aurora DB cluster snapshot identifier to restore from in eu-west-1"
  default     = "healthkicks-db-snapshot-eu-west-1"
}

variable "github_repository" {
  type        = string
  description = "GitHub monorepo (owner/repo) for OIDC federation"
  default     = "daverck/health-kicks-ecosystem"
}

# ------------------------------------------------------------------------------
# ECS Fargate Spot Compute Configuration
# ------------------------------------------------------------------------------

variable "backend_image_tag" {
  type        = string
  description = "Docker image tag for ECS Fargate backend"
  default     = "latest"
}

variable "fargate_cpu" {
  type        = string
  description = "CPU allocated to Fargate task (256, 512, 1024)"
  default     = "512"
}

variable "fargate_memory" {
  type        = string
  description = "Memory allocated to Fargate task in MiB (512, 1024, 2048)"
  default     = "1024"
}

variable "fargate_desired_count" {
  type        = number
  description = "Desired number of Fargate tasks (set to 0 to pause and stop compute billing)"
  default     = 1
}

variable "fargate_use_spot" {
  type        = bool
  description = "Use Fargate Spot (~70% discount) instead of Fargate On-Demand"
  default     = true
}

variable "enable_cloudflare_tunnel" {
  type        = bool
  description = "Enable cloudflared sidecar container (requires /healthkicks/<env>/CLOUDFLARE_TUNNEL_TOKEN in SSM)"
  default     = false
}

# ------------------------------------------------------------------------------
# Cloudflare DNS, SSL & Edge Routing Configuration
# ------------------------------------------------------------------------------

variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare Account ID"
  default     = "64757746387fc5fa02a362badccd83c1"
}

variable "cloudflare_zone_id" {
  type        = string
  description = "Cloudflare DNS Zone ID for healthkicks.eu"
  default     = "5a8edaea56b85f45796ff87919fab51f"
}

variable "cloudflare_tunnel_id" {
  type        = string
  description = "Cloudflare Zero Trust Tunnel ID for the FastAPI backend"
  default     = "a820102c-31c7-42ed-913c-dab954b993b2"
}

variable "domain_name" {
  type        = string
  description = "Primary apex domain name"
  default     = "healthkicks.eu"
}
