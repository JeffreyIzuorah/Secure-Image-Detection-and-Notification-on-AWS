import boto3
import json


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')
sns = boto3.client('sns')
topic_arn = 'arn:aws:sns:us-east-1:232224276285:my-topic'
email = 'jeffreyisora@gmail.com'

def lambda_handler(event, context):
    for record in event['Records']:
        print(event)
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            print(new_image)
            print(new_image.keys())
            labels = new_image['Labels']['L']
            pedestrian_detected = False
            for label in labels:
                if label['M']['Name']['S'].lower() == 'pedestrian':
                    pedestrian_detected = True
                    break
            if pedestrian_detected:
                response = sns.publish(
                    TopicArn= topic_arn,
                    Message='A pedestrian was detected in image: {}'.format(new_image['ImageName']['S'])
                )
                print(response)