from airbot import resolvers
from airbot import utils
import unittest
from grapher import App
import pprint


OPENID_CONFIG = {
    'ISSUER_URL': 'https://dev-545796.oktapreview.com',
    'CLIENT_ID': '0oafvba1nlTwOqPN40h7',
    'REDIRECT_URI': 'http://locahost/implicit/callback'
}


class TestEndToEnd(unittest.TestCase) :

    @classmethod
    def get_claim(cls):
        claim = utils.OpenidHelper.get_claim(OPENID_CONFIG, "moshir.mikael@gmail.com","Azerty1!")
        return claim

    def test_entity_api(self):
        event = {
            "identity": {"claims" : TestEndToEnd.get_claim()},
            "field" : "createBot",
            "path" : "Mutation/createBot",
            "arguments" : {
                "accountid"  : "testaccount",
                "input" : {
                    "name" : "mytestbot",
                    "description" :"test"
                }
            }
        }
        self.assertTrue(True)
        b= App.handler(event,{})
        print b

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "createEntity",
            "path": "Mutation/createEntity",
            "arguments": {
                "botid": b["ID"],
                "input": {
                    "name": "mytestbot",
                    "description": "test"
                }
            }
        }

        e = App.handler(event, {})
        print e

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "createEntity",
            "path": "Mutation/createEntity",
            "arguments": {
                "botid": b["ID"],
                "input": {
                    "name": "mytestbot",
                    "description": "test"
                }
            }
        }

        w= App.handler(event,{})
        print w

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "getEntity",
            "path": "Query/getEntity",
            "arguments": {
                "entityid": w["ID"],
            }
        }

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "updateEntity",
            "path": "Mutation/updateEntity",
            "arguments": {
                "entityid": w["ID"],
                "input": {
                    "tags" : "x,y,z"
                }
            }
        }
        u = App.handler(event, {})
        print "U = ", u

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "listEntities",
            "path": "Query/listentities",
            "arguments": {
                "botid": b["ID"]
            }
        }
        l = App.handler(event, {})
        print "entities = ",l

        event = {
            "identity": {"claims": TestEndToEnd.get_claim()},
            "field": "deleteEntity",
            "path": "Mutation/deleteEntity",
            "arguments": {
                "entityid": w["ID"]
            }
        }
        d = App.handler(event, {})
        print "D = ", d



if __name__ == "__main__" :
    unittest.main(verbosity=2)

