import json
import base64
import boto3
import email

s3 = boto3.client("s3")

def lambda_handler(event, context):
    request_path = event["path"].split("/")
    bucket = request_path[2]
    bucket_key = request_path[3]
    # decoding form-data into bytes
    post_data = base64.b64decode(event["body"])
    
    # fetching content-type
    try:
        content_type = event["headers"]["Content-Type"]
    except:
        content_type = event["headers"]["content-type"]
    # concate Content-Type: with content_type from event
    ct = "Content-Type: " + content_type + "\n"

    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode() + post_data)
    payload = msg.get_payload()
    json_data = json.loads(payload)
    document = json_data['document']
    
    try:
        response = s3.delete_objects(
        Bucket=bucket,
        Delete={
            'Objects': [
                {
                    'Key': bucket_key + '/' + document
                },
            ],
            'Quiet': True
        }
    )
        return {
            'statusCode': 200,
            'body': json.dumps('Document ' + document + ' is Deleted')
        }
        
    except Exception as e:
        
        return {
            'statusCode': 500,
            'body': json.dumps('Error in deleting document: ' + e)
        }       