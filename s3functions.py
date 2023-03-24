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


#Creating the necessary clients for our application
print('Creating the necessary clients for the program...')

client = boto3.client('lambda', 
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key)

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

ec2 = boto3.client(
    'ec2',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

#create session
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

s3 = session.client('s3')

dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

lambda_client = boto3.client(
    'lambda',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

cf = boto3.client('cloudformation',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key)


response = client.list_event_source_mappings(FunctionName='dynamodb_function')
for mapping in response['EventSourceMappings']:
    if mapping['EventSourceArn'] == 'arn:aws:sqs:us-east-1:232224276285:my_queue_s1935095':
        client.delete_event_source_mapping(UUID=mapping['UUID'])
        print('Cleaning up residue from past runtimes...')

#Creating an sqs queue
print('Now creating sqs queue...')
queue_name = 'my_queue_s1935095'
queue_url = sqs_client.create_queue(QueueName=queue_name)['QueueUrl']

response = sqs_client.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['QueueArn']
)

queue_arn = response['Attributes']['QueueArn']

print(f'SQS queue {queue_name} created successfully.')

# Create an SNS topic
print('Creating sns topic and necessary subscriptions...')
response = sns.create_topic(Name='my_topic_s1935095')

# Get the ARN of the SNS topic
topic_arn = response['TopicArn']

# Subscribe the SQS queue to the SNS topic
subscription = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='sqs',
    Endpoint=queue_arn
)

# Subscribe an email address to the SNS topic
response = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='jeffreyisora@gmail.com'
)

#Now we're creating a subscription wth the second lambda functions ARN as the endpoint
lambda_arn = 'arn:aws:lambda:us-east-1:232224276285:function:mailing_function'

response = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='lambda',
    Endpoint=lambda_arn,
    ReturnSubscriptionArn=True
)

subscription_arn = response['SubscriptionArn']

# Launch a new EC2 instance with the default VPC and subnet

# image_id = 'ami-005f9685cb30f234b' # Amazon Linux 2 AMI
# instance_type = 't2.micro'

# response = ec2.run_instances(
#     ImageId=image_id,
#     InstanceType=instance_type,
#     MinCount=1,
#     MaxCount=1,
#     KeyName='vockey', 
# )

# instance_id = response['Instances'][0]['InstanceId']
# print(f'EC2 instance {instance_id} created successfully.')

# Create a DynamoDB table
print('dynamodb table creating from cf template...')

stack_name = 'my-dynamodb-stack'

template = {
    "Resources": {
        "MyTable": {
            "Type": "AWS::DynamoDB::Table",
            "Properties": {
                "AttributeDefinitions": [
                    {
                        "AttributeName": "ImageName",
                        "AttributeType": "S"
                    }
                ],
                "KeySchema": [
                    {
                        "AttributeName": "ImageName",
                        "KeyType": "HASH"
                    }
                ],
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                },
                "StreamSpecification" :{
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "TableName": "my_table_s1935095"
            }
        }
    }
}

cf.create_stack(StackName=stack_name, TemplateBody=json.dumps(template))

print('Dynamodb table successfully created!')

# stream_arn = response['TableDescription']['LatestStreamArn']


# Use a CloudFormation template to create an S3 bucket
print('S3 bucket creating from cf template...')
stack_name = 'my-s3-stack'

template = {
    "Resources": {
        "MyBucketJeff": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": "my-bucket-s1935095"
            }
        }
    }
}

cf.create_stack(StackName=stack_name, TemplateBody=json.dumps(template))

print('S3 bucket successfully created!')

# Upload the provided image files to the S3 bucket using Boto3

bucket_name = 'my-bucket-s1935095'
directory = '/Users/jeffreyizuorah/School projects/CPD/images'

for filename in os.listdir(directory):
    print("Current File: ", filename)
    filepath = os.path.join(directory, filename)
    time.sleep(30)

    with open(filepath, 'rb') as f:
        s3.upload_fileobj(f, 'my-bucket-s1935095', filename)

        print(f"{filename} uploaded to s3")

        message = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "my-bucket-s1935095"
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
print(f"Message sent to SQS queue {queue_name} for all files.")


response = lambda_client.create_event_source_mapping(
    EventSourceArn=queue_arn,
    FunctionName='dynamodb_function',
    BatchSize=5,
    Enabled=True
)

print('Even source mapping completed')


response = dynamodb.describe_table(
    TableName='my_table_s1935095'
)

table_description = response['Table']
stream_arn = table_description['LatestStreamArn']

response = lambda_client.create_event_source_mapping(
    EventSourceArn=stream_arn,
    FunctionName='mailing_function',
    Enabled=True,
    StartingPosition='LATEST'
)

