class DBMock:
    bots = {
        "1": {
            "parent": "1",
            "id": "1",
            "name": "mockbot",
            "description": "my mock bot"
        }}

    entities = {
        "e1": {
            "parent": "1",
            "id": "e1",
            "name": "table1",
            "description": "first table"
        }}

    variables = {
        "v1": {
            "id": "v1",
            "parent": "e1",
            "name": "c1",
            "field": "f1",
            "description": "field"
        }}

    intents = {
        "i1": {
            "parent": "1",
            "id": "i1",
            "name": "i1",
            "description": "how many things"
        }}

    rules = {
        "r1": {
            "parent": "i1",
            "id": "1",
            "replacements": "how many things in @c1.val"
        }}


    class Bot:
        @classmethod
        def findById(cls, id):
            return DBMock.bots[id]
        @classmethod
        def list(cls,offset=0, size=10):
            return DBMock.bots.values()

        @classmethod
        def get_bot_entities(cls,id,offet=0, size=10):
            return [e for e in DBMock.entities.values() if e["parent"] == id]

        @classmethod
        def get_bot_intents(cls,id,offet=0, size=10):
            intents= [i  for i  in DBMock.intents.values() if i["parent"] == id]
            return intents

        @classmethod
        def get_bot_variables(cls,id, offset=0, size=10):
            return [v for v in DBMock.variables.values() if DBMock.entities[v["parent"]].parent == id]

        @classmethod
        def get_bot_rules(cls,id, offset=0, size=10):
            return [r for r in DBMock.variables.rules() if DBMock.intents[r["parent"]].parent == id]


        @classmethod
        def put(cls, options):
            DBMock.bots[options.get("id")] = options

        @classmethod
        def delete(cls, id):
            del DBMock.bots[id]

    class Entity :
        @classmethod
        def findById(cls, id):
            return DBMock.entities[id]

        @classmethod
        def delete(cls, id):
            del DBMock.entities[id]

        @classmethod
        def put(cls, options):
            DBMock.entities[options["id"]] = options

        @classmethod
        def list(cls,offset=0, size=10):
            return DBMock.entities.values()

        @classmethod
        def get_entity_variables(cls,id):
            return [v for v in DBMock.variables.values() if v["parent"] == id]

    class Variable:
        @classmethod
        def findById(cls, id):
            return DBMock.variables[id]

        @classmethod
        def delete(cls, id):
            del DBMock.variables[id]

        @classmethod
        def put(cls, options):
            DBMock.variables[options["id"]] = options

    class Intent :
        @classmethod
        def findById(cls, id):
            return DBMock.intents[id]

        @classmethod
        def delete(cls, id):
            del DBMock.intents[id]


        @classmethod
        def put(cls, options):
            print "putting intent", options
            DBMock.intents[options["id"]] = options

        @classmethod
        def get_intent_rules(cls,id):
            return [v for v in DBMock.rules.values() if v["parent"] == id]

    class Rule :
        @classmethod
        def findById(cls, id):
            return DBMock.rules[id]

        @classmethod
        def delete(cls, id):
            del DBMock.rules[id]

        @classmethod
        def put(cls, options):
            DBMock.rules[options["id"]] = options



    @classmethod
    def put_bot(cls,id, name,description):
        DBMock.bots[id] = {
            "id" : id,
            "name" : name,
            "description" : description
        }


    @classmethod
    def put_entity(cls,parent, id, name,description):
        DBMock.entities[id] = {
            "parent" : parent,
            "id" : id,
            "name" : name,
            "description" : description
        }



    @classmethod
    def put_entity_variable(cls,parent, id, name,description, field):
        bot = DBMock.entities[id]["bot"]
        DBMock.entities[id] = {
            "parent" : parent,
            "id" : id,
            "name" : name,
            "description" : description,
            "field" : field
        }


    @classmethod
    def put_intent(cls,parent, id, name, description):
        DBMock.intents[id] = {
            "parent" : parent,
            "id" : id,
            "name" : name,
            "description" : description
        }



    @classmethod
    def put_intent_rule(cls,parent, id, name, replacements):
        bot = DBMock.intents[id]["bot"]
        DBMock.rules[id] = {
            "parent"  : parent,
            "id" : id,
            "name" : name,
            "replacements" : replacements
        }

    @classmethod
    def delete_bot(cls,bot):
        del DBMock.bots[id]
        DBMock.entities = [e for e in DBMock.entities.values() if e["bot"]!=bot]
        DBMock.intents= [e for e in DBMock.intents.values() if e["bot"]!=bot]
        DBMock.rules= [e for e in DBMock.rules.values() if e["bot"]!=bot]
        DBMock.variables= [e for e in DBMock.variables.values() if e["bot"]!=bot]

    @classmethod
    def delete_entity(cls, entityid):
        del DBMock.entities[id]
        DBMock.variables= [e for e in DBMock.variables.values() if e["parent"]!=entityid]


    @classmethod
    def delete_intent(cls, intentid):
        del DBMock.intents[id]
        DBMock.rules= [e for e in DBMock.rules.values() if e["parent"]!=intentid]



if __name__ == "__main__" :
    print DBMock.Bot.get_bot_intents(parent="1")
    print DBMock.Entity.get_entity_variables(parent="e1")
