package test

import (
	// "fmt"
	"testing"
	"time"
	http_helper "github.com/gruntwork-io/terratest/modules/http-helper"
	// "github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	test_structure "github.com/gruntwork-io/terratest/modules/test-structure"
)

// Since we want to be able to run multiple tests in parallel on the same modules, we need to copy them into
// temp folders so that the state files and .terraform folders don't clash
func ConfigApp(t *testing.T) *terraform.Options {
	return &terraform.Options{
		TerraformDir: "../",
	}
}

func TestApiTest(t *testing.T) {

	t.Parallel()

	// A unique ID we can use to namespace all our resource names and ensure they don't clash across parallel tests
	// uniqueId := random.UniqueId()

	// initialize the terraformOptions variable and point to a terraform.Options struc
	terraformOptions := &terraform.Options{
			// The path to where our Terraform code is located
			TerraformDir: "../../",
	}

	// Copy terraform folder to temp folder for parallel testing
	// func CopyTerraformFolderToTemp(t testing.TestingT, rootFolder string, terraformModuleFolder string) string
	appPath := test_structure.CopyTerraformFolderToTemp(t, "../", "/tmp",)
	
	// At the end of the test, run `terraform destroy` to clean up any resources that were created
	// defer terraform.Destroy(t, terraformOptions)

	defer test_structure.RunTestStage(t, "cleanup_app", func() {
		appOpts := test_structure.LoadTerraformOptions(t, appPath)
		terraform.Destroy(t, appOpts)
	})

	// This will run `terraform init` and `terraform apply` and fail the test if there are any errors
	// terraform.InitAndApply(t, terraformOptions)
	// Deploy the web-service module
	test_structure.RunTestStage(t, "deploy_app", func() {
		appOpts := terraformOptions
		test_structure.SaveTerraformOptions(t, appPath, appOpts)
		terraform.InitAndApply(t, appOpts)
	})
	// Arguments: func SaveTerraformOptions(t testing.TestingT, testFolder string, terraformOptions *terraform.Options)
	


	// Check that the app is working as expected
	validateApi(t, terraformOptions) 
}

// terraformOptions: A pointer to a terraform.Options struct, which holds options for configuring the execution of Terraform commands.
func validateApi(t *testing.T, terraformOptions *terraform.Options) {
	// Verify the app returns a 200 OK 
	url := terraform.Output(t, terraformOptions, "url")
	url += "/books"
	expectedStatus := 200
	expectedBody := `{"visit_count": 1}`
	maxRetries := 10
	timeBetweenRetries := 3 * time.Second
	http_helper.HttpGetWithRetry(t, url, nil, expectedStatus, expectedBody, maxRetries, timeBetweenRetries)
}
