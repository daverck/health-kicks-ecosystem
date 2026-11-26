#!/usr/bin/env bash
set -euo pipefail

echo "[localstack-init] Provisioning DynamoDB tables and S3 buckets in eu-west-1..."

AWS_REGION="${AWS_DEFAULT_REGION:-eu-west-1}"

# 1. Telemetry table with sparse GSI for Studio session queries
if ! awslocal dynamodb describe-table --table-name healthkicks_telemetry --region "$AWS_REGION" >/dev/null 2>&1; then
  awslocal dynamodb create-table \
    --region "$AWS_REGION" \
    --table-name healthkicks_telemetry \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions \
      AttributeName=device_id,AttributeType=S \
      AttributeName=timestamp,AttributeType=N \
      AttributeName=session_id,AttributeType=S \
    --key-schema \
      AttributeName=device_id,KeyType=HASH \
      AttributeName=timestamp,KeyType=RANGE \
    --global-secondary-indexes '[
      {
        "IndexName": "gsi_session_timestamp",
        "KeySchema": [
          {"AttributeName": "session_id", "KeyType": "HASH"},
          {"AttributeName": "timestamp", "KeyType": "RANGE"}
        ],
        "Projection": {
          "ProjectionType": "INCLUDE",
          "NonKeyAttributes": ["ax", "ay", "az", "gx", "gy", "gz", "label"]
        }
      }
    ]' \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
  echo "[localstack-init] Created DynamoDB table: healthkicks_telemetry (with gsi_session_timestamp)"
else
  echo "[localstack-init] DynamoDB table healthkicks_telemetry already exists"
fi

# 2. OAuth one-time tickets table
if ! awslocal dynamodb describe-table --table-name healthkicks_oauth_tickets --region "$AWS_REGION" >/dev/null 2>&1; then
  awslocal dynamodb create-table \
    --region "$AWS_REGION" \
    --table-name healthkicks_oauth_tickets \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions AttributeName=ticket,AttributeType=S \
    --key-schema AttributeName=ticket,KeyType=HASH
  echo "[localstack-init] Created DynamoDB table: healthkicks_oauth_tickets"
fi

# 3. Distributed rate limits & idempotency table
if ! awslocal dynamodb describe-table --table-name healthkicks_rate_limits --region "$AWS_REGION" >/dev/null 2>&1; then
  awslocal dynamodb create-table \
    --region "$AWS_REGION" \
    --table-name healthkicks_rate_limits \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions AttributeName=key,AttributeType=S \
    --key-schema AttributeName=key,KeyType=HASH
  echo "[localstack-init] Created DynamoDB table: healthkicks_rate_limits"
fi

# 4. S3 firmware releases bucket
if ! awslocal s3api head-bucket --bucket healthkicks-firmware-releases-eu-west-1 --region "$AWS_REGION" >/dev/null 2>&1; then
  awslocal s3api create-bucket \
    --bucket healthkicks-firmware-releases-eu-west-1 \
    --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION"
  echo "[localstack-init] Created S3 bucket: healthkicks-firmware-releases-eu-west-1"
fi

echo "[localstack-init] AWS local initialization complete."
