# ==============================================================================
# HealthKicks Cloudflare DNS, SSL/TLS & Edge Redirects Variables
# ==============================================================================

variable "zone_id" {
  type        = string
  description = "Cloudflare DNS Zone ID"
}

variable "domain_name" {
  type        = string
  description = "Primary apex domain name"
  default     = "healthkicks.eu"
}

variable "tunnel_id" {
  type        = string
  description = "Cloudflare Zero Trust Tunnel ID serving api.<domain>"
}

variable "cloudfront_domain_name" {
  type        = string
  description = "CloudFront distribution target domain for app.<domain>"
}

variable "acm_validation_record_name" {
  type        = string
  description = "ACM DNS validation CNAME record name"
}

variable "acm_validation_record_value" {
  type        = string
  description = "ACM DNS validation CNAME record target"
}
