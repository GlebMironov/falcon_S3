import boto3
from botocore.exceptions import ClientError

from config import AWS_BUCKET_NAME, AWS_TABLE_NAME


def init():
    """Initialize AWS services for the backend.
    
        Note:
            S3 is used to store files.
            DynamoDB is used to bind a key-value between a hash and a file name.
    """

    try:
        s3 = boto3.client('s3')
        store = s3.create_bucket(Bucket=AWS_BUCKET_NAME)
    
        db = boto3.resource('dynamodb')
        table = db.create_table(
            AttributeDefinitions=[
                {'AttributeName': 'file_key', 'AttributeType': 'S'},
                {'AttributeName': 'file_name', 'AttributeType': 'S'},
            ],
            TableName=AWS_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'file_key', 'KeyType': 'HASH'},
                {'AttributeName': 'file_name','KeyType': 'RANGE'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
        })
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Table '{}' already exists.".format(AWS_TABLE_NAME))
        else:
            print("Unexpected error: {}".format(e))


if __name__ == '__main__':
    init()