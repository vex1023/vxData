# endcoding = utf-8
'''
author : vex1023
email : vex1023@qq.com

API 接口类的基础

'''

import logging
import requests
import pandas as pd
import demjson as json

from vxUtils.decorator import retry, timeout, threads
from vxUtils.PrettyLogger import add_console_logger

logger = logging.getLogger('API')
add_console_logger(logger, 'debug')


class API():

    def __init__(self, url, description, index,columns):
        self._url = url
        self._description = description
        self._index = index
        self._columns = columns

    @threads(5)
    @retry(5)
    #@timeout(2)
    def __call__(self, session=None, **kwargs):
        if session is None:
            session = requests.session()

        body = json.encode(kwargs)

        logger.debug('call body: %s' % body)
        r = session.get(self._url, data=body)
        logger.debug('return: %s' % r.text)

        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data=data, index=self._index, columns=self._columns)



