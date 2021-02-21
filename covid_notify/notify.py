from caseinfo import CaseInfo
import requests
import json
import os

def lambda_handler(event, context):
    region = "Ontario"
    case_data = CaseInfo(region).fill()

    message = "Could not retrieve info.   Please try again later"
    if case_data.is_stale():
        message = f'{region} reported {case_data.new_cases} new cases yesterday'
    else:
        message = f'{region} is reporting {case_data.new_cases} today'
        

    request_data = {
        "token": os.environ['pushoverToken'],
        "user": os.environ['pushoverUser'],
        "message": message
    }

    #response = requests.post("https://api.pushover.net/1/messages.json", request_data)

    return {
        #"statusCode": response.status_code,
        "statusCode": 200,
        #"body": json.dumps(response.json()),
        "body": json.dumps(request_data),
    }
