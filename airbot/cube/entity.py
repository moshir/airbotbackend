from argparse import Namespace
import tracery
from airbot.lex.bot import Bot
import pprint



class Doc:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Cube :


    """
    show the {qty} of {entity}
    show the {qty} of {entity} per {dimension.name}
    {calc} {qty} of {entity} with {dimension.name} {operator} {dim.value}
    {calc} {qty} of {entity} with {dimension.name} {operator}  {dim.value} by {dimension.name}

    """

    def __init__(self, name,entities):
        self.name = name
        self.entities = entities
        self.lex_rules = {
            "origin" : [
                "#action# #qty#  #entity# #filter# #group#",
            ],
            "action" : ["{%(name)saction}"%vars()],
            "qty": ["#scalar#","#calc#"],
            "scalar": ["{%(name)sscalar}"%vars()],
            "calc": ["#agg# #measure# of",],
            "agg":["{%(name)sagg}"%vars()],
            "measure":["{%(name)smeasure}"%vars()],
            "entity":["{%(name)sentity}"%vars()],
            "filter":[
                " ",
                "with {%(name)sfilterfielda} {%(name)sfilteropa} {%(name)sfieldvaluea}"%vars(),
                "with {%(name)sfilterfielda} {%(name)sfilteropa} {%(name)sfieldvaluea} and {%(name)sfilterfieldb} {%(name)sfilteropb} {%(name)sfieldvalueb}"%vars()
              ],
            "op":["{%(name)sfilterop}"%vars()],
            "group" : [
                "",
                "by {%(name)sdimfielda}"%vars(),
                "by {%(name)sdimfielda} and {%(name)sdimfieldb}"%vars()
            ]
        }

    @property
    def utterances(self):
        utterances=[]
        generator = tracery.Grammar(self.lex_rules)
        for i in range(1,3000) :
            utterance = generator.flatten("#origin#").replace("  "," ").strip()
            if utterance not in utterances:
                #if len(utterance)<200:
                    utterances.append(utterance)
                    print utterance, len(utterance)
                    yield utterance
        #return utterances

    def get_entity_aliases(self):
        aliases = []
        for e in self.entities :
            for e in e["aliases"]:
                aliases.append(e)
        return aliases

    def get_variable_aliases(self, vtype):
        aliases =[]
        for e in self.entities :
            for v in e["variables"] :
                print "??", v
                if v["type"].lower()==vtype.lower():
                    for alias in v["aliases"] :
                        aliases.append(alias)
        return aliases

    def get_variable_values(self):
        values=[]
        for e in self.entities :
            for v in e["variables"] :
                if v["type"].lower()=="dimension":
                    for value in v["values"] :
                        values.append(value)
        return values

    def deploy_bot(self):
        name = self.name
        Bot.add_slot_type("%(name)saction"%vars(), ["show", "tell me"])
        Bot.add_slot_type("%(name)sentity"%vars(), self.get_entity_aliases())
        Bot.add_slot_type("%(name)sscalar"%vars(), ["number of", "total number of", "overall number of"])
        Bot.add_slot_type("%(name)sagg"%vars(), ["sum", "greatest", "smallest"])
        Bot.add_slot_type("%(name)smeasure"%vars(), self.get_variable_aliases("Metric"))
        Bot.add_slot_type("%(name)sdimfielda"%vars(), self.get_variable_aliases("dimension"))
        Bot.add_slot_type("%(name)sdimfieldb"%vars(), self.get_variable_aliases("dimension"))
        Bot.add_slot_type("%(name)sfilterfielda"%vars(), self.get_variable_aliases("dimension"))
        Bot.add_slot_type("%(name)sfilterfieldb"%vars(), self.get_variable_aliases("dimension"))
        Bot.add_slot_type("%(name)sfilteropa"%vars(), ["diffrent from ", "equals", "greater than", "lower than"])
        Bot.add_slot_type("%(name)sfilteropb"%vars(), ["diffrent from ", "equals", "greater than", "lower than"])
        Bot.add_slot_type("%(name)sfieldvaluea"%vars(), self.get_variable_values())
        Bot.add_slot_type("%(name)sfieldvalueb"%vars(), self.get_variable_values())


        utterances = list(self.utterances)
        print ">>",len(utterances)

        Bot.add_intent({
            "sampleUtterances": utterances[:1500],
            "name": "%(name)sgeneral"%vars(),
            "slots": [
                {"name": "%(name)sentity"%vars(), "slotType": "%(name)sentity"%vars()},
                {"name": "%(name)saction"%vars(), "slotType": "%(name)saction"%vars()},
                {"name": "%(name)sscalar"%vars(), "slotType": "%(name)sscalar"%vars()},
                {"name": "%(name)sagg"%vars(), "slotType": "%(name)sagg"%vars()},
                {"name": "%(name)smeasure"%vars(), "slotType": "%(name)smeasure"%vars()},
                {"name": "%(name)sdimfielda"%vars(), "slotType": "%(name)sdimfielda"%vars()},
                {"name": "%(name)sdimfieldb"%vars(), "slotType": "%(name)sdimfieldb"%vars()},
                {"name": "%(name)sfilterfielda"%vars(), "slotType": "%(name)sfilterfielda"%vars()},
                {"name": "%(name)sfilterfieldb"%vars(), "slotType": "%(name)sfilterfieldb"%vars()},
                {"name": "%(name)sfilteropa"%vars(), "slotType": "%(name)sfilteropa"%vars()},
                {"name": "%(name)sfilteropb"%vars(), "slotType": "%(name)sfilteropb"%vars()},
                {"name": "%(name)sfieldvaluea"%vars(), "slotType": "%(name)sfieldvaluea"%vars()},
                {"name": "%(name)sfieldvalueb"%vars(), "slotType": "%(name)sfieldvalueb"%vars()}
            ]
        })

        Bot.build(self.name, intents=["%(name)sgeneral"%vars()])

    def search_entity_by_alias(self, alias):
        print "searching entity for alias", alias
        candidates =  []
        for e in self.entities :
            print "is it ", e["name"],"? aliases = ",e["aliases"]
            if alias in e["aliases"]:
                candidates.append(e)
        return candidates


    def search_variable_by_alias(self,alias ):
        print "looking for variable for alias", alias
        candidates =  []
        for e in self.entities :
            for v in e["variables"]:
                print " ... is it ", v["name"],v["aliases"]
                if alias in v["aliases"]:
                    candidates.append(v)
        return candidates



    def resolve(self, data):
        slots = {}
        for k in data.keys() :
            slots[k.replace(self.name,"")]= data[k]


        print pprint.pformat(slots)
        entity = self.resolve_entity(slots)
        print entity
        filters= self.resolve_filters(slots)
        print filters
        groups = self.resolve_groups(slots)

        select = self.resolve_select(slots)
        dimensions = self.resolve_dimensions(slots)

        semantics = {
            #"entity" : entity,
            "tablename" : '"%(database)s"."%(tablename)s"'%entity,
            "select" : select,
            "dimensions" : dimensions,
            "filters" : filters,
            "groups" :groups,
            "display" : {}
        }

        if len(groups)>0 :
            semantics["display"] ["type"]= "chart"
            semantics["display"]["y"]={
                "index" : "measure",
                "label" : "measure"
            }

            semantics["display"]["x"] = [{
                "index" :"dima",
                "label" : groups[0]["label"]
            }]
            if len(groups)==2 :
                semantics["display"]["x"].append({
                "index" :"dimb",
                "label" : groups[1]["label"]
                })
        else :
            semantics["display"] ["type"]= "text"
        if len(dimensions) :
            dims = ",".join([d["field"] for d in dimensions])
        else :
            dims =""

        sql = [
            "select ",
            select["select"],
            dims,
            "from",
            '"%(database)s"."%(tablename)s"' % entity
        ]

        if len(filters) :
            sql.append(" where ")
            sql.append(" and \n".join([f["expression"] for f in filters]))
        if len(groups) :
            sql.append("group by")
            sql.append(", ".join([g["field"] for g in groups]))

        semantics["sql"] = "  \n ".join(sql)
        return semantics


    def resolve_dimensions(self, slots):
        dims =[]
        if slots["dimfielda"] is not None :
            variable = self.search_variable_by_alias(slots["dimfielda"])[0]
            dims.append({
                "field" : '"%(tablename)s"."%(field)s" as dima'%variable,
                "index" : "dima"
            })

        if slots["dimfieldb"] is not None:
            variable = self.search_variable_by_alias(slots["dimfieldb"])[0]
            dims.append({
                "field": '"%(tablename)s"."%(field)s" as dimb' % variable,
                "index": "dimb"
            })
        return dims

    def resolve_groups(self, slots):
        groups = []
        if slots["dimfielda"] is not None :
            variable = self.search_variable_by_alias(slots["dimfielda"])[0]
            groups.append({
                "field" : '"%(tablename)s"."%(field)s"'%variable,
                "label" : slots["dimfielda"]
            })

        if slots["dimfieldb"] is not None :
            variable = self.search_variable_by_alias(slots["dimfieldb"])[0]
            groups.append({
                "field" : '"%(tablename)s"."%(field)s"'%variable,
                "label": slots["dimfieldb"]
            })

        return groups


    def resolve_select(self, slots):
        if slots["scalar"] is not None :
            return self.resolve_scalar(slots)
        elif slots["agg"] is not None and  slots["measure"] is not None :
            return self.resolve_agg(slots)

    def resolve_scalar(self, slots):
        return {
            "select" : "count(*) as measure",
            "type" : "scalar"
        }

    def resolve_agg(self, slots):
        if slots ["measure"] is not None and slots["agg"] is not None :
            variable = self.search_variable_by_alias(slots["measure"])[0]
            field = variable["field"]
            tablename = variable["tablename"]
            fn = self.resolve_function(slots["agg"])
            return {
                "select" : '%(fn)s("%(tablename)s"."%(field)s") as measure'%vars(),
                "type" : "function",
                "alias" : "measure"
            }


    def resolve_entity(self, slots):
        alias = slots["entity"]
        entity = self.search_entity_by_alias(alias)
        return entity[0]

    def resolver_operator(self, operator):
        return {
            "equals" : "=",
            "equal" : "=",
            "not equal":"!=",
            "not the same":"!=",
            "not the same as":"!=",
            "different from" : "!=",
            "greater" : ">=",
            "smaller": "<="
        }[operator]

    def resolve_function(self,fn):
        return {
            "sum" : "SUM",
            "max" : "MAX",
            "greatest" : "MAX",
            "smallest" : "MIN",
            "maxium" : "MAX",
            "average" : "AVG",
            "min" : "MIN",
            "minimum" : "MIN"
        }[fn.lower()]

    def resolve_filters(self, slots):
        filters=[]
        if slots["filterfielda"] and slots["fieldvaluea"] is not None :
            variable = self.search_variable_by_alias(slots["filterfielda"])[0]
            value = slots["fieldvaluea"]
            filter = {
                "tablename" : variable["tablename"],
                "field" : variable["field"],
                "type": variable["type"],
                "op": self.resolver_operator(slots["filteropa"])
            }
            print filter
            if variable["type"].lower()=="metric" :
                filter["value"] = float(value)
            elif variable["type"].lower()=="dimension" :
                filter["value"] = "'"+str(value)+"'"
            filter["expression"]= '"%(tablename)s"."%(field)s" %(op)s %(value)s'%filter
            filter["semantic"]= "%(filterfielda)s %(filteropa)s %(fieldvaluea)s"%slots
            filters.append(filter)

        return filters








if __name__=="__main__" :

    entities= [
        {
            "name" : "customer",
            "aliases" : ["customers","people","users","clients"],
            "variables" : [
                {
                    "name" : "age",
                    "aliases": ["age"],
                    "type" : "Measure",
                    "values":  [str(i) for i in range(1,10)]#["one", "two","three"]
                },
                {
                    "name": "sex",
                    "aliases": ["sex","genre"],
                    "type": "dimension",
                    "values": ["boy","girl"]
                }
            ]
        }
    ]

    Cube(name="ab", entities=entities).deploy_bot()
    exit()



    Bot.add_slot_type("action",["show","tell me"])
    Bot.add_slot_type("entity",["customers","sales","alerts"])
    Bot.add_slot_type("scalar",["number of","total number of","overall number of"])
    Bot.add_slot_type("agg",["sum","greatest","smallest"])
    Bot.add_slot_type("measure",["size","temperature","weigth","revenue"])
    Bot.add_slot_type("dimfielda",["country","city","customer","type"])
    Bot.add_slot_type("dimfieldb",["country","city","customer","type"])
    Bot.add_slot_type("filterfielda",["country","city","customer","type"])
    Bot.add_slot_type("filterfieldb",["country","city","customer","type"])
    Bot.add_slot_type("filteropa",["diffrent from ","equals","greater than","lower than"])
    Bot.add_slot_type("filteropb",["diffrent from ","equals","greater than","lower than"])
    Bot.add_slot_type("fieldvaluea",["paris","usa","canada"])
    Bot.add_slot_type("fieldvalueb",["paris","ceo"])

    utterances = list(C.utterances)

    Bot.add_intent({
        "sampleUtterances": utterances[:1500],
        "name": "general",
        "slots": [
            {"name": "entity", "slotType": "entity"},
            {"name": "action", "slotType": "action"},
            {"name": "scalar", "slotType": "scalar"},
            {"name": "agg", "slotType": "agg"},
            {"name": "measure", "slotType": "measure"},
            {"name": "dimfielda", "slotType": "dimfielda"},
            {"name": "dimfieldb", "slotType": "dimfieldb"},
            {"name": "filterfielda", "slotType": "filterfielda"},
            {"name": "filterfieldb", "slotType": "filterfieldb"},
            {"name": "filteropa", "slotType": "filteropa"},
            {"name": "filteropb", "slotType": "filteropb"},
            {"name": "fieldvaluea", "slotType": "fieldvaluea"},
            {"name": "fieldvalueb", "slotType": "fieldvalueb"}
        ]
    })

    Bot.build("A", intents=["general"])



    C = Cube()
    utterances = list(C.utterances)

    Bot.add_intent({
        "sampleUtterances": utterances[:1500],
        "name": "general",
        "slots":[
            {"name" : "entity","slotType":"entity"},
            {"name" : "action","slotType":"action"},
            {"name" : "scalar","slotType":"scalar"},
            {"name" : "agg","slotType":"agg"},
            {"name" : "measure","slotType":"measure"},
            {"name" : "dimfielda","slotType":"dimfielda"},
            {"name" : "dimfieldb","slotType":"dimfieldb"},
            {"name" : "filterfielda","slotType":"filterfielda"},
            {"name" : "filterfieldb","slotType":"filterfieldb"},
            {"name" : "filteropa","slotType":"filteropa"},
            {"name" : "filteropb","slotType":"filteropb"},
            {"name" : "fieldvaluea","slotType":"fieldvaluea"},
            {"name" : "fieldvalueb","slotType":"fieldvalueb"}
        ]
    })


    Bot.build("airbot", intents=["general"])








