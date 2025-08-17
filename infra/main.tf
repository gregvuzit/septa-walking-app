# infra/main.tf
# Main entry point for Terraform configuration
provider "aws" {
  region = var.aws_region
}

# VPC Module
module "vpc" {
  source       = "./vpc"
  vpc_cidr     = var.vpc_cidr
  subnet_count = 2
  name_prefix  = var.project_name
}

# RDS module
module "rds" {
  source            = "./rds"
  name_prefix       = var.project_name
  subnet_ids        = module.vpc.subnet_ids
  security_group_id = module.vpc.security_group_id
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
  depends_on        = [module.vpc]
}

# ECR Module - Using existing repository
module "ecr" {
  source          = "./ecr"
  repository_name = var.ecr_repository_name
}

# ALB Module
module "alb" {
  source            = "./alb"
  name_prefix       = var.project_name
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.subnet_ids
  security_group_id = module.vpc.security_group_id
  depends_on = [module.vpc]
}

# ECS Module
module "ecs" {
  source                    = "./ecs"
  cluster_name              = "${var.project_name}-cluster"
  name_prefix               = var.project_name
  vpc_id                    = module.vpc.vpc_id
  subnet_ids                = module.vpc.subnet_ids
  security_group_id         = module.vpc.security_group_id
  ecr_repository_url        = module.ecr.repository_url
  api_target_group_arn      = module.alb.api_target_group_arn
  frontend_target_group_arn = module.alb.frontend_target_group_arn
  dns_name                  = module.alb.load_balancer_dns
  task_cpu                  = var.task_cpu
  task_memory               = var.task_memory
  service_desired_count     = var.service_desired_count
  db_instance_address       = module.rds.db_instance_address
  db_name                   = var.db_name
  db_username               = var.db_username
  db_password               = var.db_password
  google_maps_key           = var.google_maps_key

  depends_on = [module.alb, module.rds]
}
