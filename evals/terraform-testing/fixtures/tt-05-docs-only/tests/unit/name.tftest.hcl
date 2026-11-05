variables {
  name = "billing"
}

run "policy_name_follows_service" {
  command = plan

  assert {
    condition     = output.policy_name == "billing-retention"
    error_message = "policy_name must be the service name followed by -retention."
  }
}
