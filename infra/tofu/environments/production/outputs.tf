output "database_cluster_endpoint" {
  description = "Aurora Serverless v2 PostgreSQL writer endpoint"
  value       = module.database.cluster_endpoint
}

output "backend_ecr_repository_url" {
  description = "ECR Repository URL for Backend Docker images"
  value       = module.storage.backend_repo_url
}

output "frontend_ecr_repository_url" {
  description = "ECR Repository URL for Frontend Docker images"
  value       = module.storage.frontend_repo_url
}

output "dynamodb_telemetry_table" {
  description = "DynamoDB table name for high-throughput IMU telemetry"
  value       = module.storage.telemetry_table_name
}

output "github_actions_oidc_role_arn" {
  description = "IAM Role ARN for GitHub Actions deployment via OIDC"
  value       = module.iam.github_actions_role_arn
}

output "frontend_s3_bucket" {
  description = "S3 Bucket hosting the Angular SPA static assets"
  value       = module.frontend_cdn.s3_bucket_name
}

output "frontend_cloudfront_distribution_id" {
  description = "CloudFront Distribution ID for Angular SPA"
  value       = module.frontend_cdn.cloudfront_distribution_id
}

output "frontend_cloudfront_domain_name" {
  description = "CloudFront default domain name for Angular SPA (*.cloudfront.net)"
  value       = module.frontend_cdn.cloudfront_domain_name
}

output "app_runner_service_url" {
  description = "App Runner default service HTTPS URL"
  value       = module.app_runner.service_url
}

output "app_runner_service_arn" {
  description = "App Runner service ARN"
  value       = module.app_runner.service_arn
}

output "app_runner_dns_target" {
  description = "App Runner DNS target for CNAME in Cloudflare / OVH"
  value       = module.app_runner.dns_target
}

output "frontend_acm_dns_validation_records" {
  description = "DNS records to create in OVH for ACM certificate validation"
  value       = module.frontend_cdn.acm_dns_validation_records
}
