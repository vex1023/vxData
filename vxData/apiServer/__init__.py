# endcoding = utf-8
'''
author : 
email : 
'''

import bottle
import records

api = bottle.Bottle()


@api.get('/apis')
def get_apis():
    return