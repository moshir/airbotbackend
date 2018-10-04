import unicodedata
from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory
from airbot import errors
import json
from genid import ID
base_factory(objecttype="variable",parentobjecttype="entity",parentidentitifier="entityid",identifier="variableid")
from unidecode import unidecode
from airbot.athena.query import AthenaQuery
from entity import ENTITYSTATES





@App.field(
    field="deleteVariable",
    path="Mutation/deleteVariable",
    argmap={
        "/arguments/variableid": "variableid",
        "/arguments/identity": "identity"
    }
)
def deleteVariable(identity, variableid):
    try:
        v= Item.get("variable", variableid)
        v.delete()
        return True
    except Exception:
        return False

@App.field(
    field="getVariable",
    path ="Query/getVariable",
    argmap={
        "/arguments/variableid": "variableid",
        "/arguments/identity": "identity"
    }
)
def getVariable(identity, variableid) :
    try:
        variable = Item.get("variable", variableid)
        entity = Item.get("entity",variable.parent)
    except Exception:
        raise errors.ObjectNotFound(variableid)

    variable_doc = variable.json()
    variable_doc.update(variable_doc["doc"])
    del variable_doc["doc"]
    return variable_doc


@App.field(
    "createVariable",
    path="Mutation/createVariable",
    argmap={
        "/arguments/identity" : "identity",
        "/arguments/entityid" : "parent",
        "/arguments/input" : "options"
    }
)
def createVariable(parent,options, identity):
    print ">", parent, options, identity
    try :
        entity = Item.get("entity",parent)
    except Exception:
        raise errors.ObjectNotFound(parent)


    if entity.doc.status!=ENTITYSTATES.READY :
        raise errors.InvalidParameter("Could not add variable to unparsed entity")
    bot = Item.get("bot",entity.parent)

    accountid = parent.split(":")[2]
    botname = parent.split(":")[3]
    entityname = parent.split(":")[4]
    name = options["name"]
    uri = "uri:variable:%(accountid)s:%(botname)s:%(entityname)s:%(name)s" % vars()
    print uri
    data={}
    data["ID"] = uri
    data["name"] = options["name"]
    data["objecttype"] = "variable"
    data["parent"] = parent if parent is not None else "service"
    data["search"] = name + options.get("description", "-") + options.get("tags", "-")
    data["createdat"] = ID.now()
    data["creator"] = identity
    data["doc"] = {
        "aliases" : options["aliases"],
        "field" : options["field"]
    }
    item = Item(**data)
    item.save()

    database = bot.doc.database
    tablename = entity.doc.tablename
    columnname = options["field"]


    sql = 'select %(columnname)s   from "%(database)s"."%(tablename)s" group by %(columnname)s  limit 30'%vars()
    response = AthenaQuery.run(**{"sql": sql})
    values = [r[columnname].replace('"','') for r in response["data"]["records"]]
    for i,val in enumerate(values):
        if len(val):
            slug = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
            cache = Item(**{"name" : slug,"parent" : uri,"doc": {},"createdat" : ID.now(),"objecttype" : "value","ID" : uri+":"+str(i),"search" : slug})
            print cache
            cache.save()

    d = item.json()
    d.update(d["doc"])
    del d["doc"]
    return d


def get_sample_values(uri):
    values = Item.query("value",Item.parent==uri,limit=100)
    cache=[]
    for v in values :
        if v.name.lower() not in cache:
            cache.append(v.name.lower())
            yield v.name.lower()



@App.field(
    field="updateVariable",
    path ="Mutation/updateVariable",
    argmap={
        "/arguments/variableid": "variableid",
        "/arguments/identity": "identity",
        "/arguments/input" : "data"
    }
)
def updateVariable(identity, variableid, data) :

    try:
        v = Item.get("variable",variableid)
    except Exception as e :
        raise errors.ObjectNotFound(variableid)


    v.update(actions=[
        Item.doc.aliases.set(data.get("aliases",v.doc.aliases)),
        Item.doc.field.set(data.get("field",v.doc.field)),
        Item.description.set(data.get("description", v.description))
    ])
    d = v.json()
    d.update(d["doc"])
    del d["doc"]
    return d


if __name__ == "__main__" :




    for v in get_sample_values("uri:variable:demo:mybot:thisfile:x") :
        print v