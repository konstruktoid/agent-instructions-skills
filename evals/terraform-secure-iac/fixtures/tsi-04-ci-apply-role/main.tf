resource "aws_s3_bucket" "landing" {
  bucket = "ingest-landing-staging"
}

resource "aws_sqs_queue" "events" {
  name = "ingest-events-staging"
}

resource "aws_dynamodb_table" "checkpoints" {
  name         = "ingest-checkpoints-staging"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "source"

  attribute {
    name = "source"
    type = "S"
  }
}
