# Check if ECR repository exists
data "aws_ecr_repository" "repo" {
  name = var.repository_name
}