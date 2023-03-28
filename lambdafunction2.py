import boto3
import json



dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my_table_s1935095')
sns = boto3.client('sns')
topic_arn = 'arn:aws:sns:us-east-1:232224276285:my_topic_s1935095'
email = 'jeffreyisora@gmail.com'

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            labels = new_image['Labels']['L']
            pedestrian_detected = False
            for label in labels:
                if label['M']['Name']['S'].lower() == 'pedestrian':
                    pedestrian_detected = True
                    break
            if pedestrian_detected:
                response = sns.publish(
                    TopicArn=topic_arn,
                    Message='A pedestrian was detected in image: s3://{}/{}'.format(
                        new_image['s3_bucket']['S'], new_image['s3_key']['S'])
                )
                print(response)
