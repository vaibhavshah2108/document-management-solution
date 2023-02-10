import boto3
import requests
import json
import os
from requests_aws4auth import AWS4Auth
from botocore.session import Session

s3 = boto3.client('s3')
credentials = Session().get_credentials()
region = os.environ['AWS_REGION']
service = 'aoss'
opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def extract_metadata_and_content(bucket, s3_key):
    # Download the object from S3
    obj = s3.get_object(Bucket=bucket, Key=s3_key)
    
    # Extract metadata and content from the object using your preferred method
    # For example, you could use Tika to extract metadata and content from a PDF document
    metadata = obj["Metadata"]
    content = obj['Body'].read().decode('utf-8', errors="ignore")
    version_id = obj['VersionId']
    
    return metadata, content, version_id

def lambda_handler(event, context):
    # Get the S3 bucket name and key of the new object
    bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    object_url = 'https://' + bucket + '/' + '.s3.amazonaws.com/' + s3_key
    size = event['Records'][0]['s3']['object']['size']
    
    # Extract metadata and content from the object
    metadata, content, version_id = extract_metadata_and_content(bucket, s3_key)
    
    # Add the metadata and content to the OpenSearch index
    try:
        response = requests.post(
            opensearch_endpoint + '/documents/_doc',
            auth = awsauth,
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'actions': [{
                    'create': {
                        '_id': s3_key,
                        'fields': {
                            '_metadata': metadata,
                            '_objectUrl': object_url,
                            '_size': size,
                            '_versionId': version_id,
                            'content': content,
                        },
                    }
                }]
            }
        )

        return response.json()
        
    except requests.exceptions.HTTPError as err:
        return err.json()