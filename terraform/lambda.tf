provider "aws" {
  region     = "us-east-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

variable "aws_access_key" {}
variable "aws_secret_key" {}

resource "aws_lambda_function" "dayoff_lambda" {
  function_name = "dayoff"
  s3_bucket     = "dayoff-bucket"
  s3_key        = "lambda/zipped_functions/dayoff-lambda.zip"
  handler       = "main.handler"
  runtime       = "python3.9"
  role          = "arn:aws:iam::715139502280:role/lambda_exec_role"
}

