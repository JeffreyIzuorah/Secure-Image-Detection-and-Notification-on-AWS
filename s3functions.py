import boto3
import os
import json
import logging
import time
from dotenv import load_dotenv
from botocore.exceptions import ClientError


#Loading Aws credentials from dotenv file
load_dotenv()
secret_key = os.environ.get('my_secret_key')
access_key = os.environ.get('my_access_key')
session_key = os.environ.get('my_session_token')


client = boto3.client('lambda', 
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key)

response = client.list_event_source_mappings(FunctionName='my-function')
for mapping in response['EventSourceMappings']:
    if mapping['EventSourceArn'] == 'arn:aws:sqs:us-east-1:232224276285:my_queue':
        client.delete_event_source_mapping(UUID=mapping['UUID'])
        print(response)
#Create an sqs client
sqs = boto3.client(
    'sqs',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

sns = boto3.client(
    'sns',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

# This creates a new SQS queue with the name my_queue and returns its URL.
# queue_name = 'my_queue'
# response = sqs.create_queue(QueueName=queue_name)
# queue_url = response['QueueUrl']


s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

sqs_client = boto3.client(
    'sqs',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)


# Create an SNS topic
response = sns.create_topic(Name='my-topic')

# Get the ARN of the SNS topic
topic_arn = response['TopicArn']

queue_name = 'my_queue'
queue_url = sqs_client.create_queue(QueueName=queue_name)['QueueUrl']

response = sqs_client.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['QueueArn']
)

queue_arn = response['Attributes']['QueueArn']

print(f'SQS queue {queue_name} created successfully.')

# Subscribe the SQS queue to the SNS topic
subscription = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='sqs',
    Endpoint=queue_arn
)


#Create an ec2 client
ec2 = boto3.client(
    'ec2',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

# Launch a new EC2 instance with the default VPC and subnet

# image_id = 'ami-005f9685cb30f234b' # Amazon Linux 2 AMI
# instance_type = 't2.micro'

# response = ec2.run_instances(
#     ImageId=image_id,
#     InstanceType=instance_type,
#     MinCount=1,
#     MaxCount=1,
# )

# instance_id = response['Instances'][0]['InstanceId']
# print(f'EC2 instance {instance_id} created successfully.')


# Create a DynamoDB table

# cf = boto3.client('cloudformation',
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key,
#     region_name='us-east-1',
#     aws_session_token=session_key)

# stack_name = 'my-dynamodb-stack'

# template = {
#     "Resources": {
#         "MyTable": {
#             "Type": "AWS::DynamoDB::Table",
#             "Properties": {
#                 "AttributeDefinitions": [
#                     {
#                         "AttributeName": "ImageName",
#                         "AttributeType": "S"
#                     }
#                 ],
#                 "KeySchema": [
#                     {
#                         "AttributeName": "ImageName",
#                         "KeyType": "HASH"
#                     }
#                 ],
#                 "ProvisionedThroughput": {
#                     "ReadCapacityUnits": 5,
#                     "WriteCapacityUnits": 5
#                 },
#                 "TableName": "my-table"
#             }
#         }
#     }
# }

# cf.create_stack(StackName=stack_name, TemplateBody=json.dumps(template))



# Use a CloudFormation template to create an S3 bucket

# cf = boto3.client('cloudformation',
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key,
#     region_name='us-east-1',
#     aws_session_token=session_key)

# stack_name = 'my-s3-stack'

# template = {
#     "Resources": {
#         "MyBucketJeff": {
#             "Type": "AWS::S3::Bucket",
#             "Properties": {
#                 "BucketName": "my-bucket-jeff"
#             }
#         }
#     }
# }

# cf.create_stack(StackName=stack_name, TemplateBody=json.dumps(template))

# Upload the provided image files to the S3 bucket using Boto3


#create session
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

s3 = session.client('s3')
sqs_client = boto3.client(
    'sqs',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
    )
bucket_name = 'my-bucket-jeff'
directory = '/Users/jeffreyizuorah/School projects/CPD/images'

for filename in os.listdir(directory):
    print("Current File: ", filename)
    filepath = os.path.join(directory, filename)
    time.sleep(30)

    with open(filepath, 'rb') as f:
        s3.upload_fileobj(f, 'my-bucket-jeff', filename)

        print(f"{filename} uploaded to s3")

        message = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "my-bucket-jeff"
                        },
                        "object": {
                            "key": f"{filename}"
                        }
                    }
                }
            ]
        }
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
print(f"Message sent to SQS queue {queue_name} for {filename}.")


# Configure the SQS queue to trigger a Lambda function when a message is received
queue_name = 'my-queue'


# Write a Lambda function in Python (Boto3) to extract relevant details such as file name from the SQS message
lambda_client = boto3.client(
    'lambda',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

response = lambda_client.create_event_source_mapping(
    EventSourceArn=queue_arn,
    FunctionName='my-function',
    BatchSize=5,
    Enabled=True
)

print(response)



# Use Boto3 to call the AWS Rekognition service for label detection

# Extract the relevant information from the Rekognition response and save the top five labels along with their confidence scores in the DynamoDB table

# If the label pedestrian is detected, trigger a second Lambda function that immediately notifies the email address subscribed to the SNS topic.



