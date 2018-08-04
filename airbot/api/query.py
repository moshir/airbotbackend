import graphene
from schema import Bot, Intent, Entity, Variable, Rule
from store import StoreProxy


class Query(graphene.ObjectType):
    @classmethod
    def store(cls, store=None):
        return StoreProxy.store()

    # objects
    bot = graphene.Field(Bot, id=graphene.String())
    entity = graphene.Field(Entity, id=graphene.String())
    intent = graphene.Field(Intent, id=graphene.String())
    variable = graphene.Field(Variable, id=graphene.String())
    rule = graphene.Field(Rule, id=graphene.String())

    # sets
    bots = graphene.List(Bot, offset=graphene.Int(), size=graphene.Int())
    entities = graphene.List(Entity, botid=graphene.String(), offset=graphene.Int(), size=graphene.Int())
    intents = graphene.List(Intent, botid=graphene.String(), offset=graphene.Int(), size=graphene.Int())
    variables = graphene.List(Variable, entityid=graphene.String(), offset=graphene.Int(), size=graphene.Int())
    rules = graphene.List(Rule, intentid=graphene.String(), offset=graphene.Int(), size=graphene.Int())

    def resolve_bot(self, info, id):
        try:
            bot = StoreProxy.store().Bot.findById(id=id)
            return Bot(**bot)
        except Exception, e:
            print "e = ", e
            return Bot(**{})

    def resolve_entity(self, *args, **kwargs):
        return Entity(**StoreProxy.store().Entity.findById(id=kwargs["id"]))

    def resolve_intent(self, *args, **kwargs):
        return Intent(**StoreProxy.store().Intent.findById(id=kwargs["id"]))

    def resolve_variable(self, *args, **kwargs):
        return Variable(**Query.store().Variable.findById(id=kwargs["id"]))

    def resolve_variables(self, info, entityid, offset=None, limit=None):
        return [Variable(**v) for v in StoreProxy.store().Variable.findByParent(parentid=entityid)]

    def resolve_rules(self, info, intentid, offset=None, limit=None):
        return [Rule(**r) for r  in StoreProxy.store().Rule.findByParent(parentid=intentid)]

    def resolve_rule(self, *args, **kwargs):
        return Rule(**Query.store().Rule.findById(id=kwargs["id"]))

    def resolve_bots(self, info, offset=0, size=10):
        return [Bot(**b) for b in Query.store().Bot.list(offset=offset, size=size)]


if __name__ == "__main__":
    from server.databot.model.models import Models

    StoreProxy.store(Models)
    schema = graphene.Schema(query=Query)
    r = schema.execute("""
            {
            rules(intentid:"qnxarmz") {
                    parent,
                    id,
                    name,
                    description,
                    replacements
            }
            
        }
    """)
    print r.errors
    print r.data
