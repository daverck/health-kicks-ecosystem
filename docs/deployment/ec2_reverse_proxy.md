# EC2 Nginx Reverse Proxy & SSL Configuration

This document specifies the official Nginx reverse-proxy configuration and Let's Encrypt TLS setup deployed on the AWS EC2 host (`ip-172-31-41-131`).

---

## 1. Architectural Overview

```text
[ Browser / Mobile Client ]
           │
           │ HTTPS (Port 443) / HTTP (Port 80)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AWS EC2 Host (Ubuntu)                       │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 Nginx Host Reverse Proxy                │   │
│   │   - Let's Encrypt TLS (api / app)                       │   │
│   │   - HTTP -> HTTPS 301 Permanent Redirect                │   │
│   │   - WebSocket Upgrade handling                          │   │
│   │   - Port leak mitigation (proxy_redirect)               │   │
│   └───────────────┬─────────────────────────┬───────────────┘   │
│                   │                         │                   │
│        proxy_pass │                         │ proxy_pass        │
│    127.0.0.1:8000 │                         │ 127.0.0.1:8080    │
│                   ▼                         ▼                   │
│   ┌───────────────────────────┐ ┌───────────────────────────┐   │
│   │   healthkicks-backend     │ │   healthkicks-frontend    │   │
│   │   (FastAPI Docker Container)│ │   (Angular Nginx Docker)  │   │
│   └───────────────────────────┘ └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

- **Backend API**: Accessible at `https://api.healthkicks.eu` (proxied to `http://healthkicks_backend`, dynamically alternating between container ports `8000` (`healthkicks-blue`) and `8001` (`healthkicks-green`) for zero-downtime deployment).
- **Frontend App**: Accessible at `https://app.healthkicks.eu` (proxied to container port 8080).
- **Apex / WWW**: `https://healthkicks.eu` and `https://www.healthkicks.eu` redirect 301 to `https://app.healthkicks.eu`.

---

## 2. Dynamic Blue/Green Upstream (`/etc/nginx/conf.d/healthkicks-upstream.conf`)

Managed automatically by the CI/CD deployment pipeline (`health-kicks/.github/workflows/deploy.yml`):

```nginx
upstream healthkicks_backend {
    server 127.0.0.1:8000; # Alternates between 8000 (blue) and 8001 (green)
    keepalive 16;
}
```

## 3. Nginx Configuration (`/etc/nginx/sites-available/healthkicks`)

```nginx
# ==============================================================================
# 1. HTTP to HTTPS Redirection (Port 80)
# ==============================================================================
server {
    listen 80;
    listen [::]:80;
    server_name api.healthkicks.eu app.healthkicks.eu healthkicks.eu www.healthkicks.eu;

    # Allow Let's Encrypt automated challenge validation without stopping Nginx
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
        allow all;
    }

    # Permanent 301 redirect for all HTTP requests to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# ==============================================================================
# 2. FastAPI Backend API (api.healthkicks.eu)
# ==============================================================================
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name api.healthkicks.eu;

    # Let's Encrypt SSL certificates (multi-domain SAN)
    ssl_certificate /etc/letsencrypt/live/api.healthkicks.eu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.healthkicks.eu/privkey.pem;

    # Hardened SSL parameters
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Maximum upload payload size (for firmware OTA binaries & ML model artifacts)
    client_max_body_size 50M;

    location / {
        proxy_pass http://healthkicks_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;

        # Mitigate internal container port leaking on 30x redirects
        proxy_redirect http://healthkicks_backend/ /;
        proxy_redirect http://127.0.0.1:8000/ /;
        proxy_redirect http://127.0.0.1:8001/ /;
        proxy_redirect http://$host:8000/ https://$host/;
        proxy_redirect http://$host:8001/ https://$host/;

        # WebSocket & streaming support for real-time telemetry and studio feeds
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}

# ==============================================================================
# 3. Angular Frontend Web App (app.healthkicks.eu)
# ==============================================================================
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name app.healthkicks.eu;

    ssl_certificate /etc/letsencrypt/live/api.healthkicks.eu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.healthkicks.eu/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;

        # Mitigate internal container port leaking on prerendered directory redirects
        proxy_redirect http://127.0.0.1:8080/ /;
        proxy_redirect http://$host:8080/ https://$host/;
    }
}

# ==============================================================================
# 4. Apex & WWW HTTPS Redirection (healthkicks.eu, www.healthkicks.eu -> app.healthkicks.eu)
# ==============================================================================
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name healthkicks.eu www.healthkicks.eu;

    ssl_certificate /etc/letsencrypt/live/api.healthkicks.eu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.healthkicks.eu/privkey.pem;

    location / {
        return 301 https://app.healthkicks.eu$request_uri;
    }
}

```

---

## 3. Why `proxy_redirect` & `X-Forwarded-Port` are Crucial

### Problem: Container Port Leakage

When upstream services (FastAPI/Uvicorn or container Nginx) return HTTP redirects (`301`, `302`, `307`):

- FastAPI issues trailing-slash redirects (e.g. `/api/v1/auth` -> `/api/v1/auth/`).
- Angular container Nginx issues directory redirects (e.g. `/login` -> `/login/` for prerendered routes).
- If upstream only sees its local listening socket (`:8000` or `:8080`), it appends that internal port to the HTTP `Location` header (e.g. `http://app.healthkicks.eu:8080/login/`).

### Solution

1. `proxy_set_header X-Forwarded-Port 443;` explicitly informs Uvicorn and upstream proxies of the public client-facing port.
2. `proxy_redirect http://...:PORT/ ...` instructs host Nginx to intercept `Location` response headers and rewrite any leaked internal ports/protocols back to `https://$host/`.
3. In `health-kicks-frontend/nginx.conf`, `port_in_redirect off;` and `absolute_redirect off;` ensure the container emits relative redirects (e.g. `Location: /login/`), completely preventing port leakage at the source.

---

## 4. Let's Encrypt Multi-Domain SSL Maintenance

The multi-domain certificate covers:

- `api.healthkicks.eu`
- `app.healthkicks.eu`
- `healthkicks.eu`
- `www.healthkicks.eu`

### Renewal via Webroot (Zero Downtime)

Because all HTTP port 80 traffic routes `.well-known/acme-challenge/` to `/var/www/letsencrypt`, renewals run transparently without stopping Nginx:

```bash
sudo certbot renew --dry-run
```

To reload Nginx automatically upon certificate renewal, verify `/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh`:

```bash
#!/bin/sh
systemctl reload nginx
```

chmod +x on this script ensures seamless automated renewals.

---

## 5. Synthetic Monitoring & Public Status Page

External continuous availability monitoring and public telemetry status are provided via UptimeRobot:

- **Public Status Page**: [https://stats.uptimerobot.com/c5m9EOGfwq](https://stats.uptimerobot.com/c5m9EOGfwq)
- **Monitored Services**:
  - `HealthKicks API`: `https://api.healthkicks.eu/health` (5-minute HTTP 200 health check)
  - `HealthKicks Web App`: `https://app.healthkicks.eu` (5-minute HTTP 200 health check)
- **Incident Escalation**: Real-time outage and recovery notifications are delivered via native Discord Webhooks directly to the engineering team (`#alerts`).
- **Custom Domain (Optional)**: Add a CNAME DNS record in OVH (`status.healthkicks.eu` -> `stats.uptimerobot.com`) to brand the status page.
