import boto3
import os
import json
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError


#Loading Aws credentials from dotenv file
load_dotenv()
secret_key = os.environ.get('my_secret_key')
access_key = os.environ.get('my_access_key')
session_key = os.environ.get('my_session_token')


#Create an sqs client
sqs = boto3.client(
    'sqs',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

# This creates a new SQS queue with the name my_queue and returns its URL.
queue_name = 'my_queue'
response = sqs.create_queue(QueueName=queue_name)
queue_url = response['QueueUrl']


#Create an ec2 client
ec2 = boto3.client(
    'ec2',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

# # Launch a new EC2 instance with the default VPC and subnet


image_id = 'ami-005f9685cb30f234b' # Amazon Linux 2 AMI
instance_type = 't2.micro'

response = ec2.run_instances(
    ImageId=image_id,
    InstanceType=instance_type,
    MinCount=1,
    MaxCount=1,
)

instance_id = response['Instances'][0]['InstanceId']
print(f'EC2 instance {instance_id} created successfully.')





# Create a DynamoDB table
response = dynamodb_client.create_table(
    TableName='my-table',
    KeySchema=[
        {
            'AttributeName': 'image_name',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'image_name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)


# Use a CloudFormation template to create an S3 bucket

# Upload the provided image files to the S3 bucket using Boto3

# Configure the SQS queue to trigger a Lambda function when a message is received

# Write a Lambda function in Python (Boto3) to extract relevant details such as file name from the SQS message

# Use Boto3 to call the AWS Rekognition service for label detection

# Extract the relevant information from the Rekognition response and save the top five labels along with their confidence scores in the DynamoDB table

# If the label pedestrian is detected, trigger a second Lambda function that immediately notifies the email address subscribed to the SNS topic.



