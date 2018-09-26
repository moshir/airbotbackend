import pprint
import boto3
import errors
from boto3.dynamodb.conditions import Key,Attr
from datetime import datetime

class TableModel:
    @classmethod
    def factory(base , tablename,idfield, entityname):
        class X :
            @classmethod
            def strnow(cls):
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            @classmethod
            def table(cls):
                return cls.db().Table(cls.tablename)

            @classmethod
            def db(cls):
                try :
                    return cls._db
                except AttributeError :
                    X._db =  boto3.resource('dynamodb', region_name='eu-west-1')
                    return cls._db

            @classmethod
            def table_exists(cls):
                try:
                    T = cls.table()
                    c= T.item_count
                    return True
                except Exception,e:
                    return False

            @classmethod
            def delete_table(cls):
                if cls.table_exists():
                    print "Deleting table `%(tablename)s`"%cls.__dict__
                    cls.table().delete()
                    cls.table().meta.client.get_waiter('table_not_exists').wait(TableName=cls.tablename)

            @classmethod
            def create_table(cls):
                if not cls.table_exists():
                    print "Creating table `%(tablename)s`" % cls.__dict__
                    table = cls.db().create_table(
                        TableName=cls.tablename,
                        KeySchema=[
                            {
                                "AttributeName" : "accountid",
                                "KeyType" : "HASH"
                            },
                            {
                                'AttributeName': idfield,
                                'KeyType': 'RANGE'
                            }
                        ],
                        AttributeDefinitions=[
                            {
                                'AttributeName': "accountid",
                                'AttributeType': 'S'
                            },
                            {
                                'AttributeName': idfield,
                                'AttributeType': 'S'
                            },
                            {
                                'AttributeName': "parent",
                                'AttributeType': 'S'
                            },
                            {
                                'AttributeName': "name",
                                'AttributeType': 'S'
                            },
                            {
                                'AttributeName': "search",
                                'AttributeType': 'S'
                            }
                        ],
                        ProvisionedThroughput={
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        },
                        GlobalSecondaryIndexes = [
                            {
                                'IndexName': 'name-index',
                                "KeySchema": [
                                    {
                                        "AttributeName" : "accountid",
                                        "KeyType" : "HASH",
                                    },
                                    {
                                        'AttributeName': 'name',
                                        'KeyType': 'RANGE'
                                    }
                                ],
                                'Projection': {
                                    'ProjectionType': 'ALL'
                                },
                                "ProvisionedThroughput": {
                                    'ReadCapacityUnits': 5,
                                    'WriteCapacityUnits': 5
                                }

                            },
                            {
                                'IndexName': 'parent-index',
                                "KeySchema": [
                                    {
                                        "AttributeName": "accountid",
                                        "KeyType": "HASH",
                                    },
                                    {
                                        'AttributeName': 'parent',
                                        'KeyType': 'RANGE'
                                    }
                                ],
                                'Projection': {
                                    'ProjectionType': 'ALL'
                                },
                                "ProvisionedThroughput": {
                                    'ReadCapacityUnits': 5,
                                    'WriteCapacityUnits': 5
                                }
                            },
                            {
                                'IndexName': 'search-index',
                                "KeySchema": [
                                    {
                                        "AttributeName": "accountid",
                                        "KeyType": "HASH",
                                    },
                                    {
                                        'AttributeName': 'search',
                                        'KeyType': 'RANGE'
                                    }
                                ],
                                'Projection': {
                                    'ProjectionType': 'ALL'
                                },
                                "ProvisionedThroughput": {
                                    'ReadCapacityUnits': 5,
                                    'WriteCapacityUnits': 5
                                }
                            }
                        ]
                    )

                    # Wait until the table exists.
                    table.meta.client.get_waiter('table_exists').wait(TableName=cls.tablename)
                    return True
                else:
                    print "Table `%(tablename)s` already exists" % cls.__dict__
                return False


            @classmethod
            def delete(cls, id):
                try :
                    table = X.table()
                    response = table.delete_item(Key={cls.idfield : id})
                    return True
                except Exception :
                    return False

            @classmethod
            def exists(cls,id):
                try  :
                    cls.findById(id)
                    return True
                except Exception :
                    return False

            @classmethod
            def findById(cls, id):
                try :
                    response = X.table().get_item(
                        Key={
                            idfield: id
                        }
                    )
                    return response["Item"]
                except Exception, e :
                    entity = cls.entityname
                    raise errors.ObjectNotFound("Could not find %(entity)s with %(idfield)s `%(id)s`'"%vars())


            @classmethod
            def put(cls, options):
                entity = cls.entityname
                try :
                    id = options[idfield]
                    item = cls.findById(id)
                    overrides = {
                        "search" : item["name"].lower()+options.get("description",item.get("description","")).lower()+options.get("tags",item.get("tags","")).lower(),
                        "createdat" : item["createdat"],
                        "updatedat" : cls.strnow()
                    }
                    action = "update"
                except Exception, e :
                    action = "create"
                    overrides= {
                        "search" : options["name"].lower()+options.get("description","").lower()+options.get("tags","").lower(),
                        "createdat" : cls.strnow()
                    }
                if "name" in options.keys() and action == "update":
                    del  options["name"]

                options.update(overrides)
                try :
                    response = X.table().put_item(
                        Item=options
                    )
                    return cls.findById(options[idfield])
                except Exception, e :
                    raise e


            @classmethod
            def search(cls, term):
                items = []
                client = boto3.client("dynamodb", region_name="eu-west-1")
                try :
                    filtering_exp = Attr("search").contains(term.lower())

                    params = {
                        "TableName": tablename,
                        "IndexName": "search-index",
                        "FilterExpression": filtering_exp
                    }
                    paginator = client.get_paginator("scan")
                    page_iterator = paginator.paginate(**params)
                    page_iterator = paginator.paginate(**params)
                    for page in page_iterator :
                        for item in page ["Items"]:
                            items.append(item)
                except Exception ,e:
                    print e
                    return {}

            @classmethod
            def truncate(cls):
                for item in cls.list() :
                    cls.delete(id = item["id"])

            @classmethod
            def findByParent(cls, parentid):
                items = []
                client = boto3.client("dynamodb")
                try :
                    paginator = client.paginator("query")
                    filtering_exp = Key("parent").eq(parentid)
                    params = {
                        "TableName" : tablename,
                        "IndexName" : "parent-index",
                        "KeyConditionExpression" : filtering_exp
                    }
                    page_iterator = paginator.paginate(**params)
                    for page in page_iterator :
                        for item in page ["Items"]:
                            items.append(item)

                except Exception ,e:
                    print e
                return items

        X.tablename = tablename
        X.entityname = entityname
        X.idfield = idfield

        return X




if __name__=="__main__" :
    BotModel = TableModel.factory("airbotbots","botid","Bot")
    BotModel.delete_table()
    BotModel.create_table()

    exit()

    print BotModel.put({
        "accountid" : "airliquide",
        "botid" : "bot1",
        "name" : "salesbot",
        "description" : "another bot about your sales"
    })



    print BotModel.search("salesbot")
    exit()


    UserModel = TableModel.factory("databot_user")
    print UserModel.findById("moshir","username")