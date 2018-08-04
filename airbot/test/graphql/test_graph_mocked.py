import pprint
import json
import graphene
import unittest
from api.query import Query
from api.mock import DBMock
from api.store import StoreProxy
from api.mutation import Mutation

class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        StoreProxy.store(DBMock)
        cls.schema = graphene.Schema(query=Query, mutation=Mutation)

    def test_bot_api(self):
        response = TestQuery.schema.execute("""
        {
                bot (id:"1") {
                    id
                    name
                    description
                }
        }
        """)
        b = dict(response.data["bot"])
        self.assertEqual(b["id"], "1", "found bot 1")

        response = TestQuery.schema.execute("""
                {
                        bots  {
                            id
                            name
                            description
                        }
                }
                """)
        b = response.data["bots"]
        self.assertEqual(len(b), 1, "one bot found")

        response = TestQuery.schema.execute("""
                        {
                                bots  {
                                    id
                                    name
                                    description
                                    entities {
                                        name
                                        description
                                        variables {
                                            name
                                        }
                                    }
                                    intents{
                                        name 
                                        description 
                                        rules {
                                            name
                                        }
                                    }
                                }
                        }
                        """)
        b = response.data["bots"]
        self.assertEqual(len(b), 1, "one bot found")

        response = TestQuery.schema.execute(""" 
            mutation X{
                manageBot (action : "PUT", options : {name : "created", id : "222", description : "xxxx"}){
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

        self.assertEqual(len(DBMock.bots.keys()), 2, "bot added")

    def test_intent_api(self):
        response = TestQuery.schema.execute("""
        {
            intent (id:"i1") {
                name ,
                description,
                rules {
                    name
                }
            }
        } """)

        response = TestQuery.schema.execute(""" 
                    mutation X{
                        manageIntent (action : "PUT", options : {parent : "1",name : "createdintent", id : "i2", description : "xxxx"}){
                            intent{
                                name , 
                                description
                            }
                        }
                    }
                """)
        self.assertEqual(len(DBMock.intents.keys()), 2, "intent added")

        response = TestQuery.schema.execute("""
                    {
                        bot (id:"1"){
                            name ,
                            description,
                            intents{
                                id,
                                parent, 
                                name
                                rules{
                                    name,
                                    parent
                                }
                            }
                        }
                    }
                    """)
        self.assertEqual(len(response.data["bot"]["intents"]), 2, "two intents found")

    def test_entity_api(self):
        response = TestQuery.schema.execute("""
        {
            entity (id:"e1") {
                name ,
                description,
                variables{
                    name
                }
            }
        } """)

        response = TestQuery.schema.execute(""" 
                    mutation X{
                        manageEntity(action : "PUT", options : {parent : "1",name : "createdentity", id : "e2", description : "xxxx"}){
                            entity{
                                name , 
                                description
                            }
                        }
                    }
                """)
        print response.errors
        self.assertEqual(len(DBMock.entities.keys()), 2, "entity added")

        response = TestQuery.schema.execute("""
                {
                    bot (id:"1"){
                        name ,
                        description,
                        entities{
                            id,
                            parent, 
                            name
                            variables {
                                name,
                                parent
                            }
                        }

                    }
                }
                """)
        self.assertEqual(len(response.data["bot"]["entities"]),2, "two entities found")

    def test_variable_api(self):
        response = TestQuery.schema.execute("""
        {
            variable (id:"v1") {
                name ,
                description,
                field
            }
        } """)

        response = TestQuery.schema.execute(""" 
                    mutation X{
                        manageVariable(action : "PUT", options : {parent : "e1",name : "createdvariable", id : "v2", description : "xxxx",field  : "field2"}){
                            variable{
                                name , 
                                description,
                                field
                            }
                        }
                    }
                """)
        print "WWW", response.errors
        self.assertEqual(len(DBMock.variables.keys()), 2, "variable added")

        response = TestQuery.schema.execute("""
        {
            entity (id:"e1"){
                name ,
                description,
                variables {
                    id,
                    parent, 
                    name,
                    field
                }
                
            }
        }
        """)

        self.assertEqual(len(response.data["entity"]["variables"]), 2, "2 variables returned ")

        def test_rule_api(self):
            response = TestQuery.schema.execute("""
            {
                rule (id:"r1") {
                    name ,
                    description
                }
            } """)

            response = TestQuery.schema.execute(""" 
                        mutation X{
                            manageRule(action : "PUT", options : {parent : "i1",name : "createdrule", id : "r2", description : "xxxx",replacements: "xxx"}){
                                rule{
                                    name , 
                                    description,
                                    replacements
                                }
                            }
                        }
                    """)
            print "XXX", response.errors
            self.assertEqual(len(DBMock.rules.keys()), 2, "rule added")

    def test_variable_api(self):
        response = TestQuery.schema.execute("""
        {
            variable (id:"v1") {
                name ,
                description,
                field
            }
        } """)

        response = TestQuery.schema.execute(""" 
                    mutation X{
                        manageVariable(action : "PUT", options : {parent : "e1",name : "createdvariable", id : "v2", description : "xxxx",field  : "field2"}){
                            variable{
                                name , 
                                description,
                                field
                            }
                        }
                    }
                """)
        print "WWW", response.errors
        self.assertEqual(len(DBMock.variables.keys()), 2, "variable added")

        response = TestQuery.schema.execute("""
        {
            entity (id:"e1"){
                name ,
                description,
                variables {
                    id,
                    parent, 
                    name,
                    field
                }

            }
        }
        """)

        self.assertEqual(len(response.data["entity"]["variables"]), 2, "2 variables returned ")

    def test_rule_api(self):
        response = TestQuery.schema.execute("""
        {
            rule (id:"r1") {
                name ,
                description
            }
        } """)

        response = TestQuery.schema.execute(""" 
                    mutation X{
                        manageRule(action : "PUT", options : {parent : "i1",name : "createdrule", id : "r2", description : "xxxx",replacements: "xxx"}){
                            rule{
                                name , 
                                description,
                                replacements
                            }
                        }
                    }
                """)
        print "XXX", response.errors
        self.assertEqual(len(DBMock.rules.keys()), 2, "rule added")