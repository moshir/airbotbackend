from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory



#base_factory(objecttype="intent",parentobjecttype="bot",parentidentitifier="botid",identifier="intentid")
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
    input["doc"]={}
    print pprint.pformat(input)
    item = Item(**input)
    item.save()

    return item.json()



@App.field(
    field="getIntent",
    path ="Query/getIntent",
    argmap={
        "/arguments/intentid": "intentid",
        "/arguments/identity": "identity"
    }
)
def getIntent(identity, intentid) :
    print "%/"*30
    try:
        intent= Item.get("intent", intentid)
    except Exception:
        raise errors.ObjectNotFound(intentid)

    doc= intent.json()
    doc.update(doc["doc"])
    del doc["doc"]
    print doc
    return doc



@App.field(
    field="updateIntent",
    path ="Mutation/updateIntent",
    argmap={
        "/arguments/intentid": "intentid",
        "/arguments/identity": "identity",
        "/arguments/input" : "data"
    }
)
def updateIntent(identity, intentid, data) :
    try:
        v = Item.get("intent",intentid)
    except Exception as e :
        raise errors.ObjectNotFound(intentid)


    v.update(actions=[
        Item.doc.reply.set(data.get("reply",v.doc.reply)),
        Item.doc.sql.set(data.get("sql",v.doc.sql)),
        Item.description.set(data.get("description", v.description))
    ])
    d = v.json()
    d.update(d["doc"])
    del d["doc"]
    return d


@App.field(
    field="deleteIntent",
    path="Mutation/deleteIntent",
    argmap={
        "/arguments/intentid": "intentid",
        "/arguments/identity": "identity"
    }
)
def deleteIntent(identity, intentid):
    try:
        intent= Item.get("intent", intentid)
        intent.delete()
        rules = Item.parent_index.query(intentid)
        for r in rules :
            r.delete()
        return True
    except Exception:
        return False

    return False


if __name__ =="__main__" :
    print pprint.pformat(getIntent(intentid="uri:intent:demo:mybot:q", identity=""))
    from grapher.json_utils import to_json

    print pprint.pformat(to_json(App.route({
        "field" : "getIntent",
        "arguments": {
            "intentid" : "uri:intent:demo:mybot:q",
            "identity" : "xxx"
        }
    })))

