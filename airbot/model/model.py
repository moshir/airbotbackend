import pprint
import boto3
import errors
from boto3.dynamodb.conditions import Key
from datetime import datetime


class TableModel:
    @classmethod
    def factory(base , tablename):
        class X :
            @classmethod
            def strnow(cls):
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            @classmethod
            def table(cls):
                return X.db().Table(tablename)

            @classmethod
            def db(cls):
                try :
                    return X._db
                except AttributeError :
                    X._db =  boto3.resource('dynamodb', region_name='eu-west-1')
                    return X._db


            @classmethod
            def delete(cls, id):
                try :
                    table = X.table()
                    response = table.delete_item(Key={"id": id})
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
            def findById(cls, id,idfield="id"):
                try :
                    response = X.table().get_item(
                        Key={
                            idfield: id
                        }
                    )
                    return response["Item"]
                except Exception, e :
                    raise errors.ObjectNotFound("Could not find item with %(idfield)s'"%vars()+id+"' in "+tablename)


            @classmethod
            def put(cls, options):
                print "putting item ", pprint.pformat(options), "in table ", tablename
                try :
                    item = cls.findById(options["id"])
                    overrides = {
                        "createdat" : item["createdat"],
                        "updatedat" : cls.strnow()
                    }
                except Exception, e :
                    overrides= {
                        "createdat" : cls.strnow()
                    }
                options.update(overrides)
                try :
                    response = X.table().put_item(
                        Item=options
                    )
                    return response
                except Exception, e :
                    print "??", e
                    return {}

            @classmethod
            def list(cls, offset=0, size=5):
                try :
                    return X.table().scan()["Items"]
                except Exception , e :
                    return []

            @classmethod
            def findByName(cls, name):
                try :
                    filtering_exp = Key("name").eq(name)
                    return X.table().query(
                        IndexName='name-index',
                        KeyConditionExpression=filtering_exp)["Items"]
                except Exception ,e:
                    print e
                    return {}

            @classmethod
            def truncate(cls):
                for item in cls.list() :
                    cls.delete(id = item["id"])

            @classmethod
            def findByParent(cls, parentid):
                try :
                    filtering_exp = Key("parent").eq(parentid)
                    return X.table().query(
                        IndexName='parent-index',
                        KeyConditionExpression=filtering_exp)["Items"]
                except Exception ,e:
                    print e
                    return [{}]

        return X




if __name__=="__main__" :
    BotModel = TableModel.factory("databot_bot")
    print BotModel.put({
        "id" : "bot1",
        "name" : "salesbot",
        "description" : "a bot about your sales"
    })

    print BotModel.findById("bot1")
    print BotModel.findByName("salesbot")
    print BotModel.list()


    UserModel = TableModel.factory("databot_user")
    print UserModel.findById("moshir","username")