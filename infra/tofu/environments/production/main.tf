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
  enable_custom_domain = false
}
