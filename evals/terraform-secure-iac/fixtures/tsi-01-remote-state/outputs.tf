output "uploader_access_key_id" {
  value = aws_iam_access_key.uploader.id
}

output "uploader_secret_access_key" {
  value     = aws_iam_access_key.uploader.secret
  sensitive = true
}
