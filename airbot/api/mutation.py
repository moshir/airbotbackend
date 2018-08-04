import graphene
from schema import Bot,Intent,Entity,Variable,Rule
from store import StoreProxy

"da2-w7dgmvbdvba5fgvaqn6733eze4"




class RuleInput(graphene.InputObjectType):

    parent = graphene.ID()
    id = graphene.ID()
    name = graphene.String()
    replacements = graphene.String()
    description = graphene.String()


class IntentInput(graphene.InputObjectType):
    parent = graphene.ID()
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    rules = graphene.List(RuleInput)
    sql = graphene.String()
    replies= graphene.String()


class VariableInput(graphene.InputObjectType) :
    parent = graphene.ID()
    id = graphene.ID()
    name = graphene.String()
    field = graphene.String()
    aliases = graphene.String()
    description = graphene.String()


class EntityInput(graphene.InputObjectType) :
    parent = graphene.ID()
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    aliases = graphene.String()
    tablename = graphene.String()
    variables = graphene.List(VariableInput)

class BotInput(graphene.InputObjectType):

    id = graphene.ID()
    name = graphene.String()
    description = graphene.String(required=False)
    entities = graphene.List(EntityInput)
    intents = graphene.List(EntityInput)



class BotMutation(graphene.Mutation):
    class Arguments:
        options = BotInput(required=True)
        action  = graphene.String(required=True)

    bot = graphene.Field(Bot)
    entities = graphene.List(Entity)
    intents = graphene.List(Intent)


    def resolve_entities(self):
        return graphene.List()

    def resolve_intents(self):
        return graphene.List()

    def mutate(self, info, action = "PUT",options=None):
        if action== "PUT" :
            StoreProxy.store().Bot.put(options)
        elif action == "DELETE":
            StoreProxy.store().Bot.delete(options["id"])
        else :
            raise Exception("Unsupported mutation action")
        bot = Bot(**options)
        return BotMutation(bot=bot)

class EntityMutation(graphene.Mutation):
    class Arguments:
        action  = graphene.String(required=True)
        options = EntityInput(required=True)

    entity= graphene.Field(Entity)
    variables = graphene.List(Variable)
    def resolve_variables(self):
        return graphene.List()

    def mutate(self, info, action = "PUT",options=None):
        if action== "PUT" :
            StoreProxy.store().Entity.put(options)
        elif action == "DELETE":
            StoreProxy.store().Entity.delete(options["id"])
        else :
            raise Exception("Unsupported mutation action")
        entity = Entity(**options)
        return EntityMutation(entity=entity)


class IntentMutation(graphene.Mutation):
    class Arguments:
        action  = graphene.String(required=True)
        options = IntentInput(required=True)

    intent = graphene.Field(Intent)
    rules = graphene.List(Rule)
    bot = graphene.Field(Bot)

    def resolve_bot(self):
        return Bot(**StoreProxy.store().Bot.findById(id=self.parent))

    def resolve_rules(self):
        return graphene.List()

    def mutate(self, info, action = "PUT",options=None):
        if action== "PUT" :
            StoreProxy.store().Intent.put(options)
        elif action == "DELETE":
            StoreProxy.store().Intent.delete(options["id"])
        else :
            raise Exception("Unsupported mutation action")
        intent = Intent(**options)
        return IntentMutation(intent=intent)


class VariableMutation(graphene.Mutation):
    class Arguments:
        action  = graphene.String(required=True)
        options = VariableInput(required=True)

    variable = graphene.Field(Variable)
    entity = graphene.Field(Entity)

    def resolve_entity(self):
        return Entity(**StoreProxy.Entity.findById(id = self.parent))

    def mutate(self, info, action = "PUT",options=None):
        if action== "PUT" :
            StoreProxy.store().Variable.put(options)
        elif action == "DELETE":
            StoreProxy.store().Variable.delete(options["id"])
        else :
            raise Exception("Unsupported mutation action")
        variable = Variable(**options)
        return VariableMutation(variable=variable)


class RuleMutation(graphene.Mutation):
    class Arguments:
        action  = graphene.String(required=True)
        options = RuleInput(required=True)

    rule = graphene.Field(Rule)
    intent = graphene.Field(Intent)

    def resolve_intent(self):
        return Intent(**StoreProxy.Intent.findById(id = self.parent))

    def mutate(self, info, action = "PUT",options=None):
        if action== "PUT" :
            StoreProxy.store().Rule.put(options)
        elif action == "DELETE":
            StoreProxy.store().Rule.delete(options["id"])
        else :
            raise Exception("Unsupported mutation action")
        rule = Rule(**options)
        return RuleMutation(rule=rule)


class Mutation(graphene.ObjectType):
    manageBot = BotMutation.Field()
    manageEntity = EntityMutation.Field()
    manageIntent= IntentMutation.Field()
    manageVariable= VariableMutation.Field()
    manageRule= RuleMutation.Field()


if __name__ == "__main__" :
    from query import Query
    from server.databot.model.models import Models
    from store import StoreProxy
    StoreProxy.store(Models)
    schema = graphene.Schema(query=Query, mutation=Mutation)

    response = schema.execute(""" 
            mutation X{
                manageIntent(action : "PUT", options : {
                    id : "qnxarmz",
                    parent : "222",
                    name : "itworks",
                    description: "Unset",
                    sql : "select * ",
                    replies : "sss"
                }){
                    intent{
                        id,
                        name,
                        description
                    }
                }
            }
        """)
    print response.errors