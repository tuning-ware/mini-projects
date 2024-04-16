# DynamoDB table
resource "aws_dynamodb_table" "visitor-count-table" {
  name           = "visitor-count-table"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "visits"

  attribute {
    name = "visits"
    type = "S"
  }

  # attempted workaround TTL disabled error bug
  dynamic "ttl" {
  for_each = var.ttl_attribute_name != null ? [1] : []
  iterator = index
  content {
    enabled        = true
    attribute_name = var.ttl_attribute_name
   }
  }

  # ttl {
  #   attribute_name = "TimeToExist"
  #   enabled        = true
  # }

  tags = {
    Name        = "dynamodb-table-1"
    Environment = "production"
  }
}

# permissions policy for DynamoDB
#resource "aws_iam_role_policy" "lambda_policy" {
#  name = "lambda_policy"
#  role = "${aws_iam_role.role_for_lambda.id}"
#  policy = file("iam/policy.json")
#}

# create an IAM role for Lambda to assume
resource "aws_iam_role" "role_for_lambda" {
  name = "lambdaRole"
  assume_role_policy = file("iam/assume_role_policy.json")
}

resource "aws_iam_policy" "policy" {
  name        = "dynamoDB_policy"
  path        = "/"
  description = "My test policy"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "dynamodb:BatchGetItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ],
        "Resource": "arn:aws:dynamodb:us-east-1:*:*"
      },

      {
        "Effect": "Allow"

        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]

        "Resource": "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.role_for_lambda.name
  policy_arn = aws_iam_policy.policy.arn
}

# api for lambda
resource "aws_api_gateway_rest_api" "apiLambda" {
  name        = "viewcounterapi"
  description = "view counter API using TF"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# api gateway resource 
# path_part - (Required) Last path segment of this API resource.
resource "aws_api_gateway_resource" "Resource" {
  rest_api_id = "${aws_api_gateway_rest_api.apiLambda.id}"
  parent_id   = "${aws_api_gateway_rest_api.apiLambda.root_resource_id}"
  path_part   = "books"
}

# defining methods
resource "aws_api_gateway_method" "Method" {
  rest_api_id   = "${aws_api_gateway_rest_api.apiLambda.id}"
  resource_id   = "${aws_api_gateway_resource.Resource.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambdaIntegration" {
  rest_api_id = "${aws_api_gateway_rest_api.apiLambda.id}"
  resource_id = "${aws_api_gateway_resource.Resource.id}"
  http_method = "${aws_api_gateway_method.Method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda_viewcounter.invoke_arn}"
}


resource "aws_api_gateway_method_response" "lambdaAPIResponse" {
  rest_api_id = "${aws_api_gateway_rest_api.apiLambda.id}"
  resource_id = "${aws_api_gateway_resource.Resource.id}"
  http_method = "${aws_api_gateway_method.Method.http_method}"
  status_code = "200"
}


# Configure the API Gateway and Lambda functions response
resource "aws_api_gateway_integration_response" "lambdaAPIIntegrationResponse" {
  rest_api_id = "${aws_api_gateway_rest_api.apiLambda.id}"
  resource_id = "${aws_api_gateway_resource.Resource.id}"
  http_method = "${aws_api_gateway_method.Method.http_method}"
  status_code = "${aws_api_gateway_method_response.lambdaAPIResponse.status_code}"

  depends_on = [
    aws_api_gateway_integration.lambdaIntegration
  ]
}

resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambdaIntegration,
    aws_api_gateway_integration_response.lambdaAPIIntegrationResponse
  ]

  rest_api_id = "${aws_api_gateway_rest_api.apiLambda.id}"
  stage_name  = "Prod"

  # forces to 'create' a new deployment each run. Otherwise the deployment doesn't get created after the initial run
  stage_description = timestamp()
}

# give the api gateway permissions to invoke the lambda function
resource "aws_lambda_permission" "allow_api_gateway" {
  function_name = aws_lambda_function.lambda_viewcounter.arn
  statement_id  = "AllowExecutionFromApiGateway"
  action        = "lambda:InvokeFunction"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"

  depends_on = [
    aws_api_gateway_rest_api.apiLambda,
    aws_api_gateway_resource.Resource
  ]
}

# create a deployment package for lambda function
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "lambdaapi.py"
  output_path = "lambda_function_payload.zip"
}

# lambda function
resource "aws_lambda_function" "lambda_viewcounter" {
  filename      = "lambda_function_payload.zip"
  function_name = "lambda_viewcounter"
  role          = aws_iam_role.role_for_lambda.arn
  runtime       = "python3.9"
  handler       = "lambdaapi.lambda_handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.test-attach,
    aws_cloudwatch_log_group.log_group,
  ]

  environment {
    variables = {
      TABLE_NAME = "visitor-count-table"
    }
  }
}

resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/lambda/lambda_viewcounter"
  retention_in_days = 14
}


# cloudfront distribution
resource "aws_cloudfront_distribution" "static_website" {
  origin {
    domain_name = module.s3module.name
    origin_access_control_id = aws_cloudfront_origin_access_control.cloudfront_oac.id
    origin_id   = "Custom-Origin"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  depends_on = [aws_s3_bucket.cloudfront_logs_bucket, module.s3module.name]  

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cloudfront_logs_bucket.bucket_domain_name
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "Custom-Origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_All"
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

resource "aws_s3_bucket" "cloudfront_logs_bucket" {
  bucket_prefix = "cloudfront-logs-"  # Prefix for the bucket name (optional)
 
}

resource "aws_s3_bucket_ownership_controls" "cloudfront_logs_bucket" {
  bucket = aws_s3_bucket.cloudfront_logs_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "cloudfront_logs_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.cloudfront_logs_bucket]

  bucket = aws_s3_bucket.cloudfront_logs_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_policy" "cloudfront_logs_bucket_policy" {
  bucket = aws_s3_bucket.cloudfront_logs_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "AllowCloudFrontToWriteLogs",
        Effect = "Allow",
        Principal = {
          Service = "cloudfront.amazonaws.com"
        },
        Action = "s3:PutObject",
        Resource = "${aws_s3_bucket.cloudfront_logs_bucket.arn}/*",
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}


resource "aws_cloudfront_origin_access_control" "cloudfront_oac" {
  name                              = "cloudfront_oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# s3 website module
module "s3module" {
  source = "./modules/s3-website"
  bucket_name = var.bucket_name
  cloudfront_distribution_arn = aws_cloudfront_distribution.static_website.arn
}

output "base_url" {
  value = "${aws_api_gateway_deployment.apideploy.invoke_url}"
}

# accessing module output values using the expression module.s3module.(output value declared in child module)
output "website_domain" {
  value = module.s3module.name
}

output "website_endpoint" {
  value = module.s3module.static_website_url
}

output "cloudfront_distribution_arn" {
  value = aws_cloudfront_distribution.static_website.arn
}