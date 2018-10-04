import json
from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
from factory import  base_factory, list_children_factory
import pprint
from airbot.model.botitem  import Item
from datetime import datetime
base_factory(objecttype="bot",parentobjecttype="account",parentidentitifier="accountid",identifier="botid")
list_children_factory(parentobjecttype="bot", chilobjecttype="entity", childobjectpluralized="entities")
list_children_factory(parentobjecttype="bot", chilobjecttype="intent", childobjectpluralized="intents")
from lex import Bot
from airbot.athena.query import AthenaQuery


@App.field(
    field="getBotStatus",
    path="Query/getBotStatus",
    argmap={
        "/arguments/botid" : "botid",
        "/arguments/identity" : "identity"
    }
)
def getBotStatus(identity, botid) :
    try :
        bot = Item.get("bot", botid)
    except Exception as e :
        return "NOT READY"
    try :
        response = Bot.get_bot(bot.name)
        return response["status"]
    except Exception as e :
        return "NOT READY"

@App.field(
    field="createBot",
    path="Mutation/createBot",
    argmap={
        "/arguments/accountid" : "parent",
        "/arguments/identity" : "identity",
        "/arguments/input" : "options"
    }
)
def createBot(parent,identity,options) :
    accountid = parent.split(":")[2]
    name = options.get("name","unnamedbot"+datetime.now().strftime("%Y%m%D%H%M%S"))
    uri = "uri:bot:%(accountid)s:%(name)s" % vars()
    try :
        existing = Item.get("bot", uri)
        raise errors.DuplicateError(uri)
    except Exception :
        pass
    input= {}
    input["ID"] = uri
    input["objecttype"] = "bot"
    input["parent"] = parent
    input["name"] = options.get("name","untitled")
    input["description"] = options.get("description","no description available")
    input["search"] = input["name"]+"-"+input["description"]
    input["createdat"] = ID.now()
    input["creator"] = identity
    input["doc"] = {
        "bucket" : "airbot2018",
        "database" : "airbot"+input["name"],
        "status" : "NOTBUILT",
        "prefix" : input["name"]
    }
    item = Item(**input)
    item.save()
    bot = Item.get("bot", uri)
    return bot.attribute_values

def reverse_operator(operator):
    index = {
        "in" : "=",
        "outside":"!=",
        "greater":">=",
        "equals":"=",
        "different":"!=",
        "smaller":"<=",
        "bigger":">=",
        "taller":">="
    }
    return index.get(operator,"=")




def get_filters(slots,graph) :
    varmap = {}
    filters = []
    explains = []
    for s in slots :
        basename=s.replace("val","").replace("op", "")
        for entity in graph["bot"]["entities"].values() :
            for v in entity["variables"].values() :
                if v["name"] == basename :
                    if v["name"] not in varmap :
                        varmap[v["name"]] = {
                            "field" : v["field"],
                            "tablename" : entity["tablename"]
                        }
                    if "op" in s :
                        varmap[v["name"]] ["op"]= slots[s]
                        varmap[v["name"]] ["sqlop"]= reverse_operator(slots[s])
                    if "val" in s:
                        varmap[v["name"]] ["value"]= slots[s]

    for v in varmap.values() :
        filters.append(v["field"]+v["sqlop"]+"'"+v["value"]+"'")
        explains.append(v["op"]+" "+v["value"])
    return {
        "filters" : " and ".join(filters),
        "explained" : " and ".join(explains)
    }



@App.field(
    field = "askBot",
    path = "Query/askBot",
    argmap={
        "arguments/identity" : "identity",
        "arguments/botid" : "botid",
        "arguments/question" : "question"
    }
)
def askBot(identity, botid, question) :
    import random
    try :
        bot = Item.get("bot", botid)
    except Exception as e :
        return "Seems i do not exists anymore :("

    response= Bot.send(bot=bot.name,input=question)
    print response
    if response["dialogState"] :
        parts = botid.split(":")
        accountid=parts[2]
        botname = parts[3]
        intentname = response["intentName"]
        uri = "uri:intent:%(accountid)s:%(botname)s:%(intentname)s"%vars()
        intent = Item.get("intent", uri)
        database= bot.doc.database
        SQL = intent.doc.sql

        print "SQL )= ", SQL

        graph = {
            "bot" : {
                "entities": {}
            }
        }
        entities = list(Item.parent_index.query( "entity", Item.parent==intent.parent))
        print "??",entities
        variables = {}
        for e in entities :
            print ">>>>>>>>>>>>>>>>>>>",">"+e.name+"<"
            SQL = SQL.replace(e.name, '"'+database+'".'+'"'+e.doc.tablename+'"')
            graph["bot"]["entities"][e.name] ={
                "name" : e.name,
                "tablename" : '"'+database+'"' +'."'+ e.name+'"',
                "database" : database,
                "variables" : {

                }
            }
            for v in Item.parent_index.query("variable", Item.parent == e.ID):
                graph["bot"]["entities"][e.name]["variables"][v.name] = {
                    "name" : v.name,
                    "field" : v.doc.field
                }

        print pprint.pformat(graph)
        filters = get_filters(graph=graph, slots=response["slots"])["filters"]
        explains= get_filters(graph=graph, slots=response["slots"])["explained"]
        print "filters = ",filters
        print "explains  = ",explains


        sql = "select count(*) as NB from ("+SQL+" where "+filters+") as T"

        results = AthenaQuery.run(sql=sql)

        print "+-/"*30
        print results["data"]["records"][0]

        replytpl = random.choice(intent.doc.reply)
        reply = replytpl.replace("{NB}", results["data"]["records"][0]["NB"])+" "+explains
        return reply
    else :
        return random.choice([
            "Sorry, this is not clear for and old bot",
            "Can you try to reformulate ?",
            "Hmm, i'm just a bot",
            "Well, this is clear, i'm not really awake right now"
        ])



if __name__=="__main__" :


    print App.route(
        {
            "field" : "askBot",
            "arguments": {
                "botid":"uri:bot:demo:FinancialCoach",
                "question" : "how many people are living in paris"
            }
         }
    )

    r= askBot(identity="", botid="uri:bot:demo:FinancialCoach", question="how many people are living in paris")
    print pprint.pformat(r)

    exit()
    #print     Bot.put_alias("FinancialCoach")
    print     Bot.put_bot_version("FinancialCoach")

    exit()

    print getBotStatus(identity="", botid="uri:bot:demo:FinancialCoach")


    print askBot(identity="", botid="uri:bot:demo:FinancialCoach", question="number of persons")

    exit()
    '''
    from grapher.json_utils import to_json
    event = {
        "field" : "createBot",
        "path" : "Account/bots",
        "arguments" : {
            "identity" :"service",
            "accountid" : "uri:account:demo",
            "input" : {
                "name" : "mybot"
            }
        }

    }
    b = App.route(event)

    print to_json(b)

    '''


