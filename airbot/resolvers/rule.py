from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory







@App.field(
    field="deleteRule",
    path="Mutation/deleteRule",
    argmap={
        "/arguments/ruleid": "ruleid",
        "/arguments/identity": "identity"
    }
)
def deleteRule(identity, ruleid):
    try:
        v= Item.get("rule", ruleid)
        v.delete()
        return True
    except Exception:
        return False
    return False


@App.field(
    field="getRule",
    path ="Query/getRule",
    argmap={
        "/arguments/ruleid": "ruleid",
        "/arguments/identity": "identity"
    }
)
def getRule(identity, ruleid) :
    try:
        rule = Item.get("rule", ruleid)
    except Exception:
        raise errors.ObjectNotFound(ruleid)

    rule_doc = rule.json()
    rule_doc.update(rule_doc["doc"])
    del rule_doc["doc"]
    return rule_doc


@App.field(
    "createRule",
    path="Mutation/createRule",
    argmap={
        "/arguments/identity" : "identity",
        "/arguments/intentid" : "parent",
        "/arguments/input" : "options"
    }
)
def createRule(parent,options, identity):
    print ">", parent, options, identity
    try :
        intent = Item.get("intent",parent)
    except Exception:
        raise errors.ObjectNotFound(parent)


    bot = Item.get("bot",intent.parent)

    accountid = parent.split(":")[2]
    botname = parent.split(":")[3]
    intentname = parent.split(":")[4]
    name = options["name"]
    uri = "uri:rule:%(accountid)s:%(botname)s:%(intentname)s:%(name)s" % vars()
    print uri
    data={}
    data["ID"] = uri
    data["name"] = options["name"]
    data["objecttype"] = "rule"
    data["parent"] = parent if parent is not None else "service"
    data["search"] = name + options.get("description", "-") + options.get("tags", "-")
    data["createdat"] = ID.now()
    data["creator"] = identity
    data["doc"] = {
        "replacements" : options["replacements"]
    }
    item = Item(**data)
    item.save()
    d = item.json()
    d.update(d["doc"])
    del d["doc"]
    return d



@App.field(
    field="updateRule",
    path ="Mutation/updateRule",
    argmap={
        "/arguments/ruleid": "ruleid",
        "/arguments/identity": "identity",
        "/arguments/input" : "data"
    }
)
def updateRule(identity, ruleid, data) :

    try:
        v = Item.get("rule",ruleid)
    except Exception as e :
        raise errors.ObjectNotFound(ruleid)


    v.update(actions=[
        Item.doc.replacements.set(data.get("replacements",v.doc.replacements)),
        Item.description.set(data.get("description", v.description))
    ])
    d = v.json()
    d.update(d["doc"])
    del d["doc"]
    return d
