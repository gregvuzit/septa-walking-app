output "repository_url" {
  description = "The URL of the ECR repository"
  value       = data.aws_ecr_repository.repo.repository_url
}

output "repository_name" {
  description = "The name of the ECR repository"
  value       = data.aws_ecr_repository.repo.name
}