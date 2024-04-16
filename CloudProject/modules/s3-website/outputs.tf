output "arn" {
  description = "ARN of the bucket"
  value       = aws_s3_bucket.static_site.arn
}

output "name" {
  description = "Name (id) of the bucket"
  value       = aws_s3_bucket.static_site.bucket_domain_name
}

output "domain" {
  description = "Domain name of the bucket"
  value       = aws_s3_bucket_website_configuration.static_site.website_domain
}

output "static_website_url" {
  value = aws_s3_bucket_website_configuration.static_site.website_endpoint
}