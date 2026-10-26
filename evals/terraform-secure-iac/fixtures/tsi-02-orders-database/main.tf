resource "aws_security_group" "orders_db" {
  name   = "orders-db"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }
}

resource "aws_db_subnet_group" "orders" {
  name       = "orders"
  subnet_ids = var.private_subnet_ids
}
