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
base_factory(objecttype="entity",parentobjecttype="bot",parentidentitifier="botid",identifier="entityid")
list_children_factory(parentobjecttype="entity", chilobjecttype="variable", childobjectpluralized="variables")
import time


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
    doc = json.loads(bot.doc)
    return S3Helpers.get_presigned_url(doc["bucket"],doc["prefix"]+"/"+entity.name+"/INPUT.txt")


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
    bot = Item.get("bot", entity.parent)
    doc = json.loads(bot.doc)
    error = True
    logger().info("     Querying ", )
    database = doc["database"]
    tablename = entity.name
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
    logger().info("Starting crawler ")
    entity = Item.get("entity",entityid)

    bot = Item.get("bot", entity.parent)
    doc = json.loads(bot.doc)
    database = doc["database"]
    tablename = entity.name

    name = Crawler.crawl_bucket(
        database = doc["database"],
        bucket = doc["bucket"],
        prefix = doc["prefix"]+"/"+entity.name
    )
    done = False
    nbtry = 10
    logger().info("Waiting crawler to complete")
    while not done :
        nbtry -=1
        if nbtry==0 :
            break
        time.sleep(5)
        crawler = Crawler.get(name=name)
        logger().info("    Crawler %s %s State = %s", database, tablename,crawler["State"])
        if crawler["State"] in ["SUCCESS","READY","STOPPING"]:
            done  =True
    if done is False :
        raise errors.GlueTableCreationError("%(database)s%(tablename)s"%vars())
    Crawler.delete(name=name)
    sql = 'select *  from "%(database)s"."%(tablename)s" limit 100;' % vars()
    logger().info("SQL = %s", sql)
    response = AthenaQuery.run(**{"sql": sql})
    return response["data"]["schema"]


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
    doc = json.loads(bot.doc)
    error = True
    logger().info("     Querying ", )
    database = doc["database"]
    tablename = entity.name
    sql = 'select *  from "%(database)s"."%(tablename)s" limit 100;' % vars()
    logger().info("SQL = %s",sql)
    response = AthenaQuery.run(**{"sql": sql})
    #response["data"]["schema"] = response["data"]["records"][0].keys()
    logger().info("Response = %s",pprint.pformat(response))
    return json.dumps(response["data"]["records"])



if __name__=="__main__" :
    #print preview("uri:entity:20180911183119:myfunkybot:mytestentity","")
    #print refreshSchema("uri:entity:20180911183119:myfunkybot:mytestentity","")
    print App.route({
    "field": "preview",
    "arguments": {
        "entityid": "uri:entity:20180911183119:thisnewbot:cities"
    },
    "identity": {
        "claims": {
            "email": "moshir.mikael@gmail.com"
        }
    }
})
