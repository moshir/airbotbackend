
from airbot.lex.airbot import Airbot
import unittest
import re


class Test (unittest.TestCase):
    def test_parse(self):
        entitypattern=      Airbot.patterns[0]["regexp"]
        s = Airbot.parse("This is an @@entity", "entity",Airbot.to_lex)
        self.assertTrue(s,"This is an {entity}")

        s = Airbot.parse("This is a @variable", "entity",Airbot.to_lex)
        self.assertTrue(s,"This is a @variable")


        s = Airbot.parse("This is a @variable", "variable",Airbot.to_lex)
        self.assertTrue(s,"This is a {variable}")



        s = Airbot.parse("This is a @variable.val", "variableval",Airbot.to_lex)
        self.assertTrue(s,"This is a {variableval}")

        s = Airbot.parse("This is a @variable.val", "variableval",Airbot.to_tracery)
        self.assertTrue(s,"This is a #variableval#")

    def test_to_grammar(self):
        expr = "this is @variable.val from a @variable under an @@entity"
        s = Airbot.to_grammar(expr,Airbot.to_lex)
        self.assertTrue(s,"this is a {variableval} from a {variable} under an {entity}")


    def test_get_intent_config(self):
        graph = {
            "slots": {
                "city": {
                    "values": ["town", "city"],
                    "ref" : "{city}"
                },
                "cityval": {
                    "values" : ["paris", "london", "newyork"],
                    "ref" : "{cityval}"
                },
                "cityop": {
                    "values" : ["inside", "outside", "in", "not in"],
                    "ref": "{cityop}"
                },
                "entity": {
                    "values" : ["people", "user"],
                    "ref": "{entity}"
                },
                "otherslot": {
                    "ref": "{otherslot}",
                    "values" : ["something"]
                }
            },
            "intents" :{
                "howmany" : {
                    "origin" : ["how many @@entity do we have @city.op @city @city.val"]
                    }
                }
            }
        print Airbot.get_intent_config("howmany", graph,"tracery")

