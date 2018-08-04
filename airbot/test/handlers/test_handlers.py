import json
import unittest
from server.handlers import handler
from server.databot.model.models import Models


class LambdaHandlerTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_bot_api(self):
        event = {
            "path": "/bot",
            "httpMethod": "POST",
            "body": json.dumps({
                "id": "handlertest",
                "name": "handlertest",
                "description": "generated",
                "status": "NOT_BUILT"
            })
        }
        response = handler(event, {})
        botitem = Models.BotModel.findById(id="handlertest")
        self.assertEqual(botitem["name"], "handlertest")

        event = {
            "path": "bot/",
            "httpMethod": "GET",
            "body": json.dumps({
            })
        }
        response = handler(event, {})
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 1, "one item returned")


        event = {
            "path": "bot/",
            "httpMethod": "GET",
            "body": json.dumps({
                "id" : "handlertest"
            })
        }
        response = handler(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body["data"]["id"], "handlertest", "returned item")


if __name__ == '__main__':
    unittest.main()
