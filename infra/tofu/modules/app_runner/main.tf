terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

# ------------------------------------------------------------------------------
# 1. Auto Scaling Configuration (Horizontal concurrency scaling)
# ------------------------------------------------------------------------------

resource "aws_apprunner_auto_scaling_configuration_version" "backend_scaling" {
  auto_scaling_configuration_name = "${var.service_name}-autoscaling"
  max_concurrency                 = var.max_concurrency
  min_size                        = var.min_size
  max_size                        = var.max_size

  tags = {
    Name        = "${var.service_name}-autoscaling"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 2. VPC Connector (For secure private communication with Aurora PostgreSQL)
# ------------------------------------------------------------------------------

resource "aws_apprunner_vpc_connector" "backend_vpc_connector" {
  vpc_connector_name = "${var.service_name}-vpc-connector"
  subnets            = var.subnet_ids
  security_groups    = [var.security_group_id]

  tags = {
    Name        = "${var.service_name}-vpc-connector"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 3. App Runner Service (FastAPI Container)
# ------------------------------------------------------------------------------

resource "aws_apprunner_service" "backend_service" {
  service_name                   = "${var.service_name}-${var.environment}"
  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.backend_scaling.arn

  source_configuration {
    auto_deployments_enabled = var.auto_deployments_enabled

    authentication_configuration {
      access_role_arn = var.access_role_arn
    }

    image_repository {
      image_identifier      = "${var.image_repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port                          = var.port
        runtime_environment_variables = var.environment_variables
        runtime_environment_secrets   = var.environment_secrets
      }
    }
  }

  instance_configuration {
    cpu               = var.cpu
    memory            = var.memory
    instance_role_arn = var.instance_role_arn
  }

  network_configuration {
    egress_configuration {
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.backend_vpc_connector.arn
    }
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/api/v1/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  tags = {
    Name        = "${var.service_name}-${var.environment}"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 4. Optional Custom Domain Association (e.g. api.healthkicks.eu)
# ------------------------------------------------------------------------------

resource "aws_apprunner_custom_domain_association" "api_custom_domain" {
  count       = var.enable_custom_domain && var.custom_domain_name != "" ? 1 : 0
  domain_name = var.custom_domain_name
  service_arn = aws_apprunner_service.backend_service.arn
}
