output "elastic_ip" {
  description = "Permanent Elastic IP for Cloudflare DNS A-record mapping"
  value       = module.compute.elastic_ip
}

output "ec2_instance_id" {
  description = "EC2 Host Instance ID"
  value       = module.compute.instance_id
}

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
