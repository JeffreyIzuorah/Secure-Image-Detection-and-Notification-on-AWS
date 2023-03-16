import json
import boto3


topic_arn = 'arn:aws:sns:us-east-1:232224276285:my-topic'

def lambda_handler(event, context):
    # Extract message from the event and get the image name
    message = json.loads(event['Records'][0]['body'])
    image_name = message['image_name']
    
    # Check if the label pedestrian is in the detected labels
    labels = message['labels']
    if 'Pedestrian' in labels:
        # Get the subscribed email address from the environment variables
        email = 'jeffreyisora@gmail.com'
        
        # Create the SNS client
        sns = boto3.client('sns')
        
        # Send the notification email to the subscribed email address
        subject = 'Pedestrian detected in image {}'.format(image_name)
        message = 'Pedestrian was detected in image {}. Labels: {}'.format(image_name, labels)
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        
        # Print the response from the publish method to the CloudWatch logs
        print('Notification email sent to {} with response: {}'.format(email, response))
        
    else:
        print('No pedestrian detected in image {}. Labels: {}'.format(image_name, labels))
