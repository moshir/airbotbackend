from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors

import  boto3
import json

@App.field(
    "getStsToken",
    path  = "Mutation/getStsToken",
    argmap= {
        "/arguments/identity" : "identity"
    }
)
def get_sts_token(identity=None) :
    client = boto3.client("sts", region_name="eu-west-1")
    response = client.get_session_token()
    return json.dumps(response["Credentials"])


