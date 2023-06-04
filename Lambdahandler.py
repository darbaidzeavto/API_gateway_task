import json
import io
import binascii
from urllib.request import urlopen, Request
import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
from decimal import Decimal
import base64
from botocore.vendored import requests


def query_image(f, API_URL, headers):
  http_request = Request(API_URL, data=f.read(), headers=headers)
  with urlopen(http_request) as response:
    result = response.read().decode()
    print(result)
  return result


def save_to_dynamodb(data):
  dynamodb = boto3.client('dynamodb')
  timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
  serializer = TypeSerializer()
  dynamo_serialized_data = []
  for item in json.loads(data, parse_float=Decimal):
    dynamo_serialized_item = {'M': {}}
    for key, value in item.items():
      if isinstance(value, (float, Decimal)):
        dynamo_serialized_item['M'][key] = {'N': str(value)}
      elif isinstance(value, dict):
        dynamo_serialized_item['M'][key] = {
          'M': {k: serializer.serialize(v)
                for k, v in value.items()}
        }
      else:
        dynamo_serialized_item['M'][key] = {'S': str(value)}
    dynamo_serialized_data.append(dynamo_serialized_item)

  data_ready_to_be_saved = {
    'id': {
      'S': str(uuid.uuid1())
    },
    'createdAt': {
      'S': timestamp
    },
    'updatedAt': {
      'S': timestamp
    },
    'huggingJson': {
      'L': dynamo_serialized_data
    },
    'huggingFaceStringData': {
      'S': data
    }
  }
  print(json.dumps(data_ready_to_be_saved))

  try:
    dynamodb.put_item(TableName='task1', Item=data_ready_to_be_saved)
    pass
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  return


def lambda_handler(event, context):
  print(event)
  body = json.loads(event['body'])
  image = body['image']
  API_URL = body['link']
  API_TOKEN = "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"
  headers = {"Authorization": f"Bearer {API_TOKEN}"}
  image_data = base64.b64decode(image)
  s3_bucket_name = 'task1api'
  s3_object_key = body['filename']
  s3_client = boto3.client('s3')
  s3_client.put_object(Bucket=s3_bucket_name,
                       Key=s3_object_key,
                       Body=image_data)
  file = io.BytesIO()
  s3_client.download_fileobj(Bucket=s3_bucket_name,
                             Key=s3_object_key,
                             Fileobj=file)
  file.seek(0)
  # Send file to Huggingface API
  result = query_image(file, API_URL, headers)
  print("result", result)
  save_to_dynamodb(result)
  response = {
    "statusCode": 200,
    "headers": {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    },
    "body": "Data received Successfully"
  }
  return response
