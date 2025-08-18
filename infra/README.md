# infra/README.md
# Terraform AWS Infrastructure for SEPTA Walking App

## Overview
These Terraform scripts will deploy the SEPTA Walking App into a fully working installation within AWS. It creates a VPC in which the app runs, a RDS Postgres instance for the database, an Application Load Balancer in EC2 to handle and route requests to the app and between its component containers, and ECS containers for both the api and frontend that have Cloudwatch logging enabled. The root setup is located in `infra/main.tf`. The modules for each of the above AWS services are located in their corresponding child directory in `infra`.

When the deployment successfully completes, the ALB will allow HTTP requests (port 80) to the homepage of the frontend React app. You can copy the `load_balancer_dns` output value into a browser and should be taken to the homepage where you can use the form to make API requests and see the results.

Again, as stated in the main README, this is meant for demonstration purposes so the setup is very basic. See the final section for some thoughts on what a more robust production setup would entail.

## Prerequisites
- Terraform >= 1.0 - <https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli>
- AWS CLI configured - <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>
- AWS CLI Session Manager (optional if you want to use [ECS Exec](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html), the containers are already configured with the necessary setup) - <https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html>
- Docker images for api and frontend pushed to ECR. Make sure the images are built for the `linux/amd64` platform. Ex: `docker build --platform linux/amd64 -t api .` Build images for both api and frontend this way, and create a repo on ECR if you do not already have one. Then follow steps 4 and 5 for api and frontend [here](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).

## Setup
1. Create a copy of `infra/terraform.tfvars.example`, save to `infra/terraform.tfvars` and fill in your values.
2. Run `terraform init` in the `infra/` directory.
3. Run `terraform apply` to provision resources.

## Required Variables
- `db_name`: Name of your Postgres database
- `db_username`, `db_password`: RDS credentials
- `ecr_repository_name` - Name of the ECR repo you create
- `api_image`, `frontend_image`: Docker image URIs for ECS
- `google_maps_key`: Your Google Maps API key

## Outputs
- `load_balancer_dns`: Load balancer DNS name; you should be able to go to this url in a browser and see the frontend app homepage where you can make API requests
- `rds_endpoint`: RDS endpoint

## Teardown
Simply run `terraform destroy` from the `infra/` directory.

## Notes for a True Production Release
- VPC and security group setup would be much more rigid
- The frontend container Dockerfile would create and serve a production build.
- The application would only likely be accessible on port 443 of the ALB through HTTPS. A certificate would have to be associated with the setup.
- The Postgres RDS setup would only allow SSL connections.
- Could use something like Elasticache to cache the station data instead of in memory of the api container.
