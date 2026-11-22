#!/usr/bin/env bash
# ==============================================================================
# HealthKicks - OpenTofu Live Infrastructure Import Script (Linux/macOS)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../environments/production"

echo "============================================================"
echo " HealthKicks - OpenTofu Live Infrastructure Import Script"
echo "============================================================"

echo ""
echo "1. Initializing OpenTofu..."
tofu init

echo ""
echo "2. Importing Live Resources into State..."
tofu import module.storage.aws_ecr_repository.backend healthkicks-backend || true
tofu import module.storage.aws_ecr_repository.frontend healthkicks-frontend || true
tofu import module.storage.aws_ecr_lifecycle_policy.backend_lifecycle healthkicks-backend || true
tofu import module.storage.aws_ecr_lifecycle_policy.frontend_lifecycle healthkicks-frontend || true
tofu import module.storage.aws_s3_bucket.firmware_releases healthkicks-firmware-releases || true
tofu import module.storage.aws_dynamodb_table.telemetry healthkicks_telemetry || true

tofu import module.iam.aws_iam_role.ec2_role EC2ToAuroraBDDAuthRole || true
tofu import module.iam.aws_iam_instance_profile.ec2_profile EC2ToAuroraInstanceProfile || true
tofu import module.iam.aws_iam_policy.aurora_connect arn:aws:iam::693906847467:policy/AuroraConnectPolicy || true
tofu import module.iam.aws_iam_role.mobile_iot_role HealthKicksMobileIoTRole || true
tofu import module.iam.aws_iam_role_policy.mobile_iot_policy HealthKicksMobileIoTRole:HealthKicksMobileIoTPolicy || true
tofu import module.iam.aws_iam_role_policy.ec2_dynamodb EC2ToAuroraBDDAuthRole:HealthKicks-EC2-DynamoDBPolicy || true
tofu import module.iam.aws_iam_role_policy.ec2_assume_mobile_iot EC2ToAuroraBDDAuthRole:AllowAssumeHealthKicksMobileIoTRole || true
tofu import module.iam.aws_iam_role_policy.ec2_iot_publish EC2ToAuroraBDDAuthRole:HealthKicks-EC2-IoTPublishPolicy || true
tofu import module.iam.aws_iam_role_policy_attachment.ec2_aurora_connect EC2ToAuroraBDDAuthRole/arn:aws:iam::693906847467:policy/AuroraConnectPolicy || true
tofu import module.iam.aws_iam_role_policy_attachment.ec2_ecr_read EC2ToAuroraBDDAuthRole/arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly || true
tofu import module.security.aws_security_group.web_sg sg-00db1eb2eb63723d9 || true

tofu import module.compute.aws_instance.backend_server i-0fa331c11cd475278 || true

tofu import module.database.aws_rds_cluster.aurora_cluster healthkicks-db || true
tofu import module.database.aws_rds_cluster_instance.cluster_instance database-1-instance-1 || true

echo ""
echo "3. Running tofu plan to verify synchronization..."
tofu plan

echo ""
echo "[SUCCESS] Live resources successfully imported into OpenTofu management!"
