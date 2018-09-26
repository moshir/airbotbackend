from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
from factory import  base_factory, list_children_factory
import pprint



base_factory(objecttype="account",parentobjecttype=None,parentidentitifier=None,identifier="accountid")
list_children_factory(parentobjecttype="account", chilobjecttype="bot", childobjectpluralized="bots")
list_children_factory(parentobjecttype="account", chilobjecttype="user", childobjectpluralized="users")


@App.field(
    "createAccount",
    path = "Mutation/createAccount",
    argmap = {
        "/arguments/identity" : "identity"
    }
)
def create_account(identity):
    accountid = ID.now()
    uri = "uri:account:" + accountid

    candidates = [c for c in Item.query("account", Item.creator == identity )]
    if len(candidates) :
        raise errors.DuplicateError("You already created an airbot account ")


    account = Item(
        parent = "service",
        creator = identity,
        ID = uri,
        name = accountid ,
        createdat = ID.now(),
        search = "-",
        objecttype = "account"
    )

    account.save()

    owner = Item(
        parent= uri,
        creator=identity,
        ID="uri:user:" + accountid+":"+identity,
        name=identity,
        search=identity,
        createdat = ID.now(),
        objecttype="user"
    )
    owner.save()

    return account.attribute_values



@App.field(
    field = "inviteUser",
    path = "Mutation/inviteUser",
    argmap = {
        "/arguments/accountid" : "accountid",
        "/arguments/email" : "email",
        "/arguments/identity" : "identity"
    }
)
def invite(accountid, email, identity) :
    accountid = accountid.split(":")[2]
    user = Item(
        parent = accountid,
        name = email ,
        objecttype ="user",
        creator = identity,
        createdat = ID.now(),
        ID = "uri:user:%(accountid)s:%(email)s"%vars(),
        search = email
    )
    user.save()




if __name__ == "__main__" :
    response = App.route({
        "field": "listBots",
        "path": "Account/listBots",
        "arguments": {
            "identity": "moshir.mikael@gmail.com",
            "options": {
                "limit": 1,
                "offset" : 1
            }
        },
        "source" : {
            "ID": "uri:account:20180911183119"
        }
    })
    print pprint.pformat(response)
