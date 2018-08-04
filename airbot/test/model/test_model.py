import unittest
from server.databot.model.models import Models


class ModelTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_bot(self):
        items = Models.Bot.list()
        for item in items  :
            Models.Bot.delete(item["id"])
        items = Models.Bot.list()
        self.assertEqual(len(items), 0, "all items deleted")
        Models.Bot.put({
            "id" : "1",
            "name" : "testbot",
            "description" : "testbot"
        })
        testbot = Models.Bot.findById("1")
        createdat = testbot["createdat"]
        self.assertEquals(testbot["description"],"testbot","correct description")
        self.assertTrue("createdat" in testbot.keys(), "createdat has been added")
        self.assertTrue("updatedat" not in testbot.keys(), "updatedat has not added")
        Models.Bot.put({
            "id" : "1",
            "name" : "testbot",
            "description" : "more than a testbot"
        })
        testbot = Models.Bot.findById("1")
        self.assertEquals(testbot["description"],"more than a testbot","updated description")
        self.assertEquals(testbot["createdat"],createdat,"createdat not changed")
        self.assertTrue("updatedat" in testbot.keys(), "updatedat has been added")


        items = Models.Bot.findByName("testbot")
        self.assertEqual(len(items),1,"found one")

        items = Models.Bot.findByName("an imaginary bot ")
        self.assertEqual(0, len(items) ,"not found")

        items = Models.Bot.list()
        self.assertEqual(len(items), 1, "one item")
        for item in items  :
            Models.Bot.delete(item["id"])
        items = Models.Bot.list()
        self.assertEqual(len(items), 0, "all items cleared")


    def test_entity(self):
        items = Models.Entity.list()
        for item in items  :
            Models.Entity.delete(item["id"])
        items = Models.Entity.list()
        self.assertEqual(len(items), 0, "all items deleted")
        Models.Bot.put({
            "id" : "1",
            "name" : "testbot",
            "description" : "testing bot"
        })
        Models.Entity.put({
            "parent" : "1",
            "id" : "e1",
            "name" : "mytable",
            "description" : "a test entity"
        })
        entity= Models.Entity.findById("e1")
        createdat = entity["createdat"]
        self.assertEquals(entity["description"],"a test entity","correct description")
        self.assertTrue("createdat" in entity.keys(), "createdat has been added")
        self.assertTrue("updatedat" not in entity.keys(), "updatedat has not added")
        Models.Entity.put({
            "id" : "e1",
            "parent"  : "1",
            "name" : "mytable",
            "description" : "changed description"
        })
        entity= Models.Entity.findById("e1")
        self.assertEquals(entity["description"],"changed description","updated description")
        self.assertEquals(entity["createdat"],createdat,"createdat not changed")
        self.assertTrue("updatedat" in entity.keys(), "updatedat has been added")


        items = Models.Entity.findByName("mytable")
        self.assertEqual(len(items),1,"found one")

        items = Models.Entity.findByName("an imaginary entity")
        self.assertEqual(0, len(items) ,"not found")
        Models.Entity.put({
            "parent" : "1",
            "id" : "e2",
            "name" : "myothertable",
            "description" : "another test entity"
        })

        items = Models.Entity.list()
        self.assertEqual(len(items), 2, "two items found")

        entities = Models.Bot.get_bot_entities(id="1")
        self.assertEqual(len(entities ), 2, "bot has two entities ")


        Models.Variable.put({
            "parent" : "e1",
            "id" : "v1",
            "name" : "country",
            "field" : "c1"
        })

        variables = Models.Variable.list()
        self.assertEqual(len(variables),1, "one variable found")


        variables = Models.Entity.get_entity_variables("e1")
        self.assertEqual(len(variables),1, "one variable found")

    def test_intent(self):
        items = Models.Intent.list()
        for item in items  :
            Models.Intent.delete(item["id"])
        items = Models.Intent.list()
        self.assertEqual(len(items), 0, "all items deleted")
        Models.Bot.put({
            "id" : "1",
            "name" : "testbot",
            "description" : "testing bot"
        })
        Models.Intent.put({
            "parent" : "1",
            "id" : "i1",
            "name" : "myintent",
            "description" : "a test intent"
        })
        intent = Models.Intent.findById("i1")
        createdat = intent ["createdat"]
        self.assertEquals(intent ["description"],"a test intent","correct description")
        self.assertTrue("createdat" in intent.keys(), "createdat has been added")
        self.assertTrue("updatedat" not in intent.keys(), "updatedat has not added")
        Models.Intent.put({
            "id" : "i1",
            "parent"  : "1",
            "name" : "myintent",
            "description" : "changed description"
        })
        intent= Models.Intent.findById("i1")
        self.assertEquals(intent["description"],"changed description","updated description")
        self.assertEquals(intent["createdat"],createdat,"createdat not changed")
        self.assertTrue("updatedat" in intent.keys(), "updatedat has been added")


        items = Models.Intent.findByName("myintent")
        self.assertEqual(len(items),1,"found one")

        items = Models.Entity.findByName("an imaginary intent")
        self.assertEqual(0, len(items) ,"not found")
        Models.Intent.put({
            "parent" : "1",
            "id" : "i2",
            "name" : "myotherintent",
            "description" : "another test intent"
        })

        items = Models.Intent.list()
        self.assertEqual(len(items), 2, "two items found")

        intents = Models.Bot.get_bot_intents(id="1")
        self.assertEqual(len(intents ), 2, "bot has two intents")



        Models.Rule.put({
            "parent" : "i1",
            "id" : "r1",
            "name" : "intro",
            "replacement" : "hello\nhi\n"
        })

        rules= Models.Rule.list()
        self.assertEqual(len(rules),1, "one rule found")


        rules = Models.Intent.get_intent_rules("i1")
        self.assertEqual(len(rules ),1, "one rule found")


if __name__ == '__main__':
    unittest.main()