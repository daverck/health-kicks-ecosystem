variable "environment" {
  description = "Target deployment environment (e.g. production, staging)"
  type        = string
}

variable "domain_name" {
  description = "Custom domain name for the frontend Angular application"
  type        = string
  default     = "app.healthkicks.eu"
}

variable "enable_custom_domain" {
  description = "Whether to attach custom domain and ACM certificate to CloudFront (set to true after validating ACM CNAME in OVH DNS)"
  type        = bool
  default     = false
}
