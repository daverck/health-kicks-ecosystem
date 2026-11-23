terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "github_repository" {
  type        = string
  description = "GitHub repository (owner/repo) authorized to assume the deployment role via OIDC"
  default     = "daverck/health-kicks-ecosystem"
}

variable "backend_repository" {
  type        = string
  description = "Submodule repository for the backend"
  default     = "daverck/health-kicks"
}

variable "frontend_repository" {
  type        = string
  description = "Submodule repository for the frontend"
  default     = "daverck/health-kicks-frontend"
}

variable "mobile_repository" {
  type        = string
  description = "Submodule repository for the mobile app"
  default     = "daverck/health-kicks-mobile"
}

variable "firmware_repository" {
  type        = string
  description = "Submodule repository for the firmware"
  default     = "daverck/health-kicks-esp32-s3"
}

# ------------------------------------------------------------------------------
# 1. EC2 Instance IAM Role (Matches live EC2ToAuroraBDDAuthRole)
# ------------------------------------------------------------------------------

data "aws_iam_policy_document" "ec2_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2_role" {
  name               = "EC2ToAuroraBDDAuthRole"
  assume_role_policy = data.aws_iam_policy_document.ec2_trust.json

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

# A. ECR Pull Permissions (AmazonEC2ContainerRegistryReadOnly)
resource "aws_iam_role_policy_attachment" "ec2_ecr_read" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# B. Aurora PostgreSQL IAM Authentication (AuroraConnectPolicy)
resource "aws_iam_policy" "aurora_connect" {
  name = "AuroraConnectPolicy"

  lifecycle {
    ignore_changes = [description]
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "rds-db:connect"
        Resource = [
          "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:*/postgres",
          "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:cluster-DGAWIPS4B6EG4OZY7A3BIBNNA4/postgres",
          "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:db-267CCZGLWF3DOX5LTBY4KFFURI/postgres"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_aurora_connect" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.aurora_connect.arn
}

# C. DynamoDB Access for IMU Telemetry (HealthKicks-EC2-DynamoDBPolicy)
resource "aws_iam_role_policy" "ec2_dynamodb" {
  name = "HealthKicks-EC2-DynamoDBPolicy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowHealthKicksDynamoDBAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/healthkicks_telemetry"
      }
    ]
  })
}

# D. STS AssumeRole for Mobile IoT Gateway (AllowAssumeHealthKicksMobileIoTRole)
resource "aws_iam_role_policy" "ec2_assume_mobile_iot" {
  name = "AllowAssumeHealthKicksMobileIoTRole"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = aws_iam_role.mobile_iot_role.arn
      }
    ]
  })
}

# E. IoT Publish Policy for Haptics & Fall Alerts (HealthKicks-EC2-IoTPublishPolicy)
resource "aws_iam_role_policy" "ec2_iot_publish" {
  name = "HealthKicks-EC2-IoTPublishPolicy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowIoTPublishHapticCommands"
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/healthkicks/v1/*/commands/*"
      },
      {
        Sid      = "AllowIoTPublishFallAlertDownlink"
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/healthkicks/v1/users/*/fall-alert/status"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# 2. EC2 Instance Profile (Matches live EC2ToAuroraInstanceProfile)
# ------------------------------------------------------------------------------

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "EC2ToAuroraInstanceProfile"
  role = aws_iam_role.ec2_role.name
}

# ------------------------------------------------------------------------------
# 3. Mobile IoT Gateway IAM Role (HealthKicksMobileIoTRole)
# ------------------------------------------------------------------------------

resource "aws_iam_role" "mobile_iot_role" {
  name = "HealthKicksMobileIoTRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = [
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
            aws_iam_role.ec2_role.arn
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

resource "aws_iam_role_policy" "mobile_iot_policy" {
  name = "HealthKicksMobileIoTPolicy"
  role = aws_iam_role.mobile_iot_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect",
          "iot:Publish",
          "iot:Subscribe",
          "iot:Receive"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# 4. AWS IAM OpenID Connect (OIDC) Provider for GitHub Actions
# ------------------------------------------------------------------------------

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = [
    "sts.amazonaws.com"
  ]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c5824a682c4c424e45d6542a26d73fe0a4b397b",
    "ab9d0263244dd0326eb67015705a667e79cfe998"
  ]

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 5. GitHub Actions Deployment IAM Role
# ------------------------------------------------------------------------------

data "aws_iam_policy_document" "github_actions_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        # health-kicks-ecosystem (root)
        "repo:${var.github_repository}:*",
        "repo:daverck@7854728/health-kicks-ecosystem@*:*",
        # health-kicks (backend)
        "repo:${var.backend_repository}:*",
        "repo:daverck@7854728/health-kicks@*:*",
        # health-kicks-frontend (frontend)
        "repo:${var.frontend_repository}:*",
        "repo:daverck@7854728/health-kicks-frontend@*:*",
        # health-kicks-mobile (mobile)
        "repo:${var.mobile_repository}:*",
        "repo:daverck@7854728/health-kicks-mobile@*:*",
        # health-kicks-esp32-s3 (firmware)
        "repo:${var.firmware_repository}:*",
        "repo:daverck@7854728/health-kicks-esp32-s3@*:*"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = "healthkicks-github-actions-deploy-role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_trust.json

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

data "aws_iam_policy_document" "github_actions_permissions" {
  statement {
    sid    = "ECRAuthToken"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "ECRPushPull"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:DescribeImages",
      "ecr:BatchGetImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage"
    ]
    resources = [
      "arn:aws:ecr:*:*:repository/healthkicks-backend",
      "arn:aws:ecr:*:*:repository/healthkicks-frontend"
    ]
  }

  statement {
    sid    = "OpenTofuStateAccess"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "OpenTofuPlanReadAccess"
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "rds:Describe*",
      "rds:ListTagsForResource",
      "dynamodb:Describe*",
      "dynamodb:ListTagsOfResource",
      "s3:Get*",
      "s3:List*",
      "ecr:Describe*",
      "ecr:ListTagsForResource",
      "iam:Get*",
      "iam:List*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "github_actions_deploy_policy" {
  name        = "healthkicks-github-actions-deploy-policy"
  description = "Allows GitHub Actions CI/CD to push Docker images and deploy"
  policy      = data.aws_iam_policy_document.github_actions_permissions.json
}

resource "aws_iam_role_policy_attachment" "github_actions_deploy_attach" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.github_actions_deploy_policy.arn
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "ec2_instance_profile_name" {
  description = "Name of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions OIDC deployment"
  value       = aws_iam_role.github_actions_deploy.arn
}

output "mobile_iot_role_arn" {
  description = "ARN of the IAM role assumed for Mobile IoT Gateway"
  value       = aws_iam_role.mobile_iot_role.arn
}
