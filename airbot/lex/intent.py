import pprint
import tracery
from tracery.modifiers import base_english
from slot import Slot, SlotSource
from db.db import Db
import re
from jinja2 import Template


class UnknownMode(Exception):
    pass


class UnknownRuleType(Exception):
    pass


class Intent:
    """
    @class Intent
    Represents an intent
    Args :
        name : string
            the name of the intent
        description : string
            intent description
    """
    ANNOTATION = re.compile("(?P<annotation>@\w+(\.\w+)?)", re.M)

    def __init__(self, name, description=""):
        self.name = name
        self.description = ""
        self.slots = {}
        self.rules = {
            "questions": {},
            "answers": {},
            "clarifications": {},
            "followups": {}
        }

    def get_slots(self):
        """  Get the intent slots
        Returns : list
            A list of name,values dictionaries comprising slot data
        """
        return [{"name": slotname, "values": self.slots[slotname].fetchall()} for slotname in self.slots.keys()]

    def update_rules(self, key, rules):
        """ Update this intent rules
        Args:
            key  :string
                one of 'questions', 'answers', 'followups', 'clarifications'
            rules : dict
                A dictionary of tracery rules
            sql : string, optional
                an sql template to process the intent
        Returns : Intent
            Returns self
        """
        if key not in self.rules.keys():
            raise UnknownRuleType(key)
        self.rules[key].update(rules)
        return self

    def grammar(self, rules, mode="lex"):
        """ Builds a tracery grammar from the provided set of rules
        Args :
            mode : string, defaults to 'lex'
                if lex mode, slots names are replaced by {slotname} and will not be included in the utterance generation process
                if tracery mode, slots are replaced by #slotname# and will generate values in the utterrances generation process
        Returns  : tracery.Grammar
            A tracery grammar
        """
        if mode == "lex":
            grammar = tracery.Grammar(rules)
        elif mode == "tracery":
            _rules = self.lex_intent_to_tracery_rules(rules)
            grammar = tracery.Grammar(_rules)
        else:
            raise UnknownMode(mode)

        grammar.add_modifiers(base_english)
        return grammar

    def add_slot(self, alias, slot):
        """ Adds a slot to this intent
            Args :
                alias : string
                    the name of the slot as used in the rules
                slot : SlotSource
                    the values source for this slot
            Returns  : Intent
                Returns self
        """
        print "adding slot", alias
        s = slot()
        self.slots[alias] = s
        self.rules["questions"][alias] = s.fetchall()
        return self

    def lex_intent_to_tracery_rules(self, rules):
        """ Turns the input rules to tracery rules, effectively replacing @something with #something#"
        so that slots can generate values

        Returns  : dict
            A set of rules with @\w  replaced by #\w#
        """

        new_rules = {}
        for r in rules:
            new_rules[r] = []
            for item in rules[r]:
                new_rules[r].append(self.annotated_to_tracery(item))
        return new_rules

    def generate_utterances(self, key, origin="origin", mode="lex", all=True):
        """ Generate all utterances for an origin in tracery or lex mode for the provided
        set of generative rules
        Args :
            origin : string
                the rule to expand
            mode : string
                if set to 'lex', @something will be replaced by {something} as a slot ref in lex
                if set to 'tracery', @something will be replaced by #something# as a slot generators
        """
        if not all:
            # generate one utterance
            return Intent \
                .annotated_to_lex(self.grammar(mode=mode, rules=self.rules[key]).flatten("#%(origin)s#" % vars())) \
                .strip()
        else:
            # generate all utterances
            already = 0
            items = []
            while already < 100:
                item = self.generate_utterances(key=key, origin=origin, mode=mode, all=False)
                if item not in items:
                    items.append(item)
                else:
                    already += 1
            return items

    @classmethod
    def annotated_to_tracery(cls, aninput):
        """ Takes an input text and replaces any occurence of @something with #something#
        Args
            aninput : string
                input text
        Returns : string
            tracery compatible generative rule
        """
        m = cls.ANNOTATION.findall(aninput)
        if m is not None:
            groups = cls.ANNOTATION.findall(aninput)
            for g in groups:
                n = g[0]
                nwithout = n.replace('@', '')
                aninput = aninput.replace(n, "#%(nwithout)s#" % vars())
        return aninput

    @classmethod
    def annotated_to_lex(cls, aninput):
        """ Takes an input text and replaces any occurence of @something with {something}
        Args
            aninput : string
                input text
        Returns : string
            tracery compatible generative rule
        """
        m = cls.ANNOTATION.findall(aninput)
        # print "??", aninput, m
        if m is not None:
            groups = cls.ANNOTATION.findall(aninput)
            for g in groups:
                n = g[0]
                nwithout = n.replace('@', '')
                aninput = aninput.replace(n, "{%(nwithout)s}" % vars())
        return aninput

    def run_sql(self, slots={}):
        """ Runs the sql provided for this intent
        Args :
            slots : dict
                the slot captured by lex from an input
        Returns : list
            The sql result
        """
        for slot in self.slots.keys():
            slots.update({slot: self.slots[slot].fetchall()})
        template = Template(tpl)
        body = template.render(slots)
        m = Intent.ANNOTATION.search(body)
        if m is not None:
            groups = Intent.ANNOTATION.findall(body)
            for g in groups:
                n = g[0]
                nwithoutannotation = n.replace("@", "")

                body = body.replace(n, slots[n] if n in slots.keys() else '')
        return body

    def configure_answer(self, sql, rules, options):
        self.sql = sql
        self.options = options
        self.update_rules(key="answers", rules=rules)

    def answer(self, slots):
        self.run_sql(tpl=self.sql, slots=slots)


def example():
    i = Intent("example")

    class LikeSlot(SlotSource):
        def _read(self):
            return [
                "music", "jazz", "sport", "musicals", "broadway", "theatre"
            ]

    class CustomerSlot(SlotSource):
        def _read(self):
            return [
                "customer", "user", "people", "person", "individual"
            ]

    class UserCitySlot(SlotSource):
        def _read(self):
            return Db.get("dev").sql("select distinct city as city from USERS", mode=Db.MODES.LIST)

    i.add_slot("usercity", UserCitySlot)
    i.add_slot("customerlabel", CustomerSlot)
    i.add_slot("preferences", LikeSlot)
    i.update_rules(
        key="questions",
        rules={
            "cityfilter": [
                "#in# @usercity"
            ],
            "preferencefilter": [
                "#like# @preferences"
            ],
            "filter": [
                "",
                "",
                "#cityfilter# and #preferencefilter#",
                "#cityfilter#",
                "#preferencefilter#",
                "#preferencefilter#  and #cityfilter#",
            ],
            "total": ["total number of", "overall number of", "total number of"],
            "action": ["say", "tell #me#", "get #me#", "show #me#"],
            "origin": [
                "#please#  how many @customerlabel do we have #filter# ",
                "#please#  the number of  @customerlabel  #filter#",
                "#please#  what's the number of  @customerlabel #filter#",
                "#please#  what's the #total#   @customerlabel #filter#"
            ],
            "me": ["", "me"],
            "like": ["into", "who like", "who love", "loving", "who do", "doing"],
            "please": ["", "please #action#", "can you #action#", "is it possible you #action#"],
            "in": ["living in", "located in", "in", "within area of", "around"]
        }
    )
    return i


if __name__ == "__main__":
    i = example()
    sql = """  select 
                *
            from 
                user 
            where 
                city = nvl('@usercity',city)    and
                case 
                when '@preference' is  not null then
                    case
                        {% for pref in  preferences  %}
                            when '@preference' = '{{pref}}' then like{{pref}}
                        {% endfor %}                        
                            else true
                    end
                else true
                end """
    # print "?", i.sql(sql,slots = {'@usercity' : 'madrid', '@preference' :  'music'})

    # print pprint.pformat(i.rules, indent=4)
    # print pprint.pformat(i.lex_intent_to_tracery_rules())
    for idx, u in enumerate(i.generate_utterances(key="questions", origin="origin", mode="lex")):
        print "%(idx)s." % vars(), u

    i.configure_answer(
        sql=sql,
        rules={
            "waiter": ["ok, let me find out", "a moment please", "i'm checking", "won't be long"],
            "intro": ["ok", "i got it", "here we go"],
            "thereis": ["i can tell", "i found", "there are", " "],
            "answer": ["#intro# #thereis# @{} in ?usercity #like# ##"],
        })