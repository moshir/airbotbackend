from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

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

    search = UnicodeAttribute(default=0, range_key=True)
    objecttype= UnicodeAttribute(default=0, hash_key=True)

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

    parent = UnicodeAttribute(default=0, range_key=True)
    objecttype= UnicodeAttribute(default=0, hash_key=True)


class Item(Model):
    """
    A Bot
    """
    class Meta:
        table_name = "items"
        region = 'eu-west-1'

    objecttype= UnicodeAttribute(hash_key=True)
    objectid = UnicodeAttribute(range_key=True)
    parent = UnicodeAttribute()
    search = UnicodeAttribute()
    search_index = SearchIndex()
    parent_index = ParentIndex()


#print "creating table"
#Item.create_table(read_capacity_units=1, write_capacity_units=1)

bot = Item(objectid = "xxx", objecttype = "bot", search="xxxx",parent="-")
bot.save()



for item in Item.query("bot",Item.search.contains("x")) :
    print item


for item in Item.search_index.query("bot" , Item.search =="xxxx"):
    print item