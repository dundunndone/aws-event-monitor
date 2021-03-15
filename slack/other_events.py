from send_to_slack import * 

def other_events(event):
    # Get custom event details
    eventID = (event["detail"]["eventID"])

    # Custom Slack Message    
    color = "FF0000"
    message = [{"value": f"*Event ID*: {eventID}"}]
    send_to_slack(event, message, color)