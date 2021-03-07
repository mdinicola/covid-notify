from caseinfo import CaseInfo
import json

def lambda_handler(event, context):
    region = "Ontario"
    case_data = CaseInfo(region).fill(speak=True)

    output = {}
    # get data from POST request
    request_data = json.loads(event['body'])

    output['session'] = {}
    output['session']['id'] = request_data['session']['id']
    output['session']['params'] = request_data['session']['params']
    output['prompt'] = {}
    output['prompt']['override'] = False
    output['prompt']['firstSimple'] = {}
    output['prompt']['firstSimple']['speech'] = case_data.message
    output['prompt']['firstSimple']['text'] = case_data.message

    return {
        "statusCode": 200,
        "body": json.dumps(output),
    }
