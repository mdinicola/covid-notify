from caseinfo import CaseInfo
from caseinfo import CaseInfoEncoder
import json

def lambda_handler(event, context):
    region = "Ontario"
    case_data = CaseInfo(region).fill()

    return {
        "statusCode": 200,
        "body": json.dumps(case_data, cls=CaseInfoEncoder)
    }
