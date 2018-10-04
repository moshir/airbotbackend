import types
import pprint
import json
from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
from factory import  base_factory, list_children_factory
from airbot.athena.query import AthenaQuery
import re
import tracery
from airbot.lex.bot import Bot
from airbot.logger import  logger
from variable import get_sample_values



class Airbot :
    """ slot patterns created in lex for entities, variable, variable operator and variable value"""
    patterns = [
        {
            "name": "entity",
            "regexp": r"(?P<entityname>@@\w+)",
            "extract": lambda match: match.group().replace("@@", "")
        },
        {
            "name": "variableop",
            "regexp": r"(?P<variableop>@\w+.op)",
            "extract": lambda match: match.group().replace("@", "").replace(".op", "op")
        },
        {
            "name": "variableval",
            "regexp": r"(?P<variableval>@\w+.val)",
            "extract": lambda match: match.group().replace("@", "").replace(".val", "val")
        },
        {
            "name": "variable",
            "regexp": r"(?P<variablename>@\w+)",
            "extract": lambda match: match.group().replace("@", "")
        }
    ]

    @staticmethod
    def to_lex(matchobj) :
        """ turns a matchobject and returns {name}. this is used to transform airbot annotations like
        - @@entity
        - @variable
        - @variable.val
        - @variable.op
        to valid  lex slots  {slot}
        """
        pattern = [p for p in patterns if p["regexp"]==matchobj.re.pattern][0]
        return "{"+pattern["extract"](matchobj)+"}"

    @staticmethod
    def to_tracery(matchobj) :
        """ turns a matchobject and returns #name# .
        This is used to transform airbot annotations like
        - @@entity
        - @variable
        - @variable.val
        - @variable.op
        to valid  tracery generators #slot#
        """
        pattern = [p for p in patterns if p["regexp"]==matchobj.re.pattern][0]
        return "#"+pattern["extract"](matchobj)+"#"

    @staticmethod
    def parse(expression, pattern,replacer) :
        """takes a string , finds matching occurences of the pattern and replace them using the provided replacer(match) method
        This is applied to trasnform an airbot rule to a valid lex or tracery expression
        """
        regex = [p["regexp"] for p in patterns if p["name"] == pattern][0]
        return re.sub(regex, replacer, expression)

    @staticmethod
    def to_grammar(expression, replacer=to_lex) :
        """ applies parse to expression by replacing all patterns in Lex.patterns"""
        if (type(expression)==types.ListType):
            return [to_grammar(expr,replacer) for expr in expression]
        intent = expression
        for pattern in patterns :
            key = pattern["name"]
            intent = parse(intent, key, replacer)
        return intent


    @staticmethod
    def get_intent_config(intent,graph,mode="lex"):
        grammar={
            "rules" : {},
            "slots" : {},
            "utterances": {}
        }
        for rule in graph["intents"][intent].keys() :
            grammar["rules"][rule] = []
            rules = graph["intents"][intent][rule]
            for expression in rules :
                grammar["rules"][rule].append(to_grammar(expression, to_tracery))
        for slot in graph["slots"].keys():
            grammar["slots"][slot] = graph["slots"][slot]["values"]
            if slot[-3:] == "val" and mode=="lex":
                grammar["slots"][slot] = graph["slots"][slot]["ref"]

        rules = grammar["rules"]
        rules.update(grammar["slots"])
        generator = tracery.Grammar(rules)
        for i in range(1,1000) :
            if len(grammar["utterances"])>300:
                break
            utterance = generator.flatten("#origin#")
            grammar["utterances"][hash(utterance)]=utterance.lstrip().replace(",","")
        used_slots= {}
        for utterance in grammar["utterances"].values() :
            for s in grammar["slots"].keys() :
                if s in utterance and s not in used_slots.keys():
                    used_slots[s] = graph["slots"][s]

        config = {
            "name": intent,
            "description": 'string',
            "slots" : [{
                "valueSelectionStrategy": 'ORIGINAL_VALUE',
                "name" : s,
                "slotType" : s,
                "enumerationValues": graph["slots"][s]["values"],
            } for s in used_slots.keys()],
            "sampleUtterances" :  grammar["utterances"].values(),
            "fulfillmentActivity": {
                'type': 'ReturnIntent'
            },

        }
        return config


patterns = [
    {
        "name" : "entity",
        "regexp" : r"(?P<entityname>@@\w+)",
        "extract" : lambda match : match.group().replace("@@","")
    },
     {
        "name" : "variableop",
        "regexp": r"(?P<variableop>@\w+.op)",
        "extract": lambda match: match.group().replace("@", "").replace(".op","op")
    },
    {
        "name" : "variableval",
        "regexp": r"(?P<variableval>@\w+.val)",
        "extract": lambda match: match.group().replace("@", "").replace(".val", "val")
    },
    {
        "name": "variable",
        "regexp": r"(?P<variablename>@\w+)",
        "extract": lambda match: match.group().replace("@", "")
    }
]

def to_lex(matchobj) :
    pattern = [p for p in patterns if p["regexp"]==matchobj.re.pattern][0]
    return "{"+pattern["extract"](matchobj)+"}"

def to_tracery(matchobj) :
    pattern = [p for p in patterns if p["regexp"]==matchobj.re.pattern][0]
    return "#"+pattern["extract"](matchobj)+"#"

def parse(expression, pattern,replacer) :
    regex = [p["regexp"] for p in patterns if p["name"] == pattern][0]
    return re.sub(regex, replacer, expression)


def to_grammar(expression, replacer=to_lex) :
    if (type(expression)==types.ListType):
        return [to_grammar(expr,replacer) for expr in expression]
    intent = expression
    for pattern in patterns :
        key = pattern["name"]
        intent = parse(intent, key, replacer)
    return intent


def get_intent_config(intent,graph,mode="lex"):
    grammar={
        "rules" : {},
        "slots" : {},
        "utterances": {}
    }
    for rule in graph["intents"][intent].keys() :
        grammar["rules"][rule] = []
        rules = graph["intents"][intent][rule]
        for expression in rules :
            grammar["rules"][rule].append(to_grammar(expression, to_tracery))
    for slot in graph["slots"].keys():
        grammar["slots"][slot] = graph["slots"][slot]["values"]
        if slot[-3:] == "val" and mode=="lex":
            grammar["slots"][slot] = graph["slots"][slot]["ref"]

    rules = grammar["rules"]
    rules.update(grammar["slots"])
    generator = tracery.Grammar(rules)
    for i in range(1,1000) :
        if len(grammar["utterances"])>300:
            break
        utterance = generator.flatten("#origin#")
        grammar["utterances"][hash(utterance)]=utterance.lstrip().replace(",","")
    used_slots= {}
    for utterance in grammar["utterances"].values() :
        for s in grammar["slots"].keys() :
            if s in utterance and s not in used_slots.keys():
                used_slots[s] = graph["slots"][s]

    config = {
        "name": intent,
        "description": 'string',
        "slots" : [{
            "valueSelectionStrategy": 'ORIGINAL_VALUE',
            "name" : s,
            "slotType" : s,
            "enumerationValues": graph["slots"][s]["values"],
        } for s in used_slots.keys()],
        "sampleUtterances" :  grammar["utterances"].values(),
        "fulfillmentActivity": {
            'type': 'ReturnIntent'
        },

    }
    return config



def sample_values(variableid):
    variable = Item.get("variable", variableid)
    columnname =  json.loads(variable.doc)["field"]
    entity = Item.get("entity", variable.parent)
    tablename = entity.name
    bot = Item.get("bot", entity.parent)
    doc = json.loads(bot.doc)
    database = doc["database"]
    sql = 'select %(columnname)s   from "%(database)s"."%(tablename)s" group by %(columnname)s limit 15'%vars()
    response = AthenaQuery.run(**{"sql": sql})
    return [r[columnname].replace('"','') for r in response["data"]["records"]]


def sample_values(variableid):
    return ["something","something else","anything"]

@App.field(
    "createOrUpdateLexBot",
    path = "Mutation/createOrUpdateLexBot",
    argmap = {
        "/arguments/identity" : "identity",
        "/arguments/botid" : "botid"
    }
)
def createOrUpdateLexBot(identity,botid):
    bot =Item.get("bot",botid)
    entities = Item.query("entity",Item.parent.__eq__(botid))
    botgraph  ={
        "slots" : {},
        "intents" : {}
    }
    for e in entities :
        botgraph["slots"][e.name]={
            "name" : e.name,
            "ref" : "{%(name)s}"%e.attribute_values,
            "values" : e.doc.aliases
        }
        variables = Item.query("variable",Item.parent.__eq__(e.ID))
        for v in variables :
            nameslot =v.name
            botgraph["slots"][nameslot]={
                "name" : nameslot ,
                "ref": "{%(name)s}" % v.attribute_values,
                "values" : v.doc.aliases#json.loads(v.doc)["aliases"]
            }
            opslot=v.name+"op"
            botgraph["slots"][opslot] = {
                "name" : opslot,
                "ref": "{%(name)sop}" % v.attribute_values,
                "values" : [
                    "in",
                    "outside",
                    "greater",
                    "equals",
                    "different",
                    "smaller",
                    "bigger",
                    "taller"
                ]
            }

            valslot=v.name+"val"
            botgraph["slots"][valslot] = {
                "name" : valslot,
                "ref": "{%(name)sval}" % v.attribute_values,
                "values" : list(get_sample_values(v.ID))#sample_values(v.ID)
            }

    intents = Item.query("intent",Item.parent.__eq__(botid))
    for  i in intents :
        botgraph["intents"][i.name]={}
        print " ",i
        rules = Item.query("rule",Item.parent.__eq__(i.ID))
        for r in rules :
            botgraph["intents"][i.name][r.name] = r.doc.replacements#json.loads(r.doc)["expressions"]

    logger().critical("Creating bot %s", botid)
    intents = []
    for intent in botgraph["intents"].keys():
        logger().critical("Adding Intent %s", intent)
        intent_config = get_intent_config(intent, botgraph,"lex")
        #print pprint.pformat(intent_config)
        intents.append(intent_config)
        #print pprint.pformat(intent_config)
        for slot in intent_config["slots"]:
            logger().critical("Adding Slot Type `%s`",slot["name"])
            print pprint.pformat(slot["enumerationValues"])
            Bot.add_slot_type(slot["name"], slot["enumerationValues"])

        Bot.add_intent(intent_config)

    logger().critical("Putting Bot %s", bot.name)
    Bot.build(bot.name, intents=[i["name"] for i in intents ])



    return botgraph


if __name__=="__main__" :
    #x = to_grammar("#nbof# people living in @city @city.val",to_lex)
    #print x

    #exit()
    graph= App.route({
        "field": "createOrUpdateLexBot",
        "arguments": {
            "botid": "uri:bot:demo:FinancialCoach"
        },
        "identity": {
            "claims": {
                "email": "moshir.mikael@gmail.com"
            }
        }
    })

    #print pprint.pformat(expand_intent("howmany",graph))