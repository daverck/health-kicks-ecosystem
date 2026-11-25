output "cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "service_name" {
  description = "ECS Service name"
  value       = aws_ecs_service.backend.name
}

output "task_definition_arn" {
  description = "ARN of the active ECS Task Definition"
  value       = aws_ecs_task_definition.backend.arn
}

output "log_group_name" {
  description = "CloudWatch Log Group name for container stdout/stderr"
  value       = aws_cloudwatch_log_group.backend.name
}
