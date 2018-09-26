import boto3
import json
import pprint
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return str(obj)


class ResourceNotFound(Exception):
    pass


class Bot:
    """ A Simple wrapper on top of AWS LEX API
    Args :
        name : string
            Name of the bot
    """

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_bot(cls, name):
        """ Lex Bot Getter
        Returns : dict
            A bot spec as returned by boto3 lex api"""
        try:
            response = cls.lex().get_bot(
                name=name,
                versionOrAlias="$LATEST"
            )
            return response
        except Exception:
            raise ResourceNotFound(name)

    @classmethod
    def get_slot_type(cls, name):
        """ Lex Slot Type Getter
        Returns : dict
            A slot type spec as returned by boto3 lex api"""
        try:
            response = cls.lex().get_slot_type(
                name=name,
                version='$LATEST'
            )
            return response
        except Exception, e:
            raise ResourceNotFound(name)

    @classmethod
    def add_slot_type(cls, slotname, values):
        """ Adds a slot type to an intent """
        args = {
            "name": slotname,
            "description": 'xxx',
            "enumerationValues": [
                {'value': v} for v in values
            ],
            "valueSelectionStrategy": 'ORIGINAL_VALUE'
        }
        try:
            slotdata = cls.get_slot_type(slotname)
            checksum = slotdata["checksum"]
            args["checksum"] = checksum
        except ResourceNotFound, e:
            pass
        cls.lex().put_slot_type(**args)

    @classmethod
    def get_intent(cls, name):
        """ returns an intent by its name"""
        try:
            response = cls.lex().get_intent(
                name=name,
                version='$LATEST'
            )
            return response
        except Exception, e:
            raise ResourceNotFound(name)

    @classmethod
    def add_intent(cls, intent):
        """ creates an intent """

        args = {
            "name": intent["name"],
            "description": 'string',
            "slots": [
                {
                    "name": s["name"],
                    "description": "xxx",
                    "slotType": s["slotType"],
                    "slotConstraint": "Optional",
                    "slotTypeVersion": cls.get_slot_type(name=s["slotType"])["version"]
                }
                for s in intent["slots"]
            ],
            "fulfillmentActivity": {
                'type': 'ReturnIntent'
            },
            "sampleUtterances": intent["sampleUtterances"]
        }
        try:
            r = cls.get_intent(intent["name"])
            checksum = r["checksum"]
            args["checksum"] = checksum
        except Exception, e:
            print e
            # raise e
            pass
        response = cls.lex().put_intent(**args)

    @classmethod
    def checksum(cls, name):
        return cls.get_bot(name)["checksum"]

    @classmethod
    def build(cls, name, intents):
        args = {
            "name": name,
            "description": 'string',
            "idleSessionTTLInSeconds": 123,
            "processBehavior": 'BUILD',
            "locale": 'en-US',
            "childDirected": False,
            "clarificationPrompt": {
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': 'Sorry, did not get it'
                    }
                ],
                'maxAttempts': 3,

            },
            "voiceId": "Kendra",
            "abortStatement": {
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': 'Sorry, did not get it'
                    }
                ]
            },
            "intents": [{"intentName": i, "intentVersion": cls.get_intent(i)["version"]} for i in intents]
        }
        try:
            checksum = cls.checksum(name)
            args["checksum"] = checksum
        except ResourceNotFound:
            pass

        lex = cls.lex()
        response = lex.put_bot(**args)
        return response

    @classmethod
    def lex(cls):
        client = boto3.client('lex-models', region_name="eu-west-1")
        return client

    @classmethod
    def runlex(cls):
        client = boto3.client('lex-runtime', region_name="eu-west-1")
        return client

    @classmethod
    def send(cls, bot, input):
        return cls.runlex().post_text(
            botName=bot,
            botAlias="demo",
            userId="111",
            inputText=input
        )

    @classmethod
    def publish(cls, options):
        try:
            for i in options["intents"]:
                cls.add_intent(i)
            response = cls.build(options["name"])
            print pprint.pformat(response)
            return {
                "success": True,
                "data": json.dumps(response, default=json_serial)
            }
        except Exception, e:
            return {
                "success": False,
                "data": {
                    "error": e.message
                }
            }


if __name__ == "__main__":
    '''
    #Bot.add_slot_type("customer", ["customer", "individual", "client","user"])

    """
    Bot.add_intent({
        "name": "howmany",
        "description": "how many",
        "slots": [
            {"name": "slotzbgprgd", "slottype" : "customer"}
        ],
        "realisations": ["  what is the total number of {slotzbgprgd}"]
    })
    """
    
    Bot.add_intent({
        "name": "howmanyincity",
        "description": "how many in city",
        "slots": [
            {"name": "slotzbgprgd", "slottype": "customer"},
            {"name": "slottabcdef", "slottype": "cityval"}
        ],
        "realisations": ["  what is the total number of {slotzbgprgd} in {slottabcdef}"]
    })

    Bot.build(name = "salesbot",intents=["howmanyincity"])


    """
    i = {
        "name" : "whoisthebest",
        "description" : "question about me",
        "slots" : [
            {"name" : "acountry","values": ["france","uk"]}
        ],
        "realisations" : ["who is the best in {acountry}","who is the leader in {acountry}"]
    }
    options = {
        "name" : "mytestbot",
        "intents" : [i]
    }

    Bot.add_slot_type("myslot",["something really nice"])
    #print Bot.publish(options)
    """
    '''
    # print pprint.pformat(Bot.send("salesbot",u"what is the overall number of customer"))
