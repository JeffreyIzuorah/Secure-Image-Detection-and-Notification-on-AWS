import json
import boto3

rekognition_client = boto3.client('rekognition')
dynamodb_resource = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')



def lambda_handler(event, context):
    # TODO implement
     for record in event['Records']:
        filename = json.loads(record['body'])['filename']
        print(f"Processing file: {filename}")
        
        response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': 'my-bucket-jeff',
                    'Name': filename
                }
            },
            MaxLabels=5,
            MinConfidence=80
        )
        
        table = dynamodb_resource.Table('my-table')
        item = {'filename': filename}
        for label in response['Labels']:
            item[label['Name']] = label['Confidence']
        table.put_item(Item=item)
        
        if 'Pedestrian' in item and item['Pedestrian'] >= 80:
            sns_client.publish(
                TopicArn='arn:aws:sns:us-east-1:232224276285:my-topic',
                Message=f"Pedestrian detected in {filename}"
            )