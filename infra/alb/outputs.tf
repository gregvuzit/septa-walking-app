output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app_lb.dns_name
}

output "api_target_group_arn" {
  description = "ARN of the api target group"
  value       = aws_lb_target_group.api_target_group.arn
}

output "frontend_target_group_arn" {
  description = "ARN of the frontend target group"
  value       = aws_lb_target_group.frontend_target_group.arn
}