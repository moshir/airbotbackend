import boto3
import json
import pprint


def lambda_handler(event, context):
    # TODO implement
    baseresponse = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
    }


    User = boto3.resource("dynamodb").Table("databot_user")
    user = User.get_item(Key={"username": "moshir"})["Item"]

    baseresponse["body"] = {"success": True, "data": user}
    baseresponse["body"] = json.dumps(baseresponse["body"])
    return baseresponse
