from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
from factory import  base_factory, list_children_factory
import pprint
from airbot.glue.crawler import Crawler


@App.field(
    field="crawl",
    path = "Query/crawl",
    argmap = {
        "/arguments/identity" : "identity",
        "/arguments/database" : "database",
        "/arguments/bucket":  "bucket",
        "/arguments/prefix":  "prefix"
    }
)
def parseS3Path(bucket, prefix, database,identity):
    return Crawler.crawl_bucket(
        database = database,
        bucket = bucket,
        prefix=prefix
    )

