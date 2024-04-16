resource "aws_s3_bucket" "static_site" {
  bucket = var.bucket_name

  #provisioner "local-exec" {
  #  command = "aws s3 sync C:/Users/ecche/tf-app/modules/s3-website s3://${aws_s3_bucket.static_site.bucket} --acl public-read --delete"

  #}

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_object" "provision_source_files" {
    bucket  = aws_s3_bucket.static_site.id

    # The for_each meta-argument accepts a map or a set of strings, and creates an instance for each item in that map or set.
    for_each = fileset("${path.root}/CloudResume", "**/*.*")

    # set name of copied object in the bucket
    key    = each.value 
    source = "${path.root}/CloudResume/${each.value}"
    content_type = each.value == "index.html" ? "text/html" : each.value == "Script.js" ? "application/javascript" : each.value == "style.css" ? "text/css" : null

    # Triggers updates when the value changes
    etag = filemd5("${path.root}/CloudResume/${each.value}")
}

resource "aws_s3_bucket_ownership_controls" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "static_site" {
  depends_on = [
    aws_s3_bucket_ownership_controls.static_site,
    aws_s3_bucket_public_access_block.static_site,
  ]

  bucket = aws_s3_bucket.static_site.id
  acl    = "private"
}

#resource "aws_s3_bucket_policy" "static_site" {
#  bucket = aws_s3_bucket.static_site.id
#
#  policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Effect    = "Allow",
#        Principal = {"AWS": "arn:aws:iam::539081213062:user/iamadmin"},
#        Action    = "s3:*",
#        Resource  = ["${aws_s3_bucket.static_site.arn}/*"]
#      }
#    ]
#  })
#
#  depends_on = [aws_s3_bucket_public_access_block.static_site]
#}

resource "aws_s3_bucket_policy" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  policy = jsonencode({
    Version = "2008-10-17",
    Id = "PolicyForCloudFrontPrivateContent",
    Statement = [
      {
        Sid = "AllowCloudFrontServicePrincipal",
        Effect    = "Allow",
        Principal = {
          Service = "cloudfront.amazonaws.com"
        },
        Action    = ["s3:GetObject"],
        Resource  = ["${aws_s3_bucket.static_site.arn}/*"],
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "${var.cloudfront_distribution_arn}"
          }
        }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.static_site]
}

resource "aws_s3_bucket_website_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  versioning_configuration {
    status = "Enabled"
  }
}

# resource "aws_s3_object" "bucketobject" {
#   bucket = "cloudresumebucket"
#   key    = "new_object_key"
#   source = "path/to/file"

#   # The filemd5() function is available in Terraform 0.11.12 and later
#   # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
#   # etag = "${md5(file("path/to/file"))}"
#   etag = filemd5("path/to/file")
# }

# Irrelevant
# resource "aws_s3_bucket_acl" "s3_bucketacl" {
#   bucket = aws_s3_bucket.static_site.id

#   acl = "public-read"
# }

# resource "aws_s3_bucket_policy" "s3_bucketpolicy" {
#   bucket = aws_s3_bucket.static_site.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid       = "PublicReadGetObject"
#         Effect    = "Allow"
#         Principal = "*"
#         Action    = "s3:GetObject"
#         Resource = [
#           aws_s3_bucket.s3_bucket.arn,
#           "${aws_s3_bucket.s3_bucket.arn}/*",
#         ]
#       },
#     ]
#   })
# }