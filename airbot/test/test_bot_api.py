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

    def test_aa_create_account(self):
        print "+-+"*30
        print "CREATION"
        event = {
            "identity": {"claims" : TestEndToEnd.get_claim()},
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

    def test_ab_create_bot(self):
        print "+-+"*30
        print "CREATION"
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
        w= App.handler(event,{})
        print "Creation "
        print pprint.pformat(w)






if __name__ == "__main__" :
    unittest.main(verbosity=2)

