from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
import base64
import json
import zlib
import md5
import itertools
from pynamodb.attributes import ListAttribute

def merge_doc(entity) :
    doc = entity.attribute_values
    if "doc" in doc.keys() :
        doc.update(doc["doc"].attribute_values)
        del doc["doc"]
    return doc



def encode(d):
    return json.dumps(d).encode("zlib_codec").encode("base64_codec").replace("\n","")

def decode(s) :
    return json.loads(s.decode('base64_codec').decode('zlib_codec'))



def encode_last_evaluated_keys(lek):
    #s = json.dumps(lek)
    #return base64.encodestring(json.dumps(lek)).replace("\n","")
    return encode(lek)

def decode_last_evaluated_key(token):
    if token is None :
        return None
    elif not len(token) :
        return None
    #return json.loads(base64.decodestring(token))
    return decode(token)


def apply_options(iterator, options) :
    if options is None :
        return iterator
    else:
        offset= options.get("offset",0)
        limit = options.get("limit",2000)
        return itertools.islice(iterator,offset, offset+limit)

def list_children_factory(parentobjecttype, chilobjecttype, childobjectpluralized) :
    P = parentobjecttype[0].upper()+"".join(parentobjecttype[1:])
    C = childobjectpluralized[0].upper()+"".join(childobjectpluralized[1:])
    @App.field(
        "list%(C)s"%vars(),
        path="%(P)s/%(childobjectpluralized)s"%vars(),
        argmap={
            "/source/ID" : "parent",
            "/arguments/identity": "identity",
            "/arguments/options": "options"
        }
    )
    def listmethod(parent, options, identity):
        print "listmethod <-", parent, options, identity
        prevtoken="null"
        if options is None :
            iterator = Item.parent_index.query(chilobjecttype, Item.parent == parent)
        else :
            limit=options.get("limit",5)
            #nexttoken=decode_last_evaluated_key(options.get("nexttoken")) if "nexttoken" in options.keys() else None
            #prevtoken=options.get("nexttoken","null")
            if "search" in options.keys():
                term = options.get("search",)
                iterator = Item.parent_index.query(chilobjecttype, Item.parent == parent & Item.search.contains(term))
            else:
                iterator = Item.parent_index.query(chilobjecttype, Item.parent == parent)

        #items=[i.attribute_values for i in apply_options(iterator, options)]
        items=[merge_doc(i) for i in apply_options(iterator, options)]
        return items


def base_factory(objecttype, parentobjecttype, parentidentitifier,identifier):
    capitalized = objecttype[0].upper()+"".join(objecttype[1:])

    @App.field(
        "create%(capitalized)s"%vars(),
        path  = "Mutation/create%(capitalized)s"%vars(),
        argmap= {
            "/arguments/input" : "input",
            "/arguments/%(parentidentitifier)s"%vars(): "parent",
            "/arguments/identity" : "identity"
        }
    )
    def create_item(parent, input, identity) :
        print "create %(objectype)s received", parent, input, identity
        try :
            name = input["name"]
        except Exception:
            raise errors.InvalidParameter("Missing `name` field in input"%vars())
        if parent is  None :
            parent = "service"
        else:
            try :
                parent_item =Item.get(parentobjecttype, parent)
            except Exception :
                raise errors.ObjectNotFound("No parent object with type `%(parentobjecttype)s` found with Id :`%(parent)s`"%vars())

        candidates = get_children_by_name(parent,objecttype=objecttype, name=input["name"])
        if len(candidates) :
            if parentobjecttype is None :
                parent = "accounts"
            raise errors.DuplicateError("An object with name `%(name)s`and type `%(objecttype)s` already exists in `%(parent)s`"%vars())

        objectid = ID.get()

        if objecttype == "account" :
            uri = "uri:account:%(objectid)s"%vars()


        if objecttype =="bot" :
            accountid = parent.split(":")[2]
            uri = "uri:bot:%(accountid)s:%(name)s" % vars()

        if objecttype =="entity" :
            accountid = parent.split(":")[2]
            botname = parent.split(":")[3]
            uri = "uri:entity:%(accountid)s:%(botname)s:%(name)s" % vars()

        if objecttype =="intent" :
            accountid = parent.split(":")[2]
            botname = parent.split(":")[3]
            uri = "uri:intent:%(accountid)s:%(botname)s:%(name)s" % vars()

        if objecttype =="reply" :
            accountid = parent.split(":")[2]
            botname = parent.split(":")[3]
            intentname = parent.split(":")[4]
            uri = "uri:reply:%(accountid)s:%(botname)s:%(intenname)s:(name)s" % vars()

        if objecttype =="variable" :
            accountid = parent.split(":")[2]
            botname= parent.split(":")[3]
            entityname= parent.split(":")[4]
            uri = "uri:variable:%(accountid)s:%(botname)s:%(entityname)s:%(name)s" % vars()

        if objecttype =="rule" :
            accountid = parent.split(":")[2]
            botname= parent.split(":")[3]
            intentname= parent.split(":")[4]
            uri = "uri:rule:%(accountid)s:%(botname)s:%(intentname)s:%(name)s" % vars()


        input["ID"]  = uri
        input["objecttype"] = objecttype
        input["parent"] = parent if parent is not None else "service"
        input["search"] = input.get("name")+input.get("description","-")+input.get("tags", "-")
        input["createdat"] = ID.now()
        input["creator"] = identity
        input["doc"] = input.get("doc") or '{"":""}'
        print pprint.pformat(input)
        item = Item(**input)
        item.save()
        return item.attribute_values


    def get_children_by_name(parent, objecttype, name) :
        print "get_children_by_name", parent, objecttype, name
        if objecttype =="account" :
            candidates = Item.query(hash_key=objecttype, filter_condition=Item.name.__eq__(name) )
        else :
            candidates = Item.query(hash_key=objecttype,filter_condition=Item.name.__eq__(name) & Item.parent.__eq__(parent))
        return [c.attribute_values for c in candidates]


    @App.field(
        "get%(capitalized)s"%vars(),
        path  = "Query/get%(capitalized)s"%vars(),
        argmap= {
            "/arguments/%(identifier)s"%vars() : "identifier",
            "/arguments/identity" : "identity"
        }
    )
    def get_item(identifier, identity) :
        try :
            bot = Item.get(objecttype, identifier)
            return bot.attribute_values
        except Exception:
            raise errors.ObjectNotFound(identifier)


    @App.field(
        "update%(capitalized)s"%vars(),
        path  = "Mutation/update%(capitalized)s"%vars(),
        argmap= {
            "/arguments/input" : "input",
            "/arguments/%(identifier)s"%vars() : "identifier",
            "/arguments/identity" : "identity"
        }
    )
    def update_item(identifier,input, identity) :
        print "update_item <-", identifier, input, identity
        try :
            item = Item.get(objecttype,identifier)
            doc = item.attribute_values
        except Exception :
            raise errors.ObjectNotFound("Could not find %(objecttype)s with ID `%(botid)s`"%vars())

        actions = []
        for k in input.keys() :
            attribute = getattr(Item, k)
            print "attribute = ", attribute
            actions.append(attribute.set(input[k]))
        term = doc["name"]+input.get("description", doc.get("description","-"))+input.get("tags", doc.get("tags","-"))
        actions.append(Item.search.set(term))
        print actions
        item.update(actions=actions)
        return item.attribute_values



    @App.field(
        "delete%(capitalized)s"%vars(),
        path  = "Mutation/delete%(capitalized)s"%vars(),
        argmap= {
            "/arguments/%(identifier)s"%vars() : "identifier",
            "/arguments/identity" : "identity"
        }
    )
    def delete_item(identifier, identity) :
        try :
            bot = Item.get(objecttype,identifier)
        except Exception :
            raise errors.ObjectNotFound("Could not find %(objecttype)s with ID `%(botid)s`"%vars())


        bot.delete()
        return True





if __name__=="__main__" :
    b = encode_last_evaluated_keys({"x" : 2})
    print ">",b,"<"
    print decode_last_evaluated_key(b)




