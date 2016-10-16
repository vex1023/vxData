# encoding=utf-8

import unittest
import bottle
import logging
from vxData.client import API
from vxUtils.PrettyLogger import add_console_logger

add_console_logger(logging.getLogger('test_vxData'), 'DEBUG')
logger = logging.getLogger('test_vxData')


class vxDataCase(unittest.TestCase):
    def setUp(self):
        app = bottle.Bottle()

        @app.get('/test/')
        def helloworld():
            body = bottle.request.body
            logger.info('hello world: %s' % body)
            return {'hello': {
                'columns1': body,
                'columns2': 'end:w',
            }}

    def test_API(self):
        api = API('http://127.0.0.1:8080/test/', 'this is a test', 'hello', ['columns1', 'columns2'])
        logger.info(api(symbols='sz150023', start='1900-01-01', end='2000-01-01').result)


if __name__ == '__main__':
    unittest.main()
