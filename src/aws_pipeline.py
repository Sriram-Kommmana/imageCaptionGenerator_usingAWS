import os
import time
from io import BytesIO
import boto3
from boto3.dynamodb.conditions import Key

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
DDB_TABLE_NAME = os.getenv("DDB_TABLE_NAME")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

s3 = boto3.client("s3", region_name=REGION)
ddb = boto3.resource("dynamodb", region_name=REGION)

if not DDB_TABLE_NAME:
    table = None
    print("Warning: DDB_TABLE_NAME is not set. DynamoDB operations disabled.")
else:
    table = ddb.Table(DDB_TABLE_NAME)

def upload_to_s3(file_bytes, filename):
    """
    Upload image to 'images/' folder in S3.
    Returns the S3 key (used as ImageId in DynamoDB).
    """
    s3_key = f"images/{filename}"
    s3.upload_fileobj(BytesIO(file_bytes), S3_BUCKET, s3_key)
    return s3_key

def get_caption_from_dynamodb(image_id, timeout=30, interval=2):
    """
    Poll DynamoDB until a caption is available for the given ImageId.
    Returns the latest caption or None if timeout is reached.
    """
    if not table:
        return None

    elapsed = 0
    while elapsed < timeout:
        response = table.query(
            KeyConditionExpression=Key('ImageId').eq(image_id),
            ScanIndexForward=False, 
            Limit=1
        )
        items = response.get("Items", [])
        if items:
            return items[0].get("CaptionText") or items[0].get("Caption")
        time.sleep(interval)
        elapsed += interval

    return None
