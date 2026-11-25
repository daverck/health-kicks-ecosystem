output "api_hostname" {
  description = "Public HTTPS API hostname routed through Cloudflare Tunnel"
  value       = cloudflare_dns_record.cname_api_tunnel.name
}

output "app_hostname" {
  description = "Public HTTPS Angular SPA hostname routed to CloudFront"
  value       = cloudflare_dns_record.cname_app.name
}
