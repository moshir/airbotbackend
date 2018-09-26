from airbot.model.botitem  import Item
from grapher import App
from genid import ID
from airbot import errors
import pprint
from factory import base_factory, list_children_factory


base_factory(objecttype="rule",parentobjecttype="intent",parentidentitifier="intentid",identifier="ruleid")

