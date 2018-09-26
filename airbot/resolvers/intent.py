from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory



base_factory(objecttype="intent",parentobjecttype="bot",parentidentitifier="botid",identifier="intentid")
list_children_factory(parentobjecttype="intent", chilobjecttype="rule", childobjectpluralized="rules")


@App.field(
    "createIntent",
    path  = "Mutation/createIntent",
    argmap ={
        "/arguments/botid":  "botid",
        "/arguments/input" : "input",
        "/arguments/identity" : "identity"
    }
)
def create_intent(botid, input, identity):
    name = input["name"]
    print "create received", botid, input, identity
    accountid = botid.split(":")[2]
    botname = botid.split(":")[3]
    uri = "uri:intent:%(accountid)s:%(botname)s:%(name)s" % vars()
    objectid = ID.get()
    input["ID"] = uri
    input["objecttype"] = "intent"
    input["createdat"] = ID.now()
    input["creator"] = identity
    input["parent"] = botid
    input["search"] = input.get("name") + input.get("description", "-") + input.get("tags", "-")
    print pprint.pformat(input)
    item = Item(**input)
    item.save()


    reply_input= {}
    reply_input["objecttype"] = "reply"
    reply_input["ID"] = uri
    reply_input["creator"] = identity
    reply_input["createdat"] =ID.now()
    reply_input["parent"] = uri
    reply_input["name"] = "reply"
    reply_input["search"] = "-"
    reply = Item(**reply_input)
    reply.save()

    return item.attribute_values


@App.field(
    "getReplyConfig",
    path  = "Intent/reply",
    argmap ={
        #"/arguments/intentid":  "intentid",
        "/source/ID" : "intentid",
        "/arguments/identity" : "identity"
    }
)
def get_reply_config(intentid, identity):
    try :
        reply = Item.get("reply", intentid)
        return reply.attribute_values
    except Exception :
        raise errors.ObjectNotFound("Reply %(intentid)s"%vars())


if __name__ =="__main__" :
    print App.route({
        "field": "getReplyConfig",
        "source" : {
            "ID" : "uri:intent:20180911183119:thisnewbot:howmany"
        },
        "identity": {
            "claims": {
                "email": "moshir.mikael@gmail.com"
            }
        }
    })