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

locals {
  log_group_name = "/ecs/${var.service_name}-${var.environment}"

  backend_container = {
    name      = "healthkicks-backend"
    image     = "${var.image_repository_url}:${var.image_tag}"
    essential = true

    portMappings = [
      {
        containerPort = 8000
        hostPort      = 8000
        protocol      = "tcp"
      }
    ]

    environment = [
      for k, v in var.environment_variables : {
        name  = k
        value = v
      }
    ]

    secrets = [
      for k, arn in var.environment_secrets : {
        name      = k
        valueFrom = arn
      }
    ]

    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 15
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "backend"
      }
    }
  }

  cloudflared_sidecar = var.enable_cloudflare_tunnel ? [
    {
      name      = "cloudflared"
      image     = "cloudflare/cloudflared:latest"
      essential = true
      command   = ["tunnel", "--no-autoupdate", "run"]

      secrets = [
        {
          name      = "TUNNEL_TOKEN"
          valueFrom = var.cloudflare_tunnel_token_ssm_arn
        }
      ]

      dependsOn = [
        {
          containerName = "healthkicks-backend"
          condition     = "START"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "cloudflared"
        }
      }
    }
  ] : []

  container_definitions = concat([local.backend_container], local.cloudflared_sidecar)
}

# ------------------------------------------------------------------------------
# 1. CloudWatch Log Group
# ------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "backend" {
  name              = local.log_group_name
  retention_in_days = 14

  tags = {
    Name        = local.log_group_name
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

resource "aws_cloudwatch_log_metric_filter" "backend_error_logs" {
  count          = var.enable_error_log_alarm ? 1 : 0
  name           = "${var.service_name}-${var.environment}-error-logs"
  pattern        = "{ $.level = \"ERROR\" || $.level = \"CRITICAL\" }"
  log_group_name = aws_cloudwatch_log_group.backend.name

  metric_transformation {
    name          = "BackendErrorLogCount"
    namespace     = "HealthKicks/${var.environment}"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_error_logs" {
  count               = var.enable_error_log_alarm ? 1 : 0
  alarm_name          = "${var.service_name}-${var.environment}-error-logs"
  alarm_description   = "Triggers when HealthKicks backend emits ERROR or CRITICAL structured logs."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.backend_error_logs[0].metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.backend_error_logs[0].metric_transformation[0].namespace
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = ["arn:aws:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.critical_alerts_sns_topic_name}"]

  tags = {
    Name        = "${var.service_name}-${var.environment}-error-logs"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 2. ECS Cluster & Fargate Spot Capacity Provider
# ------------------------------------------------------------------------------

resource "aws_ecs_cluster" "main" {
  name = "healthkicks-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    Name        = "healthkicks-cluster-${var.environment}"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = ["FARGATE_SPOT", "FARGATE"]

  default_capacity_provider_strategy {
    base              = 0
    weight            = 1
    capacity_provider = var.use_spot ? "FARGATE_SPOT" : "FARGATE"
  }
}

# ------------------------------------------------------------------------------
# 3. ECS Task Definition
# ------------------------------------------------------------------------------

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.service_name}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  container_definitions    = jsonencode(local.container_definitions)

  tags = {
    Name        = "${var.service_name}-${var.environment}"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# ------------------------------------------------------------------------------
# 4. ECS Service
# ------------------------------------------------------------------------------

resource "aws_ecs_service" "backend" {
  name                   = "${var.service_name}-${var.environment}"
  cluster                = aws_ecs_cluster.main.id
  task_definition        = aws_ecs_task_definition.backend.arn
  desired_count          = var.desired_count
  enable_execute_command = true

  capacity_provider_strategy {
    capacity_provider = var.use_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.security_group_id]
    assign_public_ip = true
  }

  depends_on = [aws_ecs_cluster_capacity_providers.main]

  tags = {
    Name        = "${var.service_name}-${var.environment}"
    Project     = "HealthKicks"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}
