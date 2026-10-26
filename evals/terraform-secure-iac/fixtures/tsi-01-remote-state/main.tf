resource "aws_s3_bucket" "reports" {
  bucket = "reports-${var.environment}"
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "expire-old-reports"
    status = "Enabled"

    filter {}

    expiration {
      days = 90
    }
  }
}

resource "aws_iam_user" "uploader" {
  name = "reports-uploader-${var.environment}"
}

resource "aws_iam_access_key" "uploader" {
  user = aws_iam_user.uploader.name
}
