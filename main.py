import boto3
import os
import json
import time
from dotenv import load_dotenv
from botocore.exceptions import ClientError


#Loading Aws credentials from dotenv file
load_dotenv()
secret_key = os.environ.get('my_secret_key')
access_key = os.environ.get('my_access_key')
session_key = os.environ.get('my_session_token')

# Create a function to initialize AWS clients
def create_clients():
    """
    Creates AWS clients for Lambda, SNS, SQS, S3, DynamoDB, EC2, and CloudFormation.
    """
    # Initialize AWS clients
    lambda_client = boto3.client('lambda', aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key,
                                 region_name='us-east-1',
                                 aws_session_token=session_key)
    sqs_client = boto3.client('sqs', aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name='us-east-1',
                              aws_session_token=session_key)
    sns_client = boto3.client('sns', aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name='us-east-1',
                              aws_session_token=session_key)
    s3_client = boto3.client('s3', aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                             region_name='us-east-1',
                             aws_session_token=session_key)
    dynamodb = boto3.client('dynamodb', aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key,
                                   region_name='us-east-1',
                                   aws_session_token=session_key)
    ec2 = boto3.client('ec2', aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name='us-east-1',
                              aws_session_token=session_key)
    cf = boto3.client('cloudformation', aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                             region_name='us-east-1',
                             aws_session_token=session_key)
    sns = boto3.client('sns',aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                            region_name='us-east-1',
                            aws_session_token=session_key
)                         
    return lambda_client, sqs_client, sns_client, s3_client, dynamodb, ec2, cf, sns

# Call the create_clients() function to initialize AWS clients
lambda_client, sqs_client, sns_client, s3_client, dynamodb, ec2, cf, sns = create_clients()


#create session
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1',
    aws_session_token=session_key
)

s3 = session.client('s3')

# Create a function to delete the event source mapping for a specific SQS queue
def delete_event_source_mapping():
    """
    Deletes the event source mapping for a specific SQS queue.
    """
    response = lambda_client.list_event_source_mappings(FunctionName='dynamodb_function')
    for mapping in response['EventSourceMappings']:
        if mapping['EventSourceArn'] == 'arn:aws:sqs:us-east-1:232224276285:my_queue_s1935095':
            lambda_client.delete_event_source_mapping(UUID=mapping['UUID'])
            print('Cleaning up residue from past runtimes...')

# Call the delete_event_source_mapping() function to clean up past runtimes
delete_event_source_mapping()

# Create an SQS queue
print('Now creating an SQS queue...')
queue_name = 'my_queue_s1935095'
queue_url = sqs_client.create_queue(QueueName=queue_name)['QueueUrl']
response = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
queue_arn = response['Attributes']['QueueArn']
print(f'SQS queue {queue_name} created successfully.')

def create_sns_topic(queue_arn):

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

    # Now we're creating a subscription with the second lambda function's ARN as the endpoint
    lambda_arn = 'arn:aws:lambda:us-east-1:232224276285:function:mailing_function'

    response = sns.subscribe(
        TopicArn=topic_arn,
        Protocol='lambda',
        Endpoint=lambda_arn,
        ReturnSubscriptionArn=True
    )

    subscription_arn = response['SubscriptionArn']
    print('SNS topic created successfully.')

    return topic_arn, subscription_arn

def launch_ec2_instance():

    # Launch a new EC2 instance with the default VPC and subnet
    image_id = 'ami-005f9685cb30f234b' # Amazon Linux 2 AMI
    instance_type = 't2.micro'

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName='vockey', 
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f'EC2 instance {instance_id} created successfully.')
    return instance_id

def create_dynamodb_table():

    print('Creating DynamoDB table from CloudFormation template...')
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
    print('DynamoDB table successfully created!')

topic_arn, subscription_arn = create_sns_topic(queue_arn)

# instance_id = launch_ec2_instance()

create_dynamodb_table()


# Use a CloudFormation template to create an S3 bucket
def create_s3_bucket():
    print('Creating S3 bucket...')
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
    print('S3 bucket successfully created.')


# Upload the provided image files to the S3 bucket using Boto3
def upload_files_to_s3_bucket():
    bucket_name = 'my-bucket-s1935095'
    directory = '/Users/jeffreyizuorah/School projects/CPD/images'

    for filename in os.listdir(directory):
        print("Current File: ", filename)
        filepath = os.path.join(directory, filename)
        time.sleep(30)

        with open(filepath, 'rb') as f:
            s3.upload_fileobj(f, 'my-bucket-s1935095', filename)
            print(f"{filename} uploaded to S3.")

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


create_s3_bucket()
upload_files_to_s3_bucket()

response = lambda_client.create_event_source_mapping(
    EventSourceArn=queue_arn,
    FunctionName='dynamodb_function',
    BatchSize=5,
    Enabled=True
)

response = dynamodb.describe_table(
    TableName='my_table_s1935095'
)
stream_arn = response['Table']['LatestStreamArn']

response = lambda_client.create_event_source_mapping(
    EventSourceArn=stream_arn,
    FunctionName='mailing_function',
    Enabled=True,
    StartingPosition='TRIM_HORIZON',
    BatchSize=10
)

print('Even source mapping completed')
