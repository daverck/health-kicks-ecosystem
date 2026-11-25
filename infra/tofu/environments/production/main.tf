# ==============================================================================
# HealthKicks Production Environment Architecture (OpenTofu)
# ==============================================================================

# 1. Storage: ECR repositories, DynamoDB, S3 OTA bucket
module "storage" {
  source                  = "../../modules/storage"
  environment             = var.environment
  max_ecr_images_retained = 3
}

# 2. IAM: EC2 Instance Profile and GitHub Actions OIDC Role
module "iam" {
  source            = "../../modules/iam"
  environment       = var.environment
  github_repository = var.github_repository
}

# 3. Security: Host Security Group (HTTP, HTTPS, SSH)
module "security" {
  source      = "../../modules/security"
  vpc_id      = var.vpc_id
  environment = var.environment
}

# 4. Compute: Single EC2 Host (t3.micro) + Elastic IP (for Cloudflare DNS)
module "compute" {
  source                    = "../../modules/compute"
  environment               = var.environment
  instance_type             = var.instance_type
  subnet_id                 = var.subnet_id
  key_name                  = var.key_name
  security_group_id         = module.security.web_security_group_id
  iam_instance_profile_name = module.iam.ec2_instance_profile_name
}

# 5. Database: Aurora Serverless v2 PostgreSQL 17 Cluster
module "database" {
  source       = "../../modules/database"
  environment  = var.environment
  min_capacity = 0.5
  max_capacity = 1.0
}

# 6. Frontend CDN: S3 Bucket, CloudFront Distribution, OAC, and ACM
module "frontend_cdn" {
  source = "../../modules/frontend_cdn"
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  environment          = var.environment
  domain_name          = "app.healthkicks.eu"
  enable_custom_domain = true
}

# 7. App Runner: Managed Serverless Container for Backend
module "app_runner" {
  count  = var.enable_app_runner ? 1 : 0
  source = "../../modules/app_runner"

  environment          = var.environment
  service_name         = "healthkicks-backend"
  image_repository_url = module.storage.backend_repo_url
  image_tag            = var.app_runner_image_tag
  access_role_arn      = module.iam.apprunner_access_role_arn
  instance_role_arn    = module.iam.apprunner_instance_role_arn
  subnet_ids           = var.database_subnet_ids
  security_group_id    = module.security.apprunner_security_group_id

  cpu    = var.app_runner_cpu
  memory = var.app_runner_memory
  port   = "8000"

  max_concurrency = var.app_runner_max_concurrency
  min_size        = var.app_runner_min_size
  max_size        = var.app_runner_max_size

  custom_domain_name   = "api.healthkicks.eu"
  enable_custom_domain = var.app_runner_enable_custom_domain

  environment_variables = {
    ENVIRONMENT  = var.environment
    DATABASE_URL = "postgresql+asyncpg://postgres@${module.database.cluster_endpoint}:5432/postgres"
    AWS_REGION   = var.aws_region
  }
}
