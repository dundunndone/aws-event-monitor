import logging, boto3, json, os, sys, traceback
import requests
from boto3 import resource

SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
aliases = json.loads(os.environ['accountAliases'])

def send_to_slack(event, message, color):
    event_type = event["detail"]["eventName"]
    aws_account = event["detail"]["userIdentity"]["accountId"]
    userType = event["detail"]["userIdentity"]["type"]
    if userType:
        user_id = event["detail"]["userIdentity"]["arn"]
    else:
        user_id = event["detail"]["userIdentity"]["userName"]
    aws_region = event["detail"]["awsRegion"]
    source = event["detail"]["sourceIPAddress"]
    event_time = event["detail"]["eventTime"].replace('T', " - ")
    full_username = user_id.split(":")[5]
    alias = aliases[event['account']] #Checks account ID and adds account alias
    slack_message  = {
        "attachments": [
            {
                "pretext": f"*EVENT*: {event_type} - (*{alias}*)",
                "color": f"{color}",
                "fields": [
                    {"value": f"*Time*: {event_time}"},
                    {"value": f"*Region*: {aws_region}"},
                    {"value": f"*Source*: {source}"},
                    {"value": f"*User*: {full_username}"}
                ]
            }
        ]
    }
    for value in message:
        slack_message['attachments'][0]['fields'].append(value)
    response = requests.post(SLACK_WEBHOOK, data=json.dumps(slack_message))
    print(f'Slack ACK: {response}')
    return response

def errorMsg(name,error):
    if error != "":
        slack_message = {
            "attachments": [
                {
                    "pretext": f"*EVENT*: {name} - (*ERROR*)",
                    "color": f"FF0000",
                    "fields": [
                        {"value": f"*ERROR*: {error}"}
                    ]
                }
            ]
        }
        response = requests.post(SLACK_WEBHOOK, data=json.dumps(slack_message))
        print(f'Slack ACK: {response}')
        return response