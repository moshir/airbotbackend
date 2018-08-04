import json
import graphene
from server.databot.api.query import Query
from server.databot.api.mock import DBMock
from server.databot.api.store import StoreProxy
from server.databot.api.mutation import Mutation
from server.databot.model.models import Models
StoreProxy.store(Models)
schema = graphene.Schema(query=Query, mutation=Mutation)

response = schema.execute("""
                {{
                    bots{
                        id,
                        name
                    }
                }""")

if response.errors :
    print " ".join([e.message for e in response.errors])
else :
    print response.data

    print dict(response.data)
    print json.dumps(dict(response.data))