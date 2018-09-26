from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
import base64
import json

class SearchIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = 'search-index'
        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    search = UnicodeAttribute( range_key=True)
    objecttype= UnicodeAttribute( hash_key=True)

class ParentIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = 'parent-index'
        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    parent = UnicodeAttribute(range_key=True)
    objecttype= UnicodeAttribute( hash_key=True)


class NameIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = 'name-index'
        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    name = UnicodeAttribute(range_key=True)
    objecttype= UnicodeAttribute(hash_key=True)

class Item(Model):
    """
    A Bot Resource
    """
    class Meta:
        table_name = "airtbotdb"
        region = 'eu-west-1'
        read_capacity_units = 2
        write_capacity_units = 1

    objecttype= UnicodeAttribute(hash_key=True)
    ID = UnicodeAttribute(range_key=True)
    parent = UnicodeAttribute()
    name= UnicodeAttribute()
    search = UnicodeAttribute()
    description= UnicodeAttribute(default="-")
    tags = UnicodeAttribute(default="-")
    doc = UnicodeAttribute(default='{"doc" : "empty"}')
    creator = UnicodeAttribute(default='unknown')
    createdat = UnicodeAttribute()
    updateat= UnicodeAttribute(default="-")

    search_index = SearchIndex()
    parent_index = ParentIndex()
    name_index = NameIndex()


#Item.delete_table()
#Item.create_table()

'''
bots = Item.parent_index.query("bot",Item.parent.__eq__("uri:account:20180911183119"),limit=2,last_evaluated_key=None)
for bot in  bots :
    print "page1",bot

#print bots.last_evaluated_key
#k =base64.encodestring(json.dumps(bots.last_evaluated_key))
#print json.loads(base64.decodestring(k))
page2 = Item.parent_index.query("bot",Item.parent.__eq__("uri:account:20180911183119"), last_evaluated_key=bots.last_evaluated_key)
for bot in  page2:
    print "page2",bot

print page2.last_evaluated_key
'''