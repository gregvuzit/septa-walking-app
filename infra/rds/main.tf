resource "aws_db_subnet_group" "septa" {
  name       = "septa"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.name_prefix}-db-subnet-group"
  }
}

resource "aws_db_parameter_group" "no_ssl_param_group" {
  name   = "${var.name_prefix}-param-group"
  family = "postgres17"

  parameter {
    name  = "rds.force_ssl"
    value = "0"
  }
}

resource "aws_db_instance" "postgres_instance" {
  identifier = "${var.name_prefix}-db"
  engine = "postgres"
  engine_version = "17.5"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible = true
  skip_final_snapshot = true
  db_subnet_group_name = aws_db_subnet_group.septa.name
  parameter_group_name = aws_db_parameter_group.no_ssl_param_group.name
}