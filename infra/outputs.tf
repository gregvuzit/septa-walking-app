# infra/outputs.tf
output "rds_endpoint" {
  value = module.rds.db_instance_address
}

output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = module.alb.load_balancer_dns
}
