import time
import pprint
from  boto3 import client

def inspect_slot(slottype) :
    c = client('lex-models', region_name="eu-west-1")

    response = c.get_slot_type(
        name=slottype
    )
    return response


if __name__=="__main__" :
    print pprint.pformat(inspect_slot("democustomer"))

