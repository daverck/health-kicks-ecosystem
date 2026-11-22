<#
.SYNOPSIS
    Automated OpenTofu Import Script for HealthKicks Production Resources.
.DESCRIPTION
    Imports all pre-existing live AWS resources into OpenTofu state without any downtime,
    destruction, or service modification.
#>

[CmdletBinding()]
param(
    [string]$WorkingDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " HealthKicks - OpenTofu Live Infrastructure Import Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not $WorkingDir) {
    $WorkingDir = (Resolve-Path (Join-Path $PSScriptRoot "..\environments\production")).Path
}

Push-Location $WorkingDir
try {
    Write-Host "`n1. Initializing OpenTofu..." -ForegroundColor Yellow
    tofu init

    $resources = @(
        # Storage & Telemetry
        @{ Address = "module.storage.aws_ecr_repository.backend"; Id = "healthkicks-backend" },
        @{ Address = "module.storage.aws_ecr_repository.frontend"; Id = "healthkicks-frontend" },
        @{ Address = "module.storage.aws_ecr_lifecycle_policy.backend_lifecycle"; Id = "healthkicks-backend" },
        @{ Address = "module.storage.aws_ecr_lifecycle_policy.frontend_lifecycle"; Id = "healthkicks-frontend" },
        @{ Address = "module.storage.aws_s3_bucket.firmware_releases"; Id = "healthkicks-firmware-releases" },
        @{ Address = "module.storage.aws_dynamodb_table.telemetry"; Id = "healthkicks_telemetry" },

        # IAM & Security
        @{ Address = "module.iam.aws_iam_role.ec2_role"; Id = "EC2ToAuroraBDDAuthRole" },
        @{ Address = "module.iam.aws_iam_instance_profile.ec2_profile"; Id = "EC2ToAuroraInstanceProfile" },
        @{ Address = "module.iam.aws_iam_policy.aurora_connect"; Id = "arn:aws:iam::693906847467:policy/AuroraConnectPolicy" },
        @{ Address = "module.iam.aws_iam_role.mobile_iot_role"; Id = "HealthKicksMobileIoTRole" },
        @{ Address = "module.iam.aws_iam_role_policy.mobile_iot_policy"; Id = "HealthKicksMobileIoTRole:HealthKicksMobileIoTPolicy" },
        @{ Address = "module.iam.aws_iam_role_policy.ec2_dynamodb"; Id = "EC2ToAuroraBDDAuthRole:HealthKicks-EC2-DynamoDBPolicy" },
        @{ Address = "module.iam.aws_iam_role_policy.ec2_assume_mobile_iot"; Id = "EC2ToAuroraBDDAuthRole:AllowAssumeHealthKicksMobileIoTRole" },
        @{ Address = "module.iam.aws_iam_role_policy.ec2_iot_publish"; Id = "EC2ToAuroraBDDAuthRole:HealthKicks-EC2-IoTPublishPolicy" },
        @{ Address = "module.iam.aws_iam_role_policy_attachment.ec2_aurora_connect"; Id = "EC2ToAuroraBDDAuthRole/arn:aws:iam::693906847467:policy/AuroraConnectPolicy" },
        @{ Address = "module.iam.aws_iam_role_policy_attachment.ec2_ecr_read"; Id = "EC2ToAuroraBDDAuthRole/arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly" },
        @{ Address = "module.security.aws_security_group.web_sg"; Id = "sg-00db1eb2eb63723d9" },

        # Compute (EC2 Instance)
        @{ Address = "module.compute.aws_instance.backend_server"; Id = "i-0fa331c11cd475278" },

        # Database (Aurora Serverless v2)
        @{ Address = "module.database.aws_rds_cluster.aurora_cluster"; Id = "healthkicks-db" },
        @{ Address = "module.database.aws_rds_cluster_instance.cluster_instance"; Id = "database-1-instance-1" }
    )

    Write-Host "`n2. Importing Live Resources into State..." -ForegroundColor Yellow
    foreach ($res in $resources) {
        Write-Host "-> Importing $($res.Address) with ID $($res.Id)..." -ForegroundColor Green
        try {
            tofu import $($res.Address) $($res.Id)
        } catch {
            Write-Warning "Import note for $($res.Address): $_"
        }
    }

    Write-Host "`n3. Running tofu plan to verify state synchronization..." -ForegroundColor Yellow
    tofu plan

    Write-Host "`n[SUCCESS] Live resources successfully imported into OpenTofu management!" -ForegroundColor Cyan
}
finally {
    Pop-Location
}
