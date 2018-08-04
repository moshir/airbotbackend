import time
import boto3

client = boto3.client('lex-models', region_name="eu-west-1")

slottypes = client.get_slot_types()

for s in  slottypes["slotTypes"] :
    print "cleaning", s
    response = client.delete_slot_type(
        name=s["name"]
    )
    time.sleep(5)



