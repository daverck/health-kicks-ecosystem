# ==============================================================================
# CloudWatch Log Retention for Existing eu-west-1 Lambda Functions
# ==============================================================================

locals {
  lambda_function_names = toset([
    "healthkicks_presence_handler",
    "healthkicks-alert-to-discord",
    "healthkicks-fall-alert-relay",
    "healthkicks-iot-detection-ingest",
    "healthkicks-presence-sync",
    "healthkicks-telemetry-flattener",
  ])
}

resource "aws_cloudwatch_log_group" "lambda_functions" {
  for_each = local.lambda_function_names

  name              = "/aws/lambda/${each.value}"
  retention_in_days = 14

  tags = {
    Project     = "HealthKicks"
    Component   = "Lambda"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}
