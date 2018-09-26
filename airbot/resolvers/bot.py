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
    input["doc"] = json.dumps({
        "bucket" : "airbot2018",
        "database" : "airbot"+input["name"],
        "prefix" : input["name"]
    })
    item = Item(**input)
    item.save()
    bot = Item.get("bot", uri)
    return bot.attribute_values



if __name__=="__main__" :
    event = {
        "field" : "createBot",
        "path" : "Mutation/createBot",
        "arguments" : {
            "identity" :"service",
            "accountid": "uri:account:20180911183119",
            "input":{
                "name": "myfunkybot",
                "description": "generated from pycharm"
            }
        }
    }
    print App.route(event)




