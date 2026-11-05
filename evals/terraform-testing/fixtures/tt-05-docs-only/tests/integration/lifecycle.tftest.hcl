variables {
  name = "billing"
}

run "policy_is_recorded" {
  command = apply

  assert {
    condition     = terraform_data.policy.output.retention_days == 30
    error_message = "The default retention must reach the recorded policy."
  }
}
