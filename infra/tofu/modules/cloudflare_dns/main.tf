# ==============================================================================
# HealthKicks Cloudflare DNS, SSL/TLS & Redirects Module (Provider v5)
# ==============================================================================

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
  }
}

# ------------------------------------------------------------------------------
# 1. OVH Mail & Webmail DNS Records (Strictly DNS Only / proxied = false)
# ------------------------------------------------------------------------------

resource "cloudflare_dns_record" "mx_ovh_1" {
  zone_id  = var.zone_id
  name     = var.domain_name
  type     = "MX"
  content  = "mx1.mail.ovh.net"
  priority = 1
  ttl      = 3600
  proxied  = false
}

resource "cloudflare_dns_record" "mx_ovh_2" {
  zone_id  = var.zone_id
  name     = var.domain_name
  type     = "MX"
  content  = "mx2.mail.ovh.net"
  priority = 5
  ttl      = 3600
  proxied  = false
}

resource "cloudflare_dns_record" "mx_ovh_3" {
  zone_id  = var.zone_id
  name     = var.domain_name
  type     = "MX"
  content  = "mx3.mail.ovh.net"
  priority = 100
  ttl      = 3600
  proxied  = false
}

resource "cloudflare_dns_record" "txt_spf" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "TXT"
  content = "v=spf1 include:mx.ovh.com -all"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_mail" {
  zone_id = var.zone_id
  name    = "mail.${var.domain_name}"
  type    = "CNAME"
  content = "ssl0.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_smtp" {
  zone_id = var.zone_id
  name    = "smtp.${var.domain_name}"
  type    = "CNAME"
  content = "ssl0.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_imap" {
  zone_id = var.zone_id
  name    = "imap.${var.domain_name}"
  type    = "CNAME"
  content = "ssl0.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_pop3" {
  zone_id = var.zone_id
  name    = "pop3.${var.domain_name}"
  type    = "CNAME"
  content = "ssl0.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_autoconfig" {
  zone_id = var.zone_id
  name    = "autoconfig.${var.domain_name}"
  type    = "CNAME"
  content = "mailconfig.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_autodiscover" {
  zone_id = var.zone_id
  name    = "autodiscover.${var.domain_name}"
  type    = "CNAME"
  content = "mailconfig.ovh.net"
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "srv_autodiscover" {
  zone_id  = var.zone_id
  name     = "_autodiscover._tcp.${var.domain_name}"
  type     = "SRV"
  priority = 0
  ttl      = 3600
  proxied  = false

  data = {
    priority = 0
    weight   = 0
    port     = 443
    target   = "mailconfig.ovh.net"
  }
}

resource "cloudflare_dns_record" "srv_imaps" {
  zone_id  = var.zone_id
  name     = "_imaps._tcp.${var.domain_name}"
  type     = "SRV"
  priority = 0
  ttl      = 3600
  proxied  = false

  data = {
    priority = 0
    weight   = 0
    port     = 993
    target   = "ssl0.ovh.net"
  }
}

resource "cloudflare_dns_record" "srv_submission" {
  zone_id  = var.zone_id
  name     = "_submission._tcp.${var.domain_name}"
  type     = "SRV"
  priority = 0
  ttl      = 3600
  proxied  = false

  data = {
    priority = 0
    weight   = 0
    port     = 465
    target   = "ssl0.ovh.net"
  }
}

# ------------------------------------------------------------------------------
# 2. Frontend Angular SPA (AWS CloudFront & ACM Validation - DNS Only)
# ------------------------------------------------------------------------------

resource "cloudflare_dns_record" "cname_app" {
  zone_id = var.zone_id
  name    = "app.${var.domain_name}"
  type    = "CNAME"
  content = var.cloudfront_domain_name
  ttl     = 3600
  proxied = false
}

resource "cloudflare_dns_record" "cname_app_acm_validation" {
  zone_id = var.zone_id
  name    = trimsuffix(var.acm_validation_record_name, ".")
  type    = "CNAME"
  content = trimsuffix(var.acm_validation_record_value, ".")
  ttl     = 3600
  proxied = false
}

# ------------------------------------------------------------------------------
# 3. Backend API Tunnel & Root/WWW Redirect Originless Entries (Proxied)
# ------------------------------------------------------------------------------

resource "cloudflare_dns_record" "cname_api_tunnel" {
  zone_id = var.zone_id
  name    = "api.${var.domain_name}"
  type    = "CNAME"
  content = "${var.tunnel_id}.cfargotunnel.com"
  ttl     = 1
  proxied = true
}

resource "cloudflare_dns_record" "aaaa_root" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "AAAA"
  content = "100::"
  ttl     = 1
  proxied = true
}

resource "cloudflare_dns_record" "cname_www" {
  zone_id = var.zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  content = var.domain_name
  ttl     = 1
  proxied = true
}

# ------------------------------------------------------------------------------
# 4. Zone SSL/TLS Settings & Dynamic 301 Redirect Ruleset
# ------------------------------------------------------------------------------

resource "cloudflare_zone_setting" "ssl" {
  zone_id    = var.zone_id
  setting_id = "ssl"
  value      = "full"
}

resource "cloudflare_zone_setting" "always_use_https" {
  zone_id    = var.zone_id
  setting_id = "always_use_https"
  value      = "on"
}

resource "cloudflare_ruleset" "root_redirect" {
  zone_id     = var.zone_id
  name        = "default"
  description = ""
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"

  rules = [
    {
      action      = "redirect"
      description = "Redirect root and www to https://app.healthkicks.eu"
      enabled     = true
      expression  = "(http.host in {\"${var.domain_name}\" \"www.${var.domain_name}\"})"

      action_parameters = {
        from_value = {
          preserve_query_string = true
          status_code           = 301
          target_url = {
            value = "https://app.${var.domain_name}"
          }
        }
      }
    }
  ]
}
