#!/bin/bash
set -euo pipefail

# ==============================================================================
# HealthKicks - OVH DynHost Dynamic DNS Updater
# Authentication is managed securely via ~/.netrc (no credentials in this script)
# ==============================================================================

DYN_HOST="healthkicks.eu"
LOG_FILE="/var/log/ovh_dynhost.log"
NETRC_FILE="${HOME}/.netrc"

# Ensure ~/.netrc exists
if [ ! -f "${NETRC_FILE}" ]; then
  echo "Error: ${NETRC_FILE} not found. Please create it with credentials." >&2
  exit 1
fi

# Call OVH DynHost endpoint using credentials from ~/.netrc
# OVH automatically detects the instance's public IP (56.228.24.7) from the connection.
RESPONSE=$(curl -sn "https://www.ovh.com/nic/update?system=dyndns&hostname=${DYN_HOST}")

# Log result with timestamp
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
LOG_ENTRY="${TIMESTAMP} - Response: ${RESPONSE}"

if [ -w "${LOG_FILE}" 2>/dev/null ] || [ -w "$(dirname "${LOG_FILE}")" ]; then
  echo "${LOG_ENTRY}" >> "${LOG_FILE}"
fi

echo "${LOG_ENTRY}"
