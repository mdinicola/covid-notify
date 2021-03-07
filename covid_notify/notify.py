from secretsmanager import SecretsManagerSecret
from caseinfo import CaseInfo
import requests
import json
import os
import boto3

def lambda_handler(event, context):
    secret = SecretsManagerSecret(boto3.client('secretsmanager'), os.environ['SecretName'])
    pushover_user = secret.get_value(os.environ['UserKey'])
    pushover_token = secret.get_value(os.environ['TokenKey'])

    region = "Ontario"
    case_data = CaseInfo(region).fill()
    
    if case_data.is_stale():
        message = f'{region} reported {case_data.new_cases} new cases yesterday'
    else:
        message = f'{region} is reporting {case_data.new_cases} today'
        
    request_data = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }

    response = requests.post("https://api.pushover.net/1/messages.json", request_data)

    return {
        "statusCode": response.status_code,
        "statusCode": 200,
        "body": json.dumps(response.json())
    }
