
variable "bucket_name" {
  description = "Name of the s3 bucket. Must be unique."
  type        = string
}

variable "tags" {
  description = "Tags to set on the bucket."

  # what's a map(string)?
  type        = map(string)
  default     = {}
}


variable "cloudfront_distribution_arn" {
  description = "cloudfront distribution arn"
}
