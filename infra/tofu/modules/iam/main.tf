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
# 1. Aurora PostgreSQL IAM Authentication Policy (AuroraConnectPolicy)
# ------------------------------------------------------------------------------

resource "aws_iam_policy" "aurora_connect" {
  name = "AuroraConnectPolicy"

  lifecycle {
    ignore_changes = [description]
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "rds-db:connect"
        Resource = "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:*/postgres"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# 2. Mobile IoT Gateway IAM Role (HealthKicksMobileIoTRole)
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
            aws_iam_role.ecs_task_role.arn
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
      "arn:aws:ecr:*:*:repository/healthkicks-backend"
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
    sid    = "FrontendS3Deploy"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::healthkicks-frontend-app-*",
      "arn:aws:s3:::healthkicks-frontend-app-*/*"
    ]
  }

  statement {
    sid    = "FrontendCloudFrontInvalidation"
    effect = "Allow"
    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetInvalidation"
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
      "ecr:Get*",
      "ecr:List*",
      "iam:Get*",
      "iam:List*",
      "cloudfront:Get*",
      "cloudfront:List*",
      "acm:Describe*",
      "acm:List*",
      "acm:Get*",
      "ecs:*",
      "logs:*"
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
# 6. AWS ECS Fargate Roles (Task Execution Role & Task Runtime Role)
# ------------------------------------------------------------------------------

data "aws_iam_policy_document" "ecs_tasks_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution_role" {
  name               = "HealthKicksEcsExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_trust.json

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_ssm_secrets" {
  name = "HealthKicks-ECS-Execution-SSMSecretsPolicy"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowReadHealthKicksSSMParameters"
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "kms:Decrypt"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/healthkicks/${var.environment}/*"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "HealthKicksEcsTaskRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_trust.json

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_aurora_connect" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.aurora_connect.arn
}

resource "aws_iam_role_policy" "ecs_task_dynamodb" {
  name = "HealthKicks-ECS-DynamoDBPolicy"
  role = aws_iam_role.ecs_task_role.id

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
        Resource = [
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/healthkicks_telemetry",
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/healthkicks_telemetry/index/*",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_assume_mobile_iot" {
  name = "AllowAssumeHealthKicksMobileIoTRole"
  role = aws_iam_role.ecs_task_role.id

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

resource "aws_iam_role_policy" "ecs_task_iot_publish" {
  name = "HealthKicks-ECS-IoTPublishPolicy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowIoTPublishHapticCommands"
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:*:${data.aws_caller_identity.current.account_id}:topic/healthkicks/v1/*/commands/*"
      },
      {
        Sid      = "AllowIoTPublishFallAlertDownlink"
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:*:${data.aws_caller_identity.current.account_id}:topic/healthkicks/v1/users/*/fall-alert/status"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3_firmware" {
  name = "HealthKicks-ECS-S3FirmwarePolicy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowReadFirmwareReleasesBucket"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::healthkicks-firmware-releases*",
          "arn:aws:s3:::healthkicks-firmware-releases*/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_exec" {
  name = "HealthKicks-ECS-ExecPolicy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowECSExecChannels"
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions OIDC deployment"
  value       = aws_iam_role.github_actions_deploy.arn
}

output "mobile_iot_role_arn" {
  description = "ARN of the IAM role assumed for Mobile IoT Gateway"
  value       = aws_iam_role.mobile_iot_role.arn
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS Task Execution Role"
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS Task Runtime Role"
  value       = aws_iam_role.ecs_task_role.arn
}
