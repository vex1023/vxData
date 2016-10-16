# endcoding = utf-8
'''
author :  vex1023
email : vex1023@qq.com

这里是所有的API定义中心
'''

from vxData.exception import InternalError

class apiServer():
    def __init__(self, prefix='/'):
        self.app = bottle.Bottle()
        self.prefix = prefix
        self._handlers = {}

    @self.app.get(self.prefix+'methods')
    def api_methods(self):
        methods = {}
        for key, value in self._handlers.items():
            if callable(value):
                methods[key] = value.__doc__
        return methods



class apiHandler():
    def __init__(self,  description):
        self._path = path
        self._handler = handler
        self._description = description
        self._index = index
        self._columns = columns

    def handle(self, records, **kwargs):

        raise NotImplementedError('There is not handle')
