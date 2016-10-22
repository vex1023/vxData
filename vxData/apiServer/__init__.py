# endcoding = utf-8
'''
author : 
email : 
'''

import logging
from bottle import Bottle, request
from functools import wraps

from vxData.exception import InternalError, NotSupportError, APIError
from vxUtils.PrettyLogger import add_console_logger

logger = logging.getLogger('vxData.apiServer')
add_console_logger(logger, 'DEBUG')


class APIServer():
    def __init__(self, prefix='/'):
        # route的prefix
        self.prefix = prefix
        # api 的handler 存放地方
        self._handlers = {}

    def run(self, *args, **kwargs):

        # 生成一个web app
        app = Bottle()

        @app.get(self.prefix + 'announce')
        def announce():
            '''这是公告'''
            apis = []
            for api_name, handler in self._handlers.items():
                apis.append(
                    {
                        'api_name': api_name,
                        'description': handler.__doc__
                    }
                )
            return {'apis': apis}

        @app.get(self.prefix + 'api/:api_name')
        def api_methods(api_name):
            try:
                handler = self.get_handler(api_name)
                if callable(handler):
                    return handler(self, request.query)
                else:
                    raise InternalError('unkown api_name: %s' % api_name)
            except APIError as apierr:
                logger.warning(apierr)
                return str(apierr)
            except Exception as err:
                logger.warning(err)
                return str(InternalError(err))

        # 运行 app
        try:
            app.run(*args, **kwargs)
        except Exception as err:
            logger.warning('api Server is shutdown: %s' % err)

    def get_handler(self, api_name):
        return self._handlers.get(api_name, self.default_handler)

    def default_handler(self, *args, **kwargs):
        '''缺省的返回值'''
        raise NotSupportError('check available apis in /announce')

    def handler(self, api_name):
        '''
        这个是api handler的修饰器
        @apiServer.handler('hq')
        def hq(context, params):
            return dict
        '''

        def deco_handler(fn):
            logger.info('add handler for : %s' % api_name)
            self._handlers[api_name] = fn
            print(self._handlers)

            @wraps(fn)
            def wrapped(params):
                return fn(context=self, params=params)

            return wrapped

        return deco_handler


from .apis import *
