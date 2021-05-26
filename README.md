# AWS Event Monitor
Provides real-time event notifications from AWS accounts using CloudWatch Event Rules to Slack.

## Purpose

Lets be real, companies need 100% visibility on activity happening across all account/regions. When it comes to event notifications, getting real-time notifications out of SaaS or an on-prem product can fall short. Even native services like CloudWatch Alarms are not ideal, as alarm notifications require you to login to the AWS console to view the Alarm. When it comes to cloud security, having all of the information in one step is vital.

Event monitor was created to provide event notifications in real time. This tool can quickly alert you to any new public S3 bucket, snapshot shared cross-account, public security group rule, and other critical events across your AWS accounts.

![AWS Event Monitor Diagram](https://github.com/sdunn15/aws-event-monitor/images/workflow.jpg)


## Pre-Reqs

* Deploying Lambda Layer (included) to support the python requests module.
* For Slack, you will need to create a Slack channel and setup an Incoming Webhook to send your events to.


## Deployment

Deploy templates and Lambda resources in order.

* `main.yml`
  - **Contains**: IAM & S3 resources
  - **Deploy**: us-east-1 only 
* `s3_lambda.yml`
  - **Contains**: S3 resources for Lambda
  - **Deploy**: All regions in primary account. Creates multiple S3 buckets across all of your regions.

     > **Example**: target-lambda-bucket-`012345678912`

  * **Additional Steps**: Starting with your bucket in us-east-1, create 2 sub-folders and upload both .zip files shown below. 

      1: For your Lambda layers - upload requests.zip
       ```
       S3Key: !Join [ '', ['layers/requests.zip']]
       ``` 

      2: For your Slack Function, zip / upload all files
       ```
       S3Key: !Join [ '', ['slack/index.zip']]
       ```
  * For the remaining buckets, you will need to perform the **same actions** so that all of your buckets have the same packages across the remaining regions. Why is that? Well...Lambda is a regional service and must pull from a bucket within the same region.
* `event-monitor.yml`
  - **Contains**: Lambda functions, Layer, and Event Rules.
  - **Pre-req**: Must have all .zip files uploaded to S3, otherwise this StackSet will fail.
  - **Additional Steps**: Add/Input your Slack webhook URL within the template: `https://hooks.slack.com/services/...`
  - **Deploy**: From primary account, deploy to all regions.
  - **ENABLE multi-account support** using *Event Bus*: Add an `EventBusPolicy` below, include your AWS OrgID, add above the `LambdaLayer` element, and re-run the StackSet update. 
    ```  
    EventBusPolicy:
      Type: 'AWS::Events::EventBusPolicy'
      Properties:
        Action: events:PutEvents
        Principal: '*'
        StatementId: 'PrimaryEventBus'
        Condition:
          Type: 'StringEquals'
          Key: 'aws:PrincipalOrgId'
          Value: 'o-exampleorgid'
    ```

    - If you do not have access to your AWS Organization ID, you'll need to modify the template to support AWS Accounts. (see AWS docs for details)

## Multi-account deployment (**OPTIONAL**)

Ensure you have the above templates deployed successfully.

* `main-member.yml`
  - **Contains**: IAM resouces
  - **Deploy**: From primary account, deploy as StackSet to secondary accounts in us-east-1 only.
* `event-monitor-member.yml` 
  - **Contains**: Event Rules that send events back to your Event Bus within your primary account
  - **Deploy**: From primary account, deploy as StackSet to all regions & secondary accounts 


## Supports

* Supports both customized and generic event notifications for use with Slack.
* Customizable template to send events to different Slack channels based on AWS account.
* If your planning a multi-account setup, it's important to note that Event Bus will not process some read-based events from secondary accounts. For example `ec2:DescribeInstances` events won't be forwarded cross account (*known issue with AWS*). 
* This function uses python `requests` module to send events to Slack. [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) are used to package the module and upload the `requests.zip` file into Lambda.
