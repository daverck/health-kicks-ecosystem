terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "github_repository" {
  type        = string
  description = "GitHub repository (owner/repo) authorized to assume the deployment role via OIDC"
  default     = "serckx/healthkicks-ecosystem"
}

variable "backend_repository" {
  type        = string
  description = "Submodule repository for the backend"
  default     = "serckx/health-kicks"
}

variable "frontend_repository" {
  type        = string
  description = "Submodule repository for the frontend"
  default     = "serckx/health-kicks-frontend"
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

resource "aws_iam_role_policy_attachment" "ec2_ecr_read" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# ------------------------------------------------------------------------------
# 2. EC2 Instance Profile (Matches live EC2ToAuroraInstanceProfile)
# ------------------------------------------------------------------------------

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "EC2ToAuroraInstanceProfile"
  role = aws_iam_role.ec2_role.name
}

# ------------------------------------------------------------------------------
# 3. AWS IAM OpenID Connect (OIDC) Provider for GitHub Actions
# ------------------------------------------------------------------------------

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]

  tags = {
    Project   = "HealthKicks"
    ManagedBy = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 4. GitHub Actions Deployment IAM Role
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
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_repository}:*",
        "repo:${var.backend_repository}:*",
        "repo:${var.frontend_repository}:*"
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

# Policy granting GitHub Actions permissions to push to ECR and deploy
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
