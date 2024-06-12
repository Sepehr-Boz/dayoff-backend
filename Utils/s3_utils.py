import os
import boto3
from botocore.exceptions import NoCredentialsError

# # S3_BUCKET=os.environ.get('S3_BUCKET')
# # S3_REGION=os.environ.get('S3_REGION')

# # def upload_to_s3(bucket_name, file_name, file_data):
# #     try:
# #         # Initialize S3 client
# #         s3 = boto3.client('s3',
# #                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
# #                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
# #                           region_name=os.getenv('AWS_REGION'))
# #         s3.upload_fileobj(file_data, bucket_name, file_name,ExtraArgs={'ContentType': 'image/jpeg'})
# #         return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
# #     except NoCredentialsError:
# #         raise Exception("S3 credentials not available")
# #     except Exception as e:
# #         raise Exception(f"Exception in upload_to_s3: {str(e)}")


def upload_to_s3(bucket_name, file_name, file_data):
    try:
        # Initialize S3 client
        # s3 = boto3.client('s3',
        #                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        #                   aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        #                   region_name=os.getenv('AWS_REGION'))
        s3 = boto3.client('s3')
        # Upload file to S3 bucket
        s3.upload_fileobj(file_data, bucket_name, file_name, ExtraArgs={'ContentType': 'image/jpeg'})
        
        # Return the URL of the uploaded file
        region_name = s3.meta.region_name  # Dynamically get the region of the S3 client
        return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{file_name}"
 
    except NoCredentialsError:
        raise Exception("S3 credentials not available")
    
    except Exception as e:
        raise Exception(f"Exception in upload_to_s3: {str(e)}")




