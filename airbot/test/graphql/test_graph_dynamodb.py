from os import path
import sys

currentdir= path.dirname(__file__)
srcdir = path.realpath(path.join(currentdir,"../.."))
sys.path.append(srcdir)
print sys.path
import pprint
import json
import graphene
import unittest

from server.databot.api.query import Query
from server.databot.api.mock import DBMock
from server.databot.api.store import StoreProxy
from server.databot.api.mutation import Mutation
from server.databot.model.models import Models


class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        StoreProxy.store(Models)
        cls.schema = graphene.Schema(query=Query, mutation=Mutation)

    def test_bot_api(self):
        Models.Bot.truncate()
        Models.Entity.truncate()
        Models.Intent.truncate()
        Models.Variable.truncate()
        Models.Rule.truncate()

        response = TestQuery.schema.execute("""
                {
                    bots{
                        id,
                        name
                    }
                }""")
        self.assertEqual(response.errors, None, "no errors")
        print ".. "*50
        print response.data["bots"]
        self.assertEqual(len(response.data["bots"]), 0, "one bot retrieved ")

        response = TestQuery.schema.execute(""" 
            mutation X{
                manageBot (action : "PUT", options : {name : "graphbot", id : "222", description : "xxxx"}){
                    bot {
                        name , 
                        description,
                        id,
                        entities {
                            name
                        }
                    }
                }
            }
        """)

        self.assertEqual(response.errors, None, "no errors")
        self.assertEqual(response.data["manageBot"]["bot"]["id"], "222", "right id")

        response = TestQuery.schema.execute("""{
            bots{
                id,
                name,
                description,
                intents {
                    name
                }
                entities{
                    name
                }
            }
        }""")
        self.assertEqual(response.errors, None, "no errors")
        print response.data["bots"]
        self.assertEqual(len(response.data["bots"]), 1, "one bot retrieved ")

    def test_entity_api(self):
        Models.Bot.truncate()
        Models.Entity.truncate()
        Models.Intent.truncate()
        Models.Variable.truncate()
        Models.Rule.truncate()
        response = TestQuery.schema.execute("""
            mutation B{
                manageBot(action : "PUT" , options : {name : "graphbot", id : "222"}){
                    bot {
                        id
                    }
                }
            }
        """)
        response = TestQuery.schema.execute(""" 
            mutation X{
                manageEntity(action : "PUT", options : {parent : "222",name : "myentity", id : "e1", description : "xxxx"}){
                    entity {
                        name,
                        id
                    }
                }
            }
        """)

        response = TestQuery.schema.execute("""
        {
            entity (id:"e1"){
                name,
                id
            }
        }
        """)

        print "..", response.errors
        print "..", response.data
        self.assertEqual(response.data["entity"]["name"], "myentity", "retrieved entity")

    def test_intent_api(self):
        Models.Bot.truncate()
        Models.Entity.truncate()
        Models.Intent.truncate()
        Models.Variable.truncate()
        Models.Rule.truncate()
        response = TestQuery.schema.execute("""
                   mutation B{
                       manageBot(action : "PUT" , options : {name : "graphbot", id : "222"}){
                           bot {
                               id
                           }
                       }
                   }
               """)
        print response.errors
        print response.data
        bot = Models.Bot.findById(id="222")
        self.assertEqual(bot["id"], "222", "saved bot to ddb")
        response = TestQuery.schema.execute(""" 
            mutation X{
                manageIntent(action : "PUT", options : {parent : "222",name : "myintent", id : "i1", description : "xxxx"}){
                    intent{
                        name,
                        id
                    }
                }
            }
        """)

        response = TestQuery.schema.execute("""
        {
            intent (id:"i1"){
                name,
                id
            }
        }
        """)

        self.assertEqual(response.data["intent"]["name"], "myintent", "retrieved intent")

        response = TestQuery.schema.execute("""{
            bot(id:"222"){
                name,
                description,
                intents {
                    name, 
                    description
                }
            }
        }""")
        print "!!", response.errors
        print "!!!", response.data["bot"]["intents"]
        self.assertEqual(response.data["bot"]["intents"][0]["name"], "myintent", "retrieved intent")


        response = TestQuery.schema.execute("""
        mutation X{
            manageRule(action : "PUT", options : {id: "r1", name : "hello",parent : "i1", replacements: "hi;hello"}){
                rule {
                    id
                }
            }
        }
        """)

        print ".................",response.errors
        rule = Models.Rule.findById("r1")
        self.assertEqual(rule["id"],"r1","right rule id")

        response = TestQuery.schema.execute("""{
                    rule(id:"r1"){
                        name,
                        description,
                        replacements
                    }
                }""")
        print "////", response.data
        self.assertEqual(response.data["rule"]["replacements"], "hi;hello", "right replacements")
