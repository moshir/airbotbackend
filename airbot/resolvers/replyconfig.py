from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory



def updateReply(identity, intentid, data) :
    print intentid, data
    try:
        v = Item.get("intent",intentid)
    except Exception as e :
        print e
        raise errors.ObjectNotFound(intentid)


    v.update(actions=[
        Item.doc.reply.set(data.get("reply",v.doc.reply)),
        Item.doc.sql.set(data.get("sql",v.doc.sql)),
        #Item.description.set(data.get("description", v.description))
    ])
    d = v.json()
    d.update(d["doc"])
    del d["doc"]
    return d





if __name__ =="__main__" :
    updateReply(intentid="uri:intent:demo:mybot:myintent", identity="", data={
        "sql" : "select count(*) from x ",
        "reply" : ["xxx"]
    })