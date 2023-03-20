import boto3
import json


topic_arn = 'arn:aws:sns:us-east-1:232224276285:my-topic'
email = 'jeffreyisora@gmail.com'

def lambda_handler(event, context):
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        labels = message['labels']
        pedestrian_detected = False
        image_names = []
        for label in labels:
            if label['Name'].lower() == 'pedestrian':
                pedestrian_detected = True
                image_names.append(message['s3_key'])
                break
        if pedestrian_detected:
            sns = boto3.client('sns')
            response = sns.publish(
                TopicArn= topic_arn,
                Message='Pedestrian detected in images: {}'.format(image_names)
            )
            print(response)
    except Exception as e:
        print(e)
        raise e

    # if 'Pedestrian' in labels:
    #     # Get the subscribed email address from the environment variables
    #     email = 'jeffreyisora@gmail.com'
        
    #     # Create the SNS client
    #     sns = boto3.client('sns')
        
    #     # Send the notification email to the subscribed email address
    #     subject = 'Pedestrian detected in image {}'.format(image_name)
    #     message = 'Pedestrian was detected in image {}. Labels: {}'.format(image_name, labels)
    #     response = sns.publish(
    #         TopicArn=topic_arn,
    #         Message=message,
    #         Subject=subject
    #     )
        
    #     # Print the response from the publish method to the CloudWatch logs
    #     print('Notification email sent to {} with response: {}'.format(email, response))
        
    # else:
    #     print('No pedestrian detected in image {}. Labels: {}'.format(image_name, labels))


    # response = sns.publish(
    #         TopicArn=topic_arn,
    #         Message=json.dumps({'default': json.dumps(message)}),
    #         MessageStructure='json',
    #         Subject='Pedestrian Detected',
    #         TargetArn='arn:aws:sns:us-east-1:123456789012:email-subscription:jeffreyisora@gmail.com'
