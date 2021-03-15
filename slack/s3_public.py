from send_to_slack import * 

def s3_public(event):
    # Get custom event details
    bucket_name = event["detail"]["requestParameters"]["bucketName"]   
    #Custom Slack Message
    message  = [{"value": f"*Public Bucket*: {bucket_name}"}]
    color = "FF0000"
    send_to_slack(event, message, color)
