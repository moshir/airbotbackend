import json
import pprint

from databot.glue.discover import DiscoverSchema
from databot.athena.query import AthenaQuery
from databot.lex.bot import Bot
from databot import errors
from databot.api import jsonserde

def handler(event, context):
    # TODO implement
    print "here we go"
    baseresponse = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
    }

    path = str(event["path"])


    if path=="/bot" :
        try :
            options = json.loads(event["body"])
            baseresponse["body"] = Bot.build(options["name"],options["intents"])
        except Exception,err :
            baseresponse["body"] = {
                "success" : False,
                "data" : {
                    "error" : err.message
                }
            }



    elif path=="/intent" :
        try :
            options = json.loads(event["body"])
            baseresponse["body"] = Bot.add_intent(options)
        except Exception,err :
            baseresponse["body"] = {
                "success" : False,
                "data" : {
                    "error" : err.message
                }
            }

    elif path=="/variable" :
        try :
            options = json.loads(event["body"])
            baseresponse["body"] = Bot.add_slot_type(options["name"],options["values"])
        except Exception,err :
            baseresponse["body"] = {
                "success" : False,
                "data" : {
                    "error" : err.message
                }
            }

    elif path=="/question" :
        try :
            options = json.loads(event["body"])
            baseresponse["body"] = json.dumps(Bot.send(**{
                "bot" : options["bot"],
                "input" : options["input"]
            }));
        except Exception,err :
            print "error query ", err
            baseresponse["body"] = {
                "success" : False,
                "data" : {
                    "error" : err.message
                }
            }

    elif path == "/query":
        try :
            options = json.loads(event["body"])
            baseresponse["body"] = json.dumps(AthenaQuery.run(**{
                "sql" : options["sql"]
            }))
        except Exception,err :
            print "error query ", err
            baseresponse["body"] = {
                "success" : False,
                "data" : {
                    "error" : err.message
                }
            }

    elif path == "/metadata":
        print "PATH IS /question"
        baseresponse["body"] = {"action": "metadata"}
    else :
        print "PATH IS none expected"
        baseresponse["body"] = {"action": "no action","body":  event["body"]}


    baseresponse["body"] = json.dumps(baseresponse["body"], default=jsonserde.json_serial)

    return baseresponse



if __name__=="__main__" :
    handler({
        "path"  : "/bot"
    },"")