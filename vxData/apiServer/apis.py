# endcoding = utf-8
'''
author :  vex1023
email : vex1023@qq.com

这里是所有的API定义中心
'''
import pandas as pd
import numpy as np
import time
import requests
from vxData.apiServer import APIServer

_MAX_LIST = 800

_SINA_STOCK_KEYS = [
    "name", "open", "yclose", "lasttrade", "high", "low", "bid", "ask",
    "volume", "amount", "bid1_m", "bid1_p", "bid2_m", "bid2_p", "bid3_m",
    "bid3_p", "bid4_m", "bid4_p", "bid5_m", "bid5_p", "ask1_m", "ask1_p",
    "ask2_m", "ask2_p", "ask3_m", "ask3_p", "ask4_m", "ask4_p", "ask5_m",
    "ask5_p", "date", "time", "status"]

server = APIServer()


@server.handler('hq')
def hq(context, params):
    '''获取实时行情接口'''
    symbols = params.get('list', '').split(',')

    url = 'http://hq.sinajs.cn/?rn=%d&list=' % int(time.time())

    urls = [url + ','.join(symbols[i:i + _MAX_LIST]) \
            for i in range(0, len(symbols), _MAX_LIST)]

    respones = [requests.get(url) for url in urls]
    data = list()
    for r in respones:
        lines = r.text.splitlines()
        for line in lines:
            d = line.split('"')[1].split(',')
            # 如果格式不正确,则返回nan
            if len(d) != len(_SINA_STOCK_KEYS):
                d = [np.nan] * len(_SINA_STOCK_KEYS)
            data.append(d)
    df = pd.DataFrame(data, index=symbols, columns=_SINA_STOCK_KEYS, dtype='float')
    df.index.name = 'symbol'
    df.sort_index()
    if 'volume' in _SINA_STOCK_KEYS and 'lasttrade' in _SINA_STOCK_KEYS and 'yclose' in _SINA_STOCK_KEYS:
        df.loc[df.volume == 0, 'lasttrade'] = df['yclose']
    df = df.T
    return df.to_json(double_precision=4, force_ascii=False)
