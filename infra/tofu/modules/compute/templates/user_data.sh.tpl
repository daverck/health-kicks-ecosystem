#!/usr/bin/env bash
# ==============================================================================
# HealthKicks - EC2 Cloud-Init Bootstrap Script (Ubuntu 24.04 LTS)
# ==============================================================================
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "==> 1. Updating base packages and installing dependencies..."
apt-get update -y
apt-get upgrade -y
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    unzip \
    jq \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw

echo "==> 2. Installing official Docker Engine & Docker Compose Plugin..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker service
systemctl enable --now docker
usermod -aG docker ubuntu

echo "==> 3. Installing AWS CLI v2..."
if ! command -v aws &> /dev/null; then
    curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install --update
    rm -rf /tmp/aws /tmp/awscliv2.zip
fi

echo "==> 4. Hardening SSH Daemon (/etc/ssh/sshd_config.d/99-healthkicks.conf)..."
cat <<'EOF' > /etc/ssh/sshd_config.d/99-healthkicks.conf
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 5
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

systemctl restart ssh || systemctl restart sshd

echo "==> 5. Configuring Fail2ban (/etc/fail2ban/jail.local)..."
cat <<'EOF' > /etc/fail2ban/jail.local
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5
banaction = iptables-multiport

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = systemd

[nginx-limit-req]
enabled  = true
port     = http,https
logpath  = /var/log/nginx/error.log
maxretry = 10
findtime = 1m
bantime  = 1h
EOF

systemctl enable --now fail2ban
systemctl restart fail2ban

echo "==> 6. Configuring Nginx Reverse Proxy & Rate Limiting..."
# Webroot for automated Let's Encrypt renewal
mkdir -p /var/www/letsencrypt
chown -R www-data:www-data /var/www/letsencrypt

# Rate limiting definitions in /etc/nginx/conf.d/ratelimit.conf
cat <<'EOF' > /etc/nginx/conf.d/ratelimit.conf
limit_req_zone $binary_remote_addr zone=api_auth:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=api_general:10m rate=30r/s;
EOF

# Upstream definition for in-host Blue/Green slot switching
cat <<'EOF' > /etc/nginx/conf.d/healthkicks-upstream.conf
upstream healthkicks_backend {
    server 127.0.0.1:8000;
    keepalive 16;
}
EOF

# Nginx main site configuration
cat <<'EOF' > /etc/nginx/sites-available/healthkicks
${nginx_site_conf}
EOF

# Link and test site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/healthkicks /etc/nginx/sites-enabled/healthkicks

echo "==> 7. Setting up persistent logs directory for containers..."
mkdir -p /home/ubuntu/logs
chmod 777 /home/ubuntu/logs
chown -R ubuntu:ubuntu /home/ubuntu/logs

echo "==> 8. Verifying Nginx and reloading service..."
if nginx -t; then
    systemctl enable --now nginx
    systemctl reload nginx
else
    echo "Notice: Nginx config has SSL directives that require Let's Encrypt certificates before first start."
fi

echo "==> [SUCCESS] HealthKicks host bootstrap completed successfully!"
