# ==============================================================================
# HealthKicks Production Environment Architecture (OpenTofu)
# ==============================================================================

locals {
  ssm_secret_keys = [
    "AWS_IOT_ENDPOINT",
    "AWS_IOT_ROLE_ARN",
    "HEALTHKICKS_INGEST_TOKEN",
    "HEALTHKICKS_GOOGLE_CLIENT_ID",
    "HEALTHKICKS_GOOGLE_CLIENT_SECRET",
    "HEALTHKICKS_GOOGLE_REDIRECT_URI",
    "HEALTHKICKS_GOOGLE_REDIRECT_URI_MOBILE",
    "HEALTHKICKS_JWT_SECRET",
    "HEALTHKICKS_JWT_ALGORITHM",
    "HEALTHKICKS_ACCESS_TOKEN_EXPIRE_MINUTES",
    "HEALTHKICKS_PUBLIC_ORIGINS",
    "HEALTHKICKS_AZURE_CLIENT_ID",
    "HEALTHKICKS_AZURE_CLIENT_SECRET",
    "HEALTHKICKS_AZURE_TENANT_ID",
    "HEALTHKICKS_AZURE_REDIRECT_URI",
    "HEALTHKICKS_AZURE_REDIRECT_URI_MOBILE",
    "HEALTHKICKS_PSEUDONYMIZATION_PEPPER",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "SMTP_FROM_NAME",
    "PUBLIC_BASE_URL",
    "HEALTHKICKS_FRONTEND_URL",
    "FALL_ALERT_ACK_SECRET",
    "SENTRY_DSN",
  ]
}

# 1. Storage: ECR repositories & DynamoDB in eu-west-1, S3 OTA bucket pinned in eu-north-1
module "storage" {
  source = "../../modules/storage"
  providers = {
    aws            = aws
    aws.eu_north_1 = aws.eu_north_1
  }

  environment             = var.environment
  max_ecr_images_retained = 3
}

# 2. IAM: ECS Fargate Roles, Mobile IoT Role, and GitHub Actions OIDC Role
module "iam" {
  source            = "../../modules/iam"
  environment       = var.environment
  github_repository = var.github_repository
}

# 3. Security: Security Groups for ECS Fargate tasks & Aurora PostgreSQL
module "security" {
  source                      = "../../modules/security"
  vpc_id                      = var.vpc_id
  environment                 = var.environment
  allow_direct_http_port_8000 = !var.enable_cloudflare_tunnel
}

# 4. Compute: ECS Fargate Spot (+ optional Cloudflare Tunnel sidecar)
module "ecs_fargate" {
  source = "../../modules/ecs_fargate"

  environment          = var.environment
  service_name         = "healthkicks-backend"
  image_repository_url = module.storage.backend_repo_url
  image_tag            = var.backend_image_tag
  execution_role_arn   = module.iam.ecs_execution_role_arn
  task_role_arn        = module.iam.ecs_task_role_arn
  subnet_ids           = var.database_subnet_ids
  security_group_id    = module.security.ecs_tasks_security_group_id

  cpu           = var.fargate_cpu
  memory        = var.fargate_memory
  desired_count = var.fargate_desired_count
  use_spot      = var.fargate_use_spot

  enable_cloudflare_tunnel        = var.enable_cloudflare_tunnel
  cloudflare_tunnel_token_ssm_arn = "arn:aws:ssm:${var.aws_region}:693906847467:parameter/healthkicks/${var.environment}/CLOUDFLARE_TUNNEL_TOKEN"

  environment_variables = {
    HEALTHKICKS_ENVIRONMENT = var.environment
    DATABASE_URL            = "postgresql+psycopg2://postgres@${module.database.cluster_endpoint}:5432/postgres"
    USE_RDS_IAM             = "true"
    HEALTHKICKS_USE_RDS_IAM = "true"
    DATABASE_SSLMODE        = "require"
    AWS_REGION              = var.aws_region
    AWS_DEFAULT_REGION      = var.aws_region
  }

  environment_secrets = {
    for k in local.ssm_secret_keys : k => "arn:aws:ssm:${var.aws_region}:693906847467:parameter/healthkicks/${var.environment}/${k}"
  }
}

# 5. Database: Aurora Serverless v2 PostgreSQL 17 Cluster (Restored in eu-west-1)
module "database" {
  source                 = "../../modules/database"
  environment            = var.environment
  min_capacity           = 0.5
  max_capacity           = 1.0
  snapshot_identifier    = var.aurora_snapshot_identifier
  vpc_security_group_ids = [module.security.aurora_security_group_id]
}

# 6. Frontend CDN: S3 Bucket (eu-north-1), CloudFront Distribution, OAC, and ACM (us-east-1)
module "frontend_cdn" {
  source = "../../modules/frontend_cdn"
  providers = {
    aws           = aws.eu_north_1
    aws.us_east_1 = aws.us_east_1
  }

  environment          = var.environment
  domain_name          = "app.healthkicks.eu"
  enable_custom_domain = true
}
