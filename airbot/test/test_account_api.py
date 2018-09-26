from airbot import resolvers
from airbot import utils
import unittest
from grapher import App
import pprint
from airbot.model.botitem import Item

OPENID_CONFIG = {
    'ISSUER_URL': 'https://dev-545796.oktapreview.com',
    'CLIENT_ID': '0oafvba1nlTwOqPN40h7',
    'REDIRECT_URI': 'http://locahost/implicit/callback'
}


class TestAccount(unittest.TestCase) :

    @classmethod
    def get_claim(cls):
        claim = utils.OpenidHelper.get_claim(OPENID_CONFIG, "moshir.mikael@gmail.com","Azerty2!")
        return claim


    @classmethod
    def get_accountid(cls,user="moshir.mikael@gmail.com"):
        candidates = [c.attribute_values for c in Item.query("account", Item.creator==user)]
        if len(candidates) :
            return candidates[0]["ID"]
        else :
            return None

    @classmethod
    def get_bots(cls,user="moshir.mikael@gmail.com"):
        accountid = cls.get_accountid(user)
        bots = Item.query("bot", filter_condition=Item.parent.__eq__(accountid))
        return [b.attribute_values for b in bots]


    @classmethod
    def get_entities(cls, botid):
        entities = Item.query("entity", filter_condition=Item.parent.__eq__(botid))
        return [e.attribute_values for e in entities]




    @classmethod
    def get_intents(cls, botid):
        intents = Item.query("intent", filter_condition=Item.parent.__eq__(botid))
        return [i.attribute_values for i in intents]


    @classmethod
    def get_entity(cls,user="moshir.mikael@gmail.com"):
        bots = cls.get_bots(user)
        bot = bots[0]
        entities= cls.get_entities(bot["ID"])
        return entities[0]


    @classmethod
    def get_intent(cls,user="moshir.mikael@gmail.com"):
        bots = cls.get_bots(user)
        bot = bots[0]
        intents= cls.get_intents(bot["ID"])
        return intents[0]

    def test_aa_clean(self):
        event = {
            "identity": {"claims" : TestAccount.get_claim()},
            "field" : "listMyAccounts",
            "path" : "Query/listMyAccounts",
            "arguments" : {}
        }
        accounts = App.handler(event, {})

        if type(accounts) == type(["a", "list"]) :
            print "Found", len(accounts), "accounts"
            print accounts
            for accountdoc in accounts :
                a = Item.get('account',accountdoc["ID"])
                a.delete()

            x = App.handler(event, {})
            self.assertTrue(len(x)==0)
        else:
            self.assertTrue(True, "no accounts")


    def test_ab_create_account(self):
        print "+-+"*30
        print "CREATION"
        event = {
            "identity": {"claims" : TestAccount.get_claim()},
            "field" : "createAccount",
            "path" : "Mutation/createAccount",
            "arguments" : {
                "input" : {
                    "name" : "testaccount"
                }
            }
        }
        self.assertTrue(True)
        w= App.handler(event,{})
        print "Creation "
        print pprint.pformat(w)


    def test_ac_list_myaccount(self):
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listMyAccounts",
            "path": "Query/listMyAccounts",
            "arguments": {}
        }
        x = App.handler(event, {})
        for user in x :
            print user


    def test_ad_invite(self):
        accountid = TestAccount.get_accountid()
        print "accountid = ,",accountid
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "inviteUser",
            "path": "Mutation/inviteUser",
            "arguments": {
                "accountid" : accountid,
                "email" : "jennifergouin@gmail.com",
            }
        }
        x = App.handler(event, {})
        print x


    def test_ba_create_bot(self):
        accountid = TestAccount.get_accountid()
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "createBot",
            "path": "Mutation/createBot",
            "arguments": {
                "accountid": accountid,
                "input": {
                    "name": "mytestbot",
                    "description": "test"
                }
            }
        }
        self.assertTrue(True)
        w = App.handler(event, {})
        print "Creation "
        print pprint.pformat(w)


    def test_bb_list_bots(self):
        accountid = TestAccount.get_accountid()
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listBots",
            "path": "Account/listBots",
            "arguments" : {},
            "source": {
                "ID": accountid
            }
        }

        r = App.handler(event, {})
        print r
        print pprint.pformat(r)
        self.assertTrue(len(r) == 1)


    def test_bc_get_bot(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "getBot",
            "path": "Query/getBot",
            "arguments": {
                "botid" :bot["ID"]
            }
        }
        r = App.handler(event, {})
        self.assertEqual(r["name"],bot["name"])



    def test_bd_update_bot(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "updateBot",
            "path": "Mutation/updateBot",
            "arguments": {
                "botid" :bot["ID"],
                "input" : {
                    "description" : "updated"
                }
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["description"],"updated")

    def test_be_list_bots_with_search(self):
        accountid = TestAccount.get_accountid()
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listBots",
            "path": "Account/listBots",
            "arguments": {
                "options" : {"search" : "updated"}
            },
            "source": {
                "ID" :accountid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(len(r),1)



    def test_ca_create_entity(self):
        bots = TestAccount.get_bots()
        bot = bots[0]
        print "??", bot
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "createEntity",
            "path": "Mutation/createEntity",
            "arguments": {
                "botid": botid ,
                "input": {
                    "name": "mytestentity",
                    "description": "test"
                }
            }
        }
        self.assertTrue(True)
        w = App.handler(event, {})
        print "Creation "
        print pprint.pformat(w)


    def test_cb_list_entities(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listEntities",
            "path": "Bot/listEntities",
            "arguments" : {},
            "source": {
                "ID": botid
            }
        }

        r = App.handler(event, {})
        print r
        print pprint.pformat(r)
        self.assertTrue(len(r) == 1)


    def test_cc_get_entity(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        entities = TestAccount.get_entities(botid)
        entity = entities[0]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "getEntity",
            "path": "Query/getEntity",
            "arguments": {
                "entityid" :entity["ID"]
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["name"],entity["name"])



    def test_cd_update_entity(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bots[0]["ID"]
        entities = TestAccount.get_entities(botid)
        entity = entities[0]
        entityid = entity["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "updateEntity",
            "path": "Mutation/updateEntity",
            "arguments": {
                "entityid" :entityid,
                "input" : {
                    "description" : "updated"
                }
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["description"],"updated")

    def test_ce_list_entities_with_search(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listEntities",
            "path": "Bot/listEntities",
            "arguments": {
                "options" : {"search" : "updated"}
            },
            "source": {
                "ID" :botid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(len(r),1)

    def test_da_create_intent(self):
        bots = TestAccount.get_bots()
        bot = bots[0]
        print "??", bot
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "createIntent",
            "path": "Mutation/createIntent",
            "arguments": {
                "botid": botid ,
                "input": {
                    "name": "mytestintent",
                    "description": "test"
                }
            }
        }
        self.assertTrue(True)
        w = App.handler(event, {})
        print pprint.pformat(w)


    def test_db_list_intents(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listIntents",
            "path": "Bot/listIntents",
            "arguments" : {},
            "source": {
                "ID": botid
            }
        }

        r = App.handler(event, {})
        print r
        print pprint.pformat(r)
        self.assertTrue(len(r) == 1)


    def test_dc_get_intent(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        intents = TestAccount.get_intents(botid)
        intent= intents[0]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "getIntent",
            "path": "Query/getIntent",
            "arguments": {
                "intentid" :intent["ID"]
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["name"],intent["name"])



    def test_dd_update_intent(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bots[0]["ID"]
        intents = TestAccount.get_intents(botid)
        intent= intents[0]
        intentid= intent["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "updateIntent",
            "path": "Mutation/updateIntent",
            "arguments": {
                "intentid" :intentid,
                "input" : {
                    "description" : "updated"
                }
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["description"],"updated")

    def test_de_list_intents_with_search(self):
        accountid = TestAccount.get_accountid()
        bots = TestAccount.get_bots()
        bot = bots[0]
        botid = bot["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listIntents",
            "path": "Bot/listIntents",
            "arguments": {
                "options" : {"search" : "updated"}
            },
            "source": {
                "ID" :botid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(len(r),1)










    def test_ea_create_variable(self):
        entity = TestAccount.get_entity()
        entityid = entity["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "createVariable",
            "path": "Mutation/createVariable",
            "arguments": {
                "entityid": entityid ,
                "input": {
                    "name": "mytestvariable",
                    "description": "test"
                }
            }
        }
        self.assertTrue(True)
        w = App.handler(event, {})
        print pprint.pformat(w)


    def test_eb_list_variables(self):
        entity = TestAccount.get_entity()
        entityid = entity["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listVariables",
            "path": "Entity/listVariables",
            "arguments" : {},
            "source": {
                "ID": entityid
            }
        }

        r = App.handler(event, {})
        print r
        print pprint.pformat(r)
        self.assertTrue(len(r) == 1)


    def test_ec_get_variable(self):
        entity = TestAccount.get_entity()
        entityid = entity["ID"]
        candidates = [c.attribute_values for c in Item.query("variable", Item.parent.__eq__(entityid))]
        variable = candidates[0]
        variableid = variable["ID"]
        print ">>",variableid
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "getVariable",
            "path": "Query/getVariable",
            "arguments": {
                "variableid" :variableid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["name"],variable["name"])



    def test_ed_update_variable(self):
        entity = TestAccount.get_entity()
        entityid = entity["ID"]
        candidates = [c.attribute_values for c in Item.query("variable", Item.parent.__eq__(entityid))]
        variable = candidates[0]
        variableid = variable["ID"]
        print ">>",variableid
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "updateVariable",
            "path": "Mutation/updateVariable",
            "arguments": {
                "variableid" :variableid,
                "input" : {
                    "description" : "updated"
                }
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["description"],"updated")

    def test_ee_list_variables_with_search(self):
        entity = TestAccount.get_entity()
        entityid = entity["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listVariables",
            "path": "Entity/listVariables",
            "arguments": {
                "options" : {"search" : "updated"}
            },
            "source": {
                "ID" :entityid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(len(r),1)




    def test_fa_create_rule(self):
        intent = TestAccount.get_intent()
        intentid = intent["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "createRule",
            "path": "Mutation/createRule",
            "arguments": {
                "intentid": intentid ,
                "input": {
                    "name": "mytestrule",
                    "description": "test"
                }
            }
        }
        self.assertTrue(True)
        w = App.handler(event, {})
        print pprint.pformat(w)


    def test_fb_list_rules(self):
        intent = TestAccount.get_intent()
        intentid = intent ["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listRules",
            "path": "Intent/listRules",
            "arguments" : {},
            "source": {
                "ID": intentid
            }
        }

        r = App.handler(event, {})
        print r
        print pprint.pformat(r)
        self.assertTrue(len(r) == 1)


    def test_fc_get_rule(self):
        intent = TestAccount.get_intent()
        intentid = intent ["ID"]
        candidates = [c.attribute_values for c in Item.query("rule", Item.parent.__eq__(intentid))]
        rule = candidates[0]
        ruleid = rule["ID"]
        print ">>",ruleid
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "getRule",
            "path": "Query/getRule",
            "arguments": {
                "ruleid" :ruleid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["name"],rule["name"])



    def test_fd_update_rule(self):
        intent = TestAccount.get_intent()
        intentid = intent ["ID"]
        candidates = [c.attribute_values for c in Item.query("rule", Item.parent.__eq__(intentid))]
        rule = candidates[0]
        ruleid = rule["ID"]
        print ">>",ruleid
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "updateRule",
            "path": "Mutation/updateRule",
            "arguments": {
                "ruleid" :ruleid,
                "input" : {
                    "description" : "updated"
                }
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(r["description"],"updated")

    def test_fe_list_rules_with_search(self):
        intent = TestAccount.get_intent()
        intentid= intent["ID"]
        event = {
            "identity": {"claims": TestAccount.get_claim()},
            "field": "listRules",
            "path": "Entity/listRules",
            "arguments": {
                "options" : {"search" : "updated"}
            },
            "source": {
                "ID" :intentid
            }
        }
        r = App.handler(event, {})
        print r
        self.assertEqual(len(r),1)




if __name__ == "__main__" :
    unittest.main(verbosity=2)

