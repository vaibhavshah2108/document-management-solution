import json
import base64
import boto3
from botocore.client import Config

s3_client = boto3.client("s3", config = Config(signature_version='s3v4'))

def lambda_handler(event, context):
    body = json.loads(base64.b64decode(event["body"]))
    bucket = body["bucket_name"]
    fileKey = body["file_path"]
    action = body["action"]
    expiryTime = body["expiry_time"]
    
    try:
        url = s3_client.generate_presigned_url(
            "put_object" if action.lower()=="upload" else "get_object",
            Params = {"Bucket": bucket, "Key": fileKey},
            ExpiresIn = expiryTime
            )
            
        return {
            "statusCode": "200",
            "body": json.dumps({"URL": url}),
            "headers": {
                "Content-Type": "application/json",
            }
        }
    
    except Exception as e:
        return {
            "statusCode": "400",
            "body": json.dumps({"error": e}),
            "headers": {
                "Content-Type": "application/json",
            }            
        }