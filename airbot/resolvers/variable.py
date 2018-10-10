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
from airbot.logger import logger
import types


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

    print "?",variable.doc.type
    variable_doc = variable.json()
    print ">>",variable_doc
    variable_doc.update(variable_doc["doc"])
    del variable_doc["doc"]
    return variable_doc




def scale(min, max):
    min = 0
    for i in range(1,9):
        if min>pow(10, i) :
            min = pow(10,i-1)
    interval = (float(max)-float(min))
    step = interval/10.0
    top = min
    scale=[top]
    return [ int(min+i*step) for i in range(0,11)]

def syncVariableValues(variableid):
    variable = Item.get("variable", variableid)
    valueiterator = Item.query("value", Item.parent==variableid)
    with Item.batch_write() as batch :
        for v in valueiterator:
            batch.delete(v)

    entity = Item.get("entity", variable.parent)
    bot  = Item.get("bot", entity.parent)
    database = bot.doc.database
    tablename=entity.doc.tablename
    column = variable.doc.field


    if variable.doc.type.lower()=="dimension":
        sql = 'select distinct "%(column)s" from "%(database)s"."%(tablename)s" '%vars()
        response = AthenaQuery.run(**{"sql": sql})
        #logger().info("Athena returned %s", pprint.pformat(response))
        values = [r[column].replace('"','') for r in response["data"]["records"]]
    elif variable.doc.type.lower()=="metric" :
        sql = 'select max( "%(column)s") as mx, min("%(column)s") as mn from "%(database)s"."%(tablename)s" '%vars()
        response = AthenaQuery.run(**{"sql": sql})
        r = response["data"]["records"][0]
        M= r["mx"]
        m = r["mn"]
        print m,M
        values = scale(m,M)

    print ">>",values
    with Item.batch_write() as batch :

        for i,val in enumerate(values):
            if type(val)==types.IntType:
                val  = unicode(val)
            if len(val):
                slug = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
                cache = Item(**{
                    "name" : slug,
                    "parent" : variableid,
                    "doc": {},
                    "createdat" : ID.now(),"objecttype" : "value","ID" : variableid+":"+str(i),"search" : slug})
                batch.save(cache)
    return


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
        "field" : options["field"],
        "type" : options.get("type","dimension"),
        "aliases" : options["aliases"]
    }
    item = Item(**data)
    item.save()

    syncVariableValues(variableid=uri)
    d = item.json()
    d.update(d["doc"])
    del d["doc"]
    return d

    '''

    logger().info("Saving values of variable %s", data["ID"])
    database = bot.doc.database
    tablename = entity.doc.tablename
    columnname = options["field"]


    sql = 'select "%(columnname)s"   from "%(database)s"."%(tablename)s" group by "%(columnname)s"  limit 30'%vars()
    logger().info("Running query %s", sql)
    response = AthenaQuery.run(**{"sql": sql})
    logger().info("Athena returned %s", pprint.pformat(response))
    values = [r[columnname].replace('"','') for r in response["data"]["records"]]
    logger().info("Saving values")
    for i,val in enumerate(values):
        if len(val):
            slug = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
            cache = Item(**{
                "name" : slug,
                "parent" : uri,
                "doc": {},
                "createdat" : ID.now(),"objecttype" : "value","ID" : uri+":"+str(i),"search" : slug})
            print cache
            cache.save()

    logger().info("Saved values")
    d = item.json()
    d.update(d["doc"])
    del d["doc"]
    return d
    '''

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
        Item.doc.type.set(data.get("type",v.doc.type)),
        Item.description.set(data.get("description", v.description))
    ])
    d = v.json()
    d.update(d["doc"])
    del d["doc"]
    syncVariableValues(variableid=variableid)
    return d

def get_sample_values(uri):
    values = Item.query("value",Item.parent==uri,limit=100)
    cache=[]
    for v in values :
        if v.name.lower() not in cache:
            cache.append(v.name.lower())
            yield v.name.lower()


@App.field(
    field="getVariableValues",
    path="Variable/values",
    argmap={
        "/arguments/variableid":"variableid",
        "/source/ID" : "variableid",
        "identity" : "identity"
    }
)
def getVariableValues(variableid, identity) :
    try :
        variable = Item.get("variable", variableid)
        print variable
    except Exception as e :
        raise errors.ObjectNotFound(variableid)

    if variable.doc.type.lower()=="dimension" :
        values  = []
        valueiterator =  Item.query("value",Item.parent==variableid,limit=100)
        for v in valueiterator :
            if v.name not in values:
                values.append(v.name)
        return values
    else :
        return [10,100,1000,5000, 10000]


if __name__ == "__main__" :
    syncVariableValues(variableid="uri:variable:demo:salesbot:sales:revenue")

    exit()
    print getVariableValues(variableid="uri:variable:demo:salesbot:sales:country", identity="xxx")



    updateVariable("",variableid="uri:variable:demo:salesbot:sales:country", data={
        "field" : "retailer country"
    })

