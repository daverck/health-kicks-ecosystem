output "service_id" {
  description = "Unique ID of the App Runner service"
  value       = aws_apprunner_service.backend_service.service_id
}

output "service_arn" {
  description = "ARN of the App Runner service"
  value       = aws_apprunner_service.backend_service.arn
}

output "service_url" {
  description = "Default HTTPS domain name assigned by App Runner"
  value       = aws_apprunner_service.backend_service.service_url
}

output "service_status" {
  description = "Current operational status of the service"
  value       = aws_apprunner_service.backend_service.status
}

output "vpc_connector_arn" {
  description = "ARN of the VPC Connector"
  value       = aws_apprunner_vpc_connector.backend_vpc_connector.arn
}

output "dns_target" {
  description = "Target domain for CNAME record in Cloudflare DNS"
  value       = var.enable_custom_domain && length(aws_apprunner_custom_domain_association.api_custom_domain) > 0 ? aws_apprunner_custom_domain_association.api_custom_domain[0].dns_target : aws_apprunner_service.backend_service.service_url
}

output "certificate_validation_records" {
  description = "Certificate validation CNAME records for custom domain"
  value       = var.enable_custom_domain && length(aws_apprunner_custom_domain_association.api_custom_domain) > 0 ? aws_apprunner_custom_domain_association.api_custom_domain[0].certificate_validation_records : []
}
