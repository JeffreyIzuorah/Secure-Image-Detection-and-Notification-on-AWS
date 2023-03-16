import json
import boto3
import decimal

rekognition_client = boto3.client('rekognition')
dynamodb_resource = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')
s3= boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table_name = 'my-table'
table = dynamodb.Table(table_name)


# Set precision for Decimal objects
decimal.getcontext().prec = 2


def lambda_handler(event, context):
    for record in event['Records']:
        # extract message body and image name from the SQS message
        message = json.loads(record['body'])
        image_name = message['Records'][0]['s3']['object']['key']
        
        # call Rekognition to detect labels in the image
        rekognition = boto3.client('rekognition')
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': 'my-bucket-jeff',
                    'Name': image_name
                }
            },
            MaxLabels=5
        )
        
        # extract relevant details from Rekognition response
        labels = []
        for label in response['Labels']:
            name = label['Name']
            confidence = decimal.Decimal(str(label['Confidence']))
            labels.append({'Name': name, 'Confidence': confidence})
        
        # save label details to DynamoDB
        table.put_item(
            Item={
                'ImageName': image_name,
                'Labels': labels
            }
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Labels saved to DynamoDB table')
    }
