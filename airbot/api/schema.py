import graphene
from mock import DBMock
from store import StoreProxy

class Base(graphene.Interface) :
    parent = graphene.ID(required=False)
    id = graphene.ID(required=True)
    createdat = graphene.String(required=False)
    updatedat= graphene.String(required=False)
    name = graphene.String(required=True)
    description = graphene.String(required=False)


class Reply (graphene.ObjectType) :
    class Meta :
        interfaces = (Base,)
    template = graphene.String()



class Rule(graphene.ObjectType) :
    class Meta :
        interfaces = (Base,)
    replacements = graphene.String()


class Intent(graphene.ObjectType) :
    class Meta :
        interfaces = (Base,)
    #sqltemplate = graphene.String()
    sql = graphene.String()
    chart = graphene.String()
    rules = graphene.List(Rule)
    replies = graphene.String()
    def resolve_rules(self,*args,**kwargs):
        return [Rule(**v) for v in StoreProxy.store().Intent.get_intent_rules(id=self.id)]


class Variable(graphene.ObjectType) :
    class Meta :
        interfaces = (Base,)
    field = graphene.String()
    aliases  = graphene.String()

class Entity(graphene.ObjectType):
    class Meta :
        interfaces = (Base,)
    variables = graphene.List(Variable)
    aliases = graphene.String()
    tablename = graphene.String()

    def resolve_variables(self,*args,**kwargs):
        variables = [Variable(**v) for v in StoreProxy.store().Entity.get_entity_variables(id=self.id)]
        return variables

class Bot(graphene.ObjectType) :
    class Meta :
        interfaces = (Base,)
    entities = graphene.List(Entity,id=graphene.String())
    intents = graphene.List(Intent,id=graphene.String())

    def resolve_intents(self,*args,**kwargs):
        return [Intent(**i) for i in StoreProxy.store().Bot.get_bot_intents(id=self.id)]

    def resolve_entities(self,*args,**kwargs):
        return [Entity(**e) for e in  StoreProxy.store().Bot.get_bot_entities(id=self.id)]


class User(graphene.ObjectType) :
    username = graphene.String()
    token = graphene.String()


