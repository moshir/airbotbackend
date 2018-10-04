from argparse import Namespace
import json
import pprint
from airbot.model.botitem  import Item
from  airbot.s3.helpers import S3Helpers
from airbot.glue.crawler import Crawler
from grapher import App
from genid import ID
from airbot import errors
from factory import base_factory, list_children_factory
from datetime import datetime
from airbot.athena.query import AthenaQuery
from airbot.logger import logger
#base_factory(objecttype="entity",parentobjecttype="bot",parentidentitifier="botid",identifier="entityid")
list_children_factory(parentobjecttype="entity", chilobjecttype="variable", childobjectpluralized="variables")
import time
from pynamodb.attributes import MapAttribute


class ENTITYSTATES :
    NOT_READY = "NOTREADY"
    READY = "READY"
    PARSING = "PARSING"
    FAILED = "FAILED"




@App.field(
    field="deleteEntity",
    path="Mutation/deleteEntity",
    argmap={
        "/arguments/entityid": "entityid",
        "/arguments/identity": "identity"
    }
)
def deleteEntity(identity, entityid):
    try:
        e= Item.get("entity", entityid)
        e.delete()
        vars = Item.parent_index.query(entityid)
        for r in vars :
            r.delete()
        return True
    except Exception as e:
        print e
        return False


@App.field(
    field="createEntity",
    path ="Mutation/createEntity",
    argmap={
        "/arguments/botid": "botid",
        "/arguments/identity": "identity",
        "/arguments/input" : "data"
    }
)
def createEntity(identity, botid, data) :

    try:
        bot = Item.get("bot",botid)
    except Exception as e :
        raise errors.ObjectNotFound(botid)

    print ">>",data
    parts = botid.split(":")
    accountid=parts[2]
    botname=parts[3]
    entityname=data["name"]
    uri= "uri:entity:%(accountid)s:%(botname)s:%(entityname)s"%vars()
    entity = Item(
        parent = botid,
        ID=uri,
        createdat = ID.now(),
        name = data["name"],
        description  = data.get("description","-"),
        search = data["name"]+data.get("description","-"),
        objecttype="entity",
        doc = {
            "aliases" : data["aliases"],
            "status" : ENTITYSTATES.NOT_READY,
            "database" : bot.doc.database,
            "tablename" : data["name"]
        }
    )

    print entity

    entity.save()
    return entity.attribute_values





@App.field(
    field="updateEntity",
    path ="Mutation/updateEntity",
    argmap={
        "/arguments/entityid": "entityid",
        "/arguments/identity": "identity",
        "/arguments/input" : "data"
    }
)
def updateEntity(identity, entityid, data) :

    try:
        entity = Item.get("entity",entityid)
    except Exception as e :
        raise errors.ObjectNotFound(entityid)


    entity.update(actions=[
        Item.doc.aliases.set(data.get("aliases",entity.doc.aliases)),
        Item.description.set(data.get("description", entity.description))
    ])
    return entity.attribute_values


@App.field(
    field="getEntity",
    path ="Query/getEntity",
    argmap={
        "/arguments/entityid": "entityid",
        "/arguments/identity": "identity"
    }
)
def getEntity(identity, entityid) :
    try:
        entity = Item.get("entity", entityid)
        bot = Item.get("bot",entity.parent)
    except Exception:
        raise errors.ObjectNotFound(entityid)

    print ENTITYSTATES.PARSING, ">>",entity.doc.status, ENTITYSTATES.PARSING==entity.doc.status
    if entity.doc.status==ENTITYSTATES.PARSING:
        logger().info("entity is parsing")
        if len(entity.doc.crawler) :
            crawler_name = entity.doc.crawler
            crawler = Crawler.get(name=crawler_name)
            if crawler["State"] in ["READY","STOPPING"]:
                doc = bot.doc
                database=doc.database
                tablename = entity.doc.tablename
                columns = Crawler.get_table(database,tablename)
                print "columns", columns
                entity.update(actions=[Item.doc.columns.set(columns),Item.doc.status.set(ENTITYSTATES.READY)])
    entity_doc = entity.json()
    print "entity_doc ", pprint.pformat(entity_doc)
    entity_doc.update(entity_doc["doc"])
    del entity_doc["doc"]
    return entity_doc

@App.field(
    field = "getPresignedUrl",
    path="Query/uploadUrl",
    argmap ={
        "/arguments/entityid":  "entityid",
        "/arguments/identity" : "identity"
    }
)
def get_presigned_url(entityid,identity) :
    entity = Item.get("entity",entityid)
    bot = Item.get("bot", entity.parent)
    doc = bot.doc
    return S3Helpers.get_presigned_url(doc.bucket,doc.prefix+"/"+entity.name+"/INPUT.txt")


@App.field(
    field = "preview",
    path="Entity/preview",
    argmap ={
        "/source/entityid":  "entityid",
        "/arguments/identity" : "identity"
    }
)
def preview(entityid,identity) :
    logger().info("Preview of %s", entityid)
    entity = Item.get("entity",entityid)
    if entity.doc.status != ENTITYSTATES.READY:
        raise errors.FileStatusError("File has not been parsed")

    bot = Item.get("bot", entity.parent)
    doc = bot.doc
    error = True
    logger().info("     Querying ", )
    database = doc.database
    tablename = entity.doc.tablename
    sql = 'select *  from "%(database)s"."%(tablename)s" limit 100;' % vars()
    logger().info("SQL = %s",sql)
    response = AthenaQuery.run(**{"sql": sql})
    logger().info("Response = %s,",pprint.pformat(response))
    return response


@App.field(
    field = "schema",
    path="Mutation/refreshEntitySchema",
    argmap ={
        "/arguments/entityid":  "entityid",
        "/arguments/identity" : "identity"
    }
)
def refreshSchema(entityid,identity) :
    entity = Item.get("entity",entityid)
    print "??",entity.doc.attribute_values
    print "==>",entity.doc.status
    if entity.doc.status==ENTITYSTATES.PARSING:
        return False
    logger().info("Creating  crawler ")
    bot = Item.get("bot", entity.parent)
    doc = bot.doc
    database = doc["database"]
    tablename = entity.name

    name = Crawler.crawl_bucket(
        database = doc["database"],
        bucket = doc["bucket"],
        prefix = doc["prefix"]+"/"+entity.name
    )
    done = False
    nbtry = 10
    entity.update(actions=[Item.doc.status.set(ENTITYSTATES.PARSING),Item.doc.crawler.set(name)])
    return True

@App.field(
    field = "preview",
    path="Query/previewEntity",
    argmap ={
        "/arguments/entityid":  "entityid",
        "/arguments/identity" : "identity"
    }
)
def preview(entityid,identity) :
    logger().info("Preview of %s", entityid)
    entity = Item.get("entity",entityid)
    bot = Item.get("bot", entity.parent)
    doc = bot.doc
    error = True
    logger().info("     Querying ", )
    database = doc.database
    tablename = entity.doc.tablename
    sql = 'select *  from "%(database)s"."%(tablename)s" limit 100;' % vars()
    logger().info("SQL = %s",sql)
    response = AthenaQuery.run(**{"sql": sql})
    #response["data"]["schema"] = response["data"]["records"][0].keys()
    logger().info("Response = %s",pprint.pformat(response))
    return json.dumps(response["data"]["records"])



if __name__=="__main__" :
    from grapher.json_utils import to_json
    print to_json(deleteEntity(entityid="uri:entity:demo:mybot:thisfile", identity=""))