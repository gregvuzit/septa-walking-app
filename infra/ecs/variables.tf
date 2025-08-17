variable "cluster_name" {
  description = "Name of the ECS cluster"
}

variable "name_prefix" {
  description = "Prefix to use for resource names"
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "security_group_id" {
  description = "ID of the security group"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "task_cpu" {
  description = "CPU units for the task"
}

variable "task_memory" {
  description = "Memory for the task in MB"
}

variable "service_desired_count" {
  description = "Desired count of tasks in the service"
}

variable "dns_name" {
  description = "Load balancer DNS name"
  type        = string
}

variable "api_target_group_arn" {
  description = "ARN of the api target group for the load balancer"
  type        = string
}

variable "frontend_target_group_arn" {
  description = "ARN of the frontend target group for the load balancer"
  type        = string
}

variable "db_instance_address" {
  description = "Endpoint of the RDS Postgres instance"
  type        = string
}

variable "db_name" {
  description = "Database name for RDS."
  type        = string
}

variable "db_username" {
  description = "Database master username."
  type        = string
}

variable "db_password" {
  description = "Database master password."
  type        = string
  sensitive   = true
}

variable "google_maps_key" {
  description = "Access key for Google Maps API"
  type        = string
}