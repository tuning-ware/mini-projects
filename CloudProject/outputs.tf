output "url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}

output "function_arn" {
  value = aws_lambda_function.lambda_viewcounter.arn
}

output "iam_role_arn" {
  value = aws_iam_role.role_for_lambda.arn
}

output "DynamoDB_arn" {
  value = aws_dynamodb_table.visitor-count-table.arn
}

output "Cloudfront_distribution" {
  value = aws_cloudfront_distribution.static_website.domain_name
}