import pprint
import boto3
import errors
import time

class AthenaQuery:
    @classmethod
    def start(cls,**kwargs):
        client = boto3.client('athena', region_name="eu-west-1")
        try :
            response = client.start_query_execution(
                QueryString=kwargs["sql"],
                QueryExecutionContext={
                    'Database': 'sampledb'
                },
                ResultConfiguration={
                    'OutputLocation': 's3://myairbot/athena/queries'
                }
            )
            return {
                "success" : True,
                "data" : {
                    "QueryExecutionId" : response["QueryExecutionId"]
                }
            }
        except Exception ,e:
            return {
                "success" : False,
                "data" : {
                    "error" : e.message
                }
            }

    @classmethod
    def get_query_execution(cls, **kwargs):
        client = boto3.client('athena', region_name="eu-west-1")
        try :
            response = client.get_query_execution(
                QueryExecutionId = kwargs["QueryExecutionId"]
            )
            return {
                "success" : True,
                "data" : {
                    "status" : response["QueryExecution"]["Status"]["State"]
                }
            }
        except Exception ,e:
            return {
                "success": False,
                "data": {
                    "error" : e.message
                }
            }

    @classmethod
    def json(cls, athenaresponse):
        records = []
        fields = athenaresponse["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        for r in athenaresponse["ResultSet"]["Rows"][1:] :
            data = r["Data"]
            record = {}
            for index, v in enumerate(data) :
                fieldname = fields[index]["Name"]
                fieldtype= v.keys()[0]
                record[fieldname] = v[fieldtype]
            records.append(record)
        return records

    @classmethod
    def get_results(cls,**kwargs):
        client = boto3.client('athena', region_name="eu-west-1")
        try :
            response = client.get_query_results(
                QueryExecutionId = kwargs["QueryExecutionId"],
                MaxResults = 500
            )
            print "Response received"
            print pprint.pformat(response)
            return {
                "success" : True,
                "data" : {
                    #"records" : response["ResultSet"]["Rows"],
                    #"metadata" : response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"],
                    "records" : cls.json(response)
                }
            }
        except Exception ,e:
            return {
                "success" : False,
                "data" : {
                    "error" : e.message
                }
            }

    @classmethod
    def run(cls,**kwargs):
        print kwargs
        start = cls.start(**kwargs)
        if start["success"] is True:
            completed = False
            nbtry = 10
            while (completed is False) and (nbtry>0):
                print "Looping "
                nbtry -=1
                watcher = cls.get_query_execution(**{"QueryExecutionId" : start["data"]["QueryExecutionId"]})
                print "watcher", pprint.pformat(watcher)
                if watcher["success"] is True:
                    if watcher["data"]["status"] =="SUCCEEDED":
                        print "watcher succeeded"
                        completed  = True
                        return cls.get_results(**{"QueryExecutionId" : start["data"]["QueryExecutionId"]})
                    else:
                        print "waiting" , nbtry
                        time.sleep(3)
                if watcher["success"] is False :
                    return watcher
            return {
                "success": False,
                "data" : {
                    "error" : "Timed out"
                }
            }
        else :
            return start






if __name__=="__main__":
    #r = AthenaQuery.start(**{"sql" : "select * from sampledb.data;"})
    #r = AthenaQuery.get_query_execution(**{"QueryExecutionId": r["data"]["QueryExecutionId"]})
    #r = AthenaQuery.get_query_execution(**{"QueryExecutionId": "4c745380-d0a0-406e-87bf-5b8fb1984a56"})
    print pprint.pformat(AthenaQuery.run(**{"sql" : "select count(*) as nb from sampledb.user where city='bordeaux' limit 100;"}))