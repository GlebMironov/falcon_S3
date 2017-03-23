import hashlib
import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from celery import Celery

from config import AWS_BUCKET_NAME, AWS_TABLE_NAME, UPLOAD_PATH, DOWNLOAD_PATH


app = Celery('tasks', backend='rpc://', broker='pyamqp://')


def read_chunks(f, chunk_size=8192):
    """Read file
    
        Note: 
            Reads potentially big file by chunks
    
    """

    while True:
        data = f.read(chunk_size)
        if not data:
            break
        yield data

def md5(f):
    """Obtain the md5 digest
    
        Note: 
            Obtains md5 hash function of file-like object
    
    """

    h = hashlib.md5()
    for chunk in read_chunks(f):
        h.update(chunk)
    return h.hexdigest()

@app.task
def put_data_to_s3(file_path):
    """Upload file into AWS S3 storage
    
        Note: 
            Receives file path, obtains md5 hash function of the file,
            saves file_key (hash) and file_name values in AWS DynamoDB,
            uploads file to AWS S3 storage.
    
    """

    hash_string = None
    try:
        db = boto3.resource('dynamodb')
        table = db.Table(AWS_TABLE_NAME)
    
        with open(file_path, 'rb') as f:
            hash_string = md5(f)
    
        path, file_name = os.path.split(file_path)
        table.put_item(
            Item = {
                'file_key': hash_string,
                'file_name': file_name
            })
    
        s3 = boto3.client('s3')
        with open(file_path, 'rb') as f:
            s3.upload_fileobj(f, AWS_BUCKET_NAME, hash_string)
    except ClientError as e:
        hash_string = None

    return hash_string

@app.task
def get_data_from_s3(file_key):
    """Download file from AWS S3 storage
    
        Note: 
            Receives file key, obtains file name from AWS DynamoDB,
            downloads file from AWS S3 storage.
    
    """

    file_name = None
    try:
        db = boto3.resource("dynamodb")
        table = db.Table(AWS_TABLE_NAME)
        
        result = table.query(
            KeyConditionExpression=Key('file_key').eq(file_key)
        )
        
        if result['Count']:
            file_name = result["Items"][0]["file_name"]
            file_path = os.path.join(DOWNLOAD_PATH, file_name)
        
            s3 = boto3.client('s3')
            with open(file_path, 'wb') as f:
                s3.download_fileobj(AWS_BUCKET_NAME, file_key, f)    

    except ClientError as e:
        file_name = None

    return file_name
