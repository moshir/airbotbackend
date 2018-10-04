import os
from airbot import resolvers
from grapher import App


def handler(event, context) :
    x=  App.handler(event, context)
    print x
    return x

