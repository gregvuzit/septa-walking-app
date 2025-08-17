# Load Balancer
resource "aws_lb" "app_lb" {
  name               = "${var.name_prefix}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.security_group_id]
  subnets            = var.subnet_ids
}

resource "aws_lb_target_group" "api_target_group" {
  name                      = "api-tg"
  port                      = 8000
  protocol                  = "HTTP"
  target_type               = "ip"
  vpc_id                    = var.vpc_id
}

resource "aws_lb_target_group" "frontend_target_group" {
  name                      = "frontend-tg"
  port                      = 3000
  protocol                  = "HTTP"
  target_type               = "ip"
  vpc_id                    = var.vpc_id
}

resource "aws_lb_listener" "frontend_listener" {
  load_balancer_arn         = aws_lb.app_lb.arn
  port                      = 80
  protocol                  = "HTTP"

  default_action {
    type                    = "forward"
    target_group_arn        = aws_lb_target_group.frontend_target_group.arn
  }
}

resource "aws_lb_listener" "api_listener" {
  load_balancer_arn         = aws_lb.app_lb.arn
  port                      = 8000
  protocol                  = "HTTP"

  default_action {
    type                    = "forward"
    target_group_arn        = aws_lb_target_group.api_target_group.arn
  }
}