import boto3
import errors
from boto3.dynamodb.conditions import Key
from model import TableModel



class Models :
    Bot= TableModel.factory("databot_bot")
    Intent= TableModel.factory("databot_intent")
    Entity= TableModel.factory("databot_entity")
    Variable = TableModel.factory("databot_variable")
    Rule = TableModel.factory("databot_rule")
    User = TableModel.factory("databot_user")





def get_bot_entities(cls, id):
    return Models.Entity.findByParent(parentid=id)


def get_bot_intents(cls, id):
    print "get_bot_intents", id
    return Models.Intent.findByParent(parentid=id)

def get_intent_rules(cls, id):
    return Models.Rule.findByParent(parentid=id)


def get_entity_variables(cls, id):
    return Models.Variable.findByParent(parentid=id)

setattr(Models.Bot, 'get_bot_entities', classmethod(get_bot_entities))
setattr(Models.Bot, 'get_bot_intents', classmethod(get_bot_intents))
setattr(Models.Entity, 'get_entity_variables', classmethod(get_entity_variables))
setattr(Models.Intent, 'get_intent_rules', classmethod(get_intent_rules))
#Models.Bot.get_bot_entities = Models.get_bot_entities
#Models.Bot.get_bot_intents= Models.get_bot_intents
#Models.Intent.get_intent_rules = Models.get_intent_rules
#Models.Entity.get_entity_variables = Models.get_entity_variables



if __name__ == "__main__" :
    pass

