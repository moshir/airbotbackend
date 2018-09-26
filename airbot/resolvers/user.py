from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
from factory import  base_factory, list_children_factory, apply_options
import pprint



#base_factory(objecttype="user",parentobjecttype="account",parentidentitifier="accountid",identifier="userid")


@App.field(
    field ="listMyAccounts",
    path = "Query/listMyAccounts",
    argmap = {
        "/arguments/identity" : "identity",
        "/arguments/options" : "options"
    }
)
def list_accounts(identity,options) :
    accounts  =[]
    iterator = apply_options(Item.query("user", Item.name.__eq__(identity)),options)
    for user in iterator:
        try :
            print user.attribute_values
            account = Item.get("account", user.parent)
            accounts.append(account.attribute_values)
        except Exception,e :
            pass
    return accounts



if __name__=="__main__" :


    response = App.route({
        "field" : "listMyAccounts",
        "path" : "Query/listMyAccounts",
        "arguments" : {
            "identity" : "moshir.mikael@gmail.com",
            "options" : {"limit" : 200}
        }
    })
    #response = list_accounts("moshir.mikael@gmail.com",None)
    print pprint.pformat(response)