# orders

Terraform for the orders service's data tier. The security group and subnet group are in place;
the database itself is not yet.

The deploy job reads this configuration's outputs with `terraform output -json`.
