import logging, boto3, json, os, sys, traceback, requests, datetime
from boto3 import resource
from s3_public import *
from other_events import *

s3 = boto3.client('s3')
SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
bucket_name = os.environ['EVENTS_LOGS_BUCKET']

def lambda_handler(event, context):
    print("-- Event Log --")
    print(json.dumps(event))
    key_name = 'eventlogs'
    region = boto3.Session().region_name
    errors = ""
    otherEvents = json.loads(os.environ['otherEvents']) # For Generic Events

    try:
        #Reads & logs event details to s3
        today = datetime.date.today()            
        evtId = event["id"]
        acctID = event["account"]        
        file = evtId + ".json"
        key = key_name + '/' + acctID + '/' + region + '/' + str(today) + '/' + evtId + '.json'
        strEvent = str.encode(json.dumps(event))    
        upload = s3.put_object(Body=strEvent, Bucket=bucket_name, Key=key, ServerSideEncryption='aws:kms')
        print(f'Logged: s3://{bucket_name}/{key}')  
        #Events with errors are not processed
        if "errorCode" in event['detail'].keys():
            return
        #Reads generic event details
        event_type = event["detail"]["eventName"]
        if "additionalEventData" in event["detail"].keys():
            if "MFAUsed" in event["detail"]["additionalEventData"].keys():            
                nomfa = event["detail"]["additionalEventData"]["MFAUsed"]
            else:
                nomfa = event["detail"]["additionalEventData"]
        else:
            nomfa = "None"
        userType = event["detail"]["userIdentity"]["type"]   
        if userType == "IAMUser":
            user_id = event["detail"]["userIdentity"]["userName"]
        elif userType == "Root":
            user_id = event["detail"]["userIdentity"]["arn"].split(":")[5]

        #For each CloudWatch Event rule, add the associated event name(s)
        #   (1) add a new .py file to customize event notifications OR
        #   (2) add event name to other_events - event notification will contain eventID
        #Function will detect the event name and send it to the target .py file for processing
    
        if event_type == "PutBucketAcl": 
            s3_public(event) 

        if event_type in otherEvents:
            other_events(event) 

    except Exception as error:
        errors = traceback.format_exc()
        errorHandler("index",errors)