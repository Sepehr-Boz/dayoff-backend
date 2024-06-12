provider "aws" {
  region     = "us-east-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

variable "aws_access_key" {}
variable "aws_secret_key" {}

resource "aws_s3_bucket" "lambda_code" {
  bucket = "dayoff-bucket"  # Update this to your existing bucket name
}

resource "aws_lambda_function" "dayoff_lambda" {
  function_name = "dayoff"
  s3_bucket     = aws_s3_bucket.lambda_code.bucket
  s3_key        = "lambda/zipped_functions/dayoff-lambda.zip"
  handler       = "main.handler"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}