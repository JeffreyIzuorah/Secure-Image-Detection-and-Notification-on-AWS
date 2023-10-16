# Secure Image Detection and Notification on AWS
Project Description:
The project is an innovative image recognition and notification system designed to address the issue of pedestrian safety. It leverages a cloud-based architecture with a focus on cost efficiency and security. The primary goal is to detect pedestrians in images and notify relevant stakeholders when pedestrians are detected. The project is implemented using Amazon Web Services (AWS) cloud services, making it highly scalable and cost-effective.
Key Components and Architecture:

1.	EC2 Instance: The project begins with an Amazon Elastic Compute Cloud (EC2) instance. This serves as the user interface for uploading images. Users can upload images directly to this instance for processing.
2.	S3 Bucket: Once an image is uploaded to the EC2 instance, it's stored in an Amazon Simple Storage Service (S3) bucket. S3 is an object storage service that provides scalability and durability for data storage.
3.	SQS Queue: To manage image processing requests, the project utilizes an Amazon Simple Queue Service (SQS) queue. This message queue holds the image processing requests until they are picked up by the processing function.
4.	First Lambda Function: AWS Lambda, a serverless compute service, powers the first part of the image processing. When new images are uploaded, an event triggers the first Lambda function. It sends the image to Amazon Rekognition for pedestrian detection.
5.	Amazon Rekognition: Amazon Rekognition, an AWS service, employs deep learning to analyze images. It detects pedestrians and provides insights into image content.
6.	DynamoDB: For data persistence, the processed image data is stored in Amazon DynamoDB, a NoSQL database service. DynamoDB allows for efficient retrieval of data.
7.	Second Lambda Function: The second Lambda function plays a pivotal role. It is triggered by new items added to the DynamoDB table. The function checks if pedestrians were detected and, if so, sends email notifications.
8.	SNS (Simple Notification Service): Notifications are sent via Amazon SNS, which is a publish-subscribe service. In this case, SNS sends email notifications to alert relevant stakeholders.

Cost Optimization:
The project is designed with cost optimization in mind. Several AWS services employed are pay-as-you-go, ensuring cost efficiency. By ensuring that Lambda functions are short-lived and use minimal resources, it reduces operational costs. This cost-effective approach makes it feasible to run the system over extended periods without incurring exorbitant expenses.

Security:
Security is a top priority in the project. AWS Identity and Access Management (IAM) controls access to AWS resources, ensuring that only authorized entities can interact with the system. Data at rest is encrypted in the S3 bucket, and data in transit is secured with SSL/TLS encryption. Additionally, AWS CloudTrail is employed to monitor API activity, providing an extra layer of security by detecting and alerting for any unauthorized access attempts.

Demonstration:
In a live demonstration, an image of a pedestrian is uploaded to the EC2 instance. The system processes the image, detects the pedestrian, and sends an email notification through SNS to alert stakeholders. This hands-on demonstration showcases the practicality and effectiveness of the solution.

Improvements:
While the current architecture is functional, there are opportunities for enhancement. For instance, image resizing before processing could reduce processing time and costs. Implementing Amazon CloudWatch to monitor system metrics and identify performance issues could further improve the system's efficiency.

Conclusion:
The project provides a scalable, cost-effective, and secure solution to address pedestrian safety concerns. It demonstrates how AWS services can be harnessed to create an efficient image recognition system with applications in various domains, including public safety, traffic management, and surveillance.

