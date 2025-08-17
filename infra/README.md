# infra/README.md
# Terraform AWS Infrastructure for SEPTA Walking App

## Prerequisites
- Terraform >= 1.0
- AWS CLI configured
- Docker images for api and frontend pushed to ECR or Docker Hub
- ACM certificate for your domain (in us-east-1 for ALB)

## Setup
1. Copy `infra/terraform.tfvars.example` to `infra/terraform.tfvars` and fill in your values.
2. Run `terraform init` in the `infra/` directory.
3. Run `terraform apply` to provision resources.

## Required Variables
- `db_username`, `db_password`: RDS credentials
- `acm_certificate_arn`: ACM certificate ARN for HTTPS
- `api_image`, `frontend_image`: Docker image URIs for ECS

## Outputs
- `alb_dns_name`: Load balancer DNS name
- `rds_endpoint`: RDS endpoint

## Notes
- The ECS services expect your containers to listen on ports 8000 (api) and 3000 (frontend).
- You may need to update security groups or add environment variables as needed.
- For production, consider secrets management and autoscaling.
