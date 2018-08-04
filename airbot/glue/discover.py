
import pprint
import boto3

class DiscoverSchema:
    @classmethod
    def run(cls,**kwargs):
        client = boto3.client('glue', region_name="eu-west-1")
        try :
            response = client.get_table(
                DatabaseName='sampledb',
                Name=kwargs["entity"]
            )
            schema = response["Table"]["StorageDescriptor"]["Columns"]
            return {
                "success" : True,
                "data" : schema
            }
        except Exception :
            return {
                "success" : False,
                "data" : errors.ObjectNotFound(kwargs["entity"])
            }

if __name__=="__main__" :
    r = DiscoverSchema.run(entity="data")
    print pprint.pformat(r)
