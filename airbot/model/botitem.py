from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute,ListAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
import base64
import json


class Base(Model) :
    def json(self):
        return {
            "name" : self.name,
            "description" : self.description,
            "objecttype": self.objecttype,
            "ID" : self.ID,
            "doc" : {
                "aliases":list(self.doc.aliases),
                "replacements":list(self.doc.replacements),
                "status" : self.doc.status,
                "columns": list([{"Name" : c.Name ,"Type" : c.Type} for c in self.doc.columns]),
                "bucket" : self.doc.bucket,
                "database" : self.doc.database,
                "tablebname": self.doc.tablename,
                "field": self.doc.field,
                "prefix": self.doc.prefix,
                "crawler" : self.doc.crawler,
                "sql" : self.doc.sql,
                "reply" : list(self.doc.reply)
            },
            "parent" : self.parent,
            "search" :self.search,
            "tags" : self.tags,
            "creator" : self.creator,
            "createdat" : self.createdat,
            "updateat" : self.updateat,
        }

class Column(MapAttribute) :
    Name = UnicodeAttribute(attr_name="Name")
    Type= UnicodeAttribute(attr_name="Type")



class Doc(MapAttribute):
    aliases = ListAttribute(attr_name="aliases", default=[])
    status = UnicodeAttribute(attr_name="status", default="ready")
    columns = ListAttribute(attr_name="columns", of=Column,default=[])
    bucket = UnicodeAttribute(attr_name="bucket", default="")
    database = UnicodeAttribute(attr_name="database", default="")
    tablename= UnicodeAttribute(attr_name="tablename", default="")
    field= UnicodeAttribute(attr_name="field", default="")
    crawler= UnicodeAttribute(attr_name="crawler", default="")
    prefix=UnicodeAttribute(attr_name="prefix", default="")
    replacements=ListAttribute(attr_name="replacements", default=[])
    sql=UnicodeAttribute(attr_name="sql", default="")
    reply =ListAttribute(attr_name="reply", default=[])





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

class Item(Base):
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
    #doc = UnicodeAttribute(default='{"doc" : "empty"}')
    doc = Doc()
    creator = UnicodeAttribute(default='unknown')
    createdat = UnicodeAttribute()
    updateat= UnicodeAttribute(default="-")
    resource_status=UnicodeAttribute(default="-")

    search_index = SearchIndex()
    parent_index = ParentIndex()
    name_index = NameIndex()

