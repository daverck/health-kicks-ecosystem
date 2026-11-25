output "s3_bucket_name" {
  description = "Name of the S3 bucket hosting Angular SPA assets"
  value       = aws_s3_bucket.frontend.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket hosting Angular SPA assets"
  value       = aws_s3_bucket.frontend.arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID for edge cache invalidations"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_distribution_arn" {
  description = "CloudFront Distribution ARN"
  value       = aws_cloudfront_distribution.frontend.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront Distribution default domain name (*.cloudfront.net)"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate created in us-east-1"
  value       = aws_acm_certificate.frontend.arn
}

output "acm_certificate_status" {
  description = "Validation status of the ACM certificate"
  value       = aws_acm_certificate.frontend.status
}

output "acm_dns_validation_records" {
  description = "DNS records managed in Cloudflare for ACM certificate validation"
  value = [
    for dvo in aws_acm_certificate.frontend.domain_validation_options : {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  ]
}
