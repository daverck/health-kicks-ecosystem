terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # Local or S3 remote backend
  # To enable remote S3 state with state locking, uncomment the backend block below:
  # backend "s3" {
  #   bucket         = "healthkicks-tofu-state-eu-north-1"
  #   key            = "production/terraform.tfstate"
  #   region         = "eu-north-1"
  #   dynamodb_table = "healthkicks-tofu-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "HealthKicks"
      Environment = var.environment
      ManagedBy   = "OpenTofu"
    }
  }
}
