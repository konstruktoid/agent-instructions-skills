package unit

import (
	"path/filepath"
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestServiceName(t *testing.T) {
	t.Parallel()

	options := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../..",
		PlanFilePath: filepath.Join(t.TempDir(), "plan.tfplan"),
		Vars: map[string]interface{}{
			"name": "api",
			"host": "api.example.internal",
		},
	})

	plan := terraform.InitAndPlanAndShowWithStruct(t, options)
	output := plan.RawPlan.PlannedValues.Outputs["service_name"]

	assert.Equal(t, "svc-api", output.Value)
}
