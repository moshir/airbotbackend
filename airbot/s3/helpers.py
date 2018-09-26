import boto3


class S3Helpers :


    @staticmethod
    def get_presigned_url( bucket, key):
        s3 = boto3.client("s3")
        return s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket, "Key": key}
        ).replace("s3.amazonaws.com", "s3-eu-west-1.amazonaws.com")


'''
if __name__=="__main__" :
    print(S3Helpers.get_presigned_url("airbot2018data","myentity"))
    import sys
    import time
    client = boto3.client("s3")
    response = client.list_buckets()
    for b in response["Buckets"] :
        answer = raw_input("Do you want to delete  bucket `%(Name)s`?"%b)
        if answer.upper() in ["Y","YES","1"] :
            S3 = boto3.resource('s3')
            Bucket = S3.Bucket(b["Name"])
            total = len(list(Bucket.objects.all()))
            for i,object in enumerate(Bucket.objects.all()):
                pct= int(100.0*((i+0.0)/(total+0.0)))
                print( "|"*pct+"%(pct)s%% done \r"%vars(),end='')
                sys.stdout.flush()
                Object = S3.Object(b["Name"],object.key)
                #print Object
                Object.delete()
            nbtry = 10
            success=False
            while (not success and nbtry>0):
                try :
                    print("Deleting bucket "+b["Name"])
                    Bucket.delete()
                    success = True
                except Exception, e :
                    print(str(e))
                    nbtry =nbtry -1
                    time.sleep(1)
                    pass
            if success :
                print ("Successfully deleted bucket")
            else :
                print("Failed to delete bucket")
        else :
            print ("Skipping")
'''