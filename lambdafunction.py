import json
import boto3
import decimal
from decimal import Decimal

rekognition_client = boto3.client('rekognition')
dynamodb_resource = boto3.resource('dynamodb')
sns = boto3.client('sns')
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')
s3= boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table_name = 'my_table_s1935095'
table = dynamodb.Table(table_name)
topic_arn = 'arn:aws:sns:us-east-1:232224276285:my_topic_s1935095'


# Define custom JSON encoder class
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    for record in event['Records']:
        # extract message body and image name from the SQS message
        message = json.loads(record['body'])
        bucket_name = message['Records'][0]['s3']['bucket']['name']
        image_name = message['Records'][0]['s3']['object']['key']
        
        # get the image bytes from S3
        response = s3.get_object(Bucket=bucket_name, Key=image_name)
        image_bytes = response['Body'].read()
        
        # call Rekognition to detect labels in the image
        rekognition = boto3.client('rekognition')
        response = rekognition.detect_labels(
            Image={ 
                'Bytes': image_bytes
            },
            MaxLabels=5
        )
        
      # extract relevant details from Rekognition response
        labels = []
        for label in response['Labels']:
            name = label['Name']
            confidence = decimal.Decimal(str(label['Confidence']))
            labels.append({'Name': name, 'Confidence':(confidence)}) 
        
        # save label details to DynamoDB
        table.put_item(
            Item={
                'ImageName': image_name,
                'Labels': labels
            }
        )

        # Check if the 'pedestrian' label was detected and publish a message to the SNS topic
    for label in response['Labels']:
        if label['Name'].lower() == 'pedestrian':
            message = {
                's3_bucket': bucket_name,
                's3_key': image_name,
                'labels': labels
            }
            response = sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps({'default': json.dumps(message, cls=DecimalEncoder)}),
                MessageStructure='json'
            )
            print("SNS message sent: ", response)
            break
    
    return {
        'statusCode': 200,
        'body': json.dumps('Labels saved to DynamoDB table')
    }
