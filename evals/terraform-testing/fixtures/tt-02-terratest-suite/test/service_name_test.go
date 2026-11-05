package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestServiceName(t *testing.T) {
	t.Parallel()

	options := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "..",
		Vars: map[string]interface{}{
			"name": "api",
			"host": "api.example.internal",
		},
	})

	defer terraform.Destroy(t, options)
	terraform.InitAndApply(t, options)

	assert.Equal(t, "svc-api", terraform.Output(t, options, "service_name"))
}
