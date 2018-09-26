import json
import pprint
import re
import types
import tracery

class Airbot:
    """ slot patterns created in lex for entities, variable, variable operator and variable value"""
    patterns = [
        {
            "name": "entity",
            "regexp": r"(?P<entityname>@@\w+)",
            "extract": lambda match: match.group().replace("@@", "")
        },
        {
            "name": "variableop",
            "regexp": r"(?P<variableop>@\w+.op)",
            "extract": lambda match: match.group().replace("@", "").replace(".op", "op")
        },
        {
            "name": "variableval",
            "regexp": r"(?P<variableval>@\w+.val)",
            "extract": lambda match: match.group().replace("@", "").replace(".val", "val")
        },
        {
            "name": "variable",
            "regexp": r"(?P<variablename>@\w+)",
            "extract": lambda match: match.group().replace("@", "")
        }
    ]

    @staticmethod
    def to_lex(matchobj):
        """ turns a matchobject and returns {name}. this is used to transform airbot annotations like
        - @@entity
        - @variable
        - @variable.val
        - @variable.op
        to valid  lex slots  {slot}
        Example :
        >>> m = re.compile(Airbot.patterns[0]["regexp"]).match("this is a @variable")
        >>> Airbot.to_lex(m)
        "this is a {variable}"
        """
        pattern = [p for p in Airbot.patterns if p["regexp"] == matchobj.re.pattern][0]
        return "{" + pattern["extract"](matchobj) + "}"

    @staticmethod
    def to_tracery(matchobj):
        """ turns a matchobject and returns #name# .
        This is used to transform airbot annotations like
        - @@entity
        - @variable
        - @variable.val
        - @variable.op
        to valid  tracery generators #slot#
        Example
        >>> m = re.compile(Airbot.patterns[0]["regexp"]).match("this is a @variable")
        >>> Airbot.to_tracery(m)
        "this is a #variable#"

        """
        pattern = [p for p in Airbot.patterns if p["regexp"] == matchobj.re.pattern][0]
        return "#" + pattern["extract"](matchobj) + "#"

    @staticmethod
    def parse(expression, pattern, replacer):
        """takes a string , finds matching occurences of the pattern and replace them using the provided replacer(match) method
        This is applied to trasnform an airbot rule to a valid lex or tracery expression
        Example
        >>> #Replace entities in a string with the lex slot:
        >>> parse("This is a @variable from an @@entity", Airbot.patterns[0],Airbot.to_lex)
        "This is a @variable from en {entity}"
        """
        regex = [p["regexp"] for p in Airbot.patterns if p["name"] == pattern][0]
        return re.sub(regex, replacer, expression)

    @staticmethod
    def to_grammar(expression, replacer=to_lex):
        """ applies parse to expression by replacing all patterns in Lex.patterns
        Example
        >>> Airbot.to_grammar("This is a @variable  from an @@entity ")
        "This is a {variable} from  and {entity}"
        """
        if (type(expression) == types.ListType):
            return [Airbot.to_grammar(expr, replacer) for expr in expression]
        intent = expression
        for pattern in Airbot.patterns:
            key = pattern["name"]
            intent = Airbot.parse(intent, key, replacer)
        return intent

    @staticmethod
    def get_intent_config(intent, graph, mode="lex"):
        """ Takes a bot graph with intents and slots keys and build the Lex put_intent arguments.

        """
        grammar = {
            "rules": {},
            "slots": {},
            "utterances": {}
        }
        for rule in graph["intents"][intent].keys():
            grammar["rules"][rule] = []
            rules = graph["intents"][intent][rule]
            for expression in rules:
                print expression
                grammar["rules"][rule].append(Airbot.to_grammar(expression, Airbot.to_tracery))
        print grammar
        for slot in graph["slots"].keys():
            grammar["slots"][slot] = graph["slots"][slot]["values"]
            if slot[-3:] == "val" and mode == "lex":
                grammar["slots"][slot] = graph["slots"][slot]["ref"]

        rules = grammar["rules"]
        rules.update(grammar["slots"])
        generator = tracery.Grammar(rules)
        for i in range(1, 1000):
            if len(grammar["utterances"]) > 300:
                break
            utterance = generator.flatten("#origin#")
            grammar["utterances"][hash(utterance)] = utterance.lstrip().replace(",", "")
        used_slots = {}
        for utterance in grammar["utterances"].values():
            for s in grammar["slots"].keys():
                if s in utterance and s not in used_slots.keys():
                    used_slots[s] = graph["slots"][s]

        config = {
            "name": intent,
            "description": 'string',
            "slots": [{
                "valueSelectionStrategy": 'ORIGINAL_VALUE',
                "name": s,
                "slotType": s,
                "enumerationValues": graph["slots"][s]["values"],
            } for s in used_slots.keys()],
            "sampleUtterances": grammar["utterances"].values(),
            "fulfillmentActivity": {
                'type': 'ReturnIntent'
            },

        }
        return config




