//go:build integration

package integration

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestApplyRecordsService(t *testing.T) {
	options := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../..",
		Vars: map[string]interface{}{
			"name": "api",
			"host": "api.example.internal",
		},
	})

	defer terraform.Destroy(t, options)
	terraform.InitAndApply(t, options)

	assert.Equal(t, "svc-api", terraform.Output(t, options, "service_name"))
}
