# encoding=utf-8

'''
author: vex1023
email: vex1023@qq.com

市场状态的接口

'''

import time
import requests
import json
import numpy as np
import pandas as pd
from random import random
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool as Pool
from vxUtils.decorator import retry

_MAX_SINA_HQ_LIST = 800

_SINA_STOCK_KEYS = [
    "name", "open", "yclose", "lasttrade", "high", "low", "bid", "ask",
    "volume", "amount", "bid1_m", "bid1_p", "bid2_m", "bid2_p", "bid3_m",
    "bid3_p", "bid4_m", "bid4_p", "bid5_m", "bid5_p", "ask1_m", "ask1_p",
    "ask2_m", "ask2_p", "ask3_m", "ask3_p", "ask4_m", "ask4_p", "ask5_m",
    "ask5_p", "date", "time", "status"]

_BAR_URL_TEMPLATE = \
    'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq%s&param=%s,%s,%s-01-01,%s-12-31,640,qfq&r=%s'


class StockExchange():
    def __init__(self, max_worker=5):
        self._status = 'close'
        self._expire_at = 0
        self._thread_pools = Pool(max_worker)

    @property
    def market_status(self):
        now = datetime.now()
        if self._expire_at < now.timestamp():
            self._update_market_status(now)
        return self._status

    @property
    def market_am_open(self):
        now = datetime.now()
        if self._expire_at < now.timestamp():
            self._update_market_status(now)
        return self._market_am_open

    @property
    def market_am_close(self):
        now = datetime.now()
        if self._expire_at < now.timestamp():
            self._update_market_status(now)
        return self._market_am_close

    @property
    def market_fm_open(self):
        now = datetime.now()
        if self._expire_at < now.timestamp():
            self._update_market_status(now)
        return self._market_fm_open

    @property
    def market_fm_close(self):
        now = datetime.now()
        if self._expire_at < now.timestamp():
            self._update_market_status(now)
        return self._market_fm_close

    def _update_market_status(self, now):
        hq = self.hq('sh000001')
        hq_date = hq.loc['sh000001', 'date']
        hq_time = hq.loc['sh000001', 'time']
        hq_datetime = datetime.strptime(hq_date + ' ' + hq_time, '%Y-%m-%d %H:%M:%S')

        self._market_am_open = hq_datetime.replace(hour=9, minute=25, second=0, microsecond=0)
        self._market_am_close = hq_datetime.replace(hour=11, minute=30, second=0, microsecond=0)
        self._market_fm_open = hq_datetime.replace(hour=13, minute=0, second=0, microsecond=0)
        self._market_fm_close = hq_datetime.replace(hour=15, minute=0, second=0, microsecond=0)

        if hq_datetime.date() < now.date():
            self._status = 'close'
            self._expire_at = (self._market_am_open + timedelta(days=1)).timestamp()
        else:
            if hq_datetime < self._market_am_close:
                self._status = 'trading'
                self._expire_at = self._market_am_close.timestamp()
            elif hq_datetime < self._market_fm_open:
                self._status = 'break'
                self._expire_at = self._market_fm_open.timestamp()
            elif hq_datetime < self._market_fm_close:
                self._status = 'trading'
                self._expire_at = self._market_fm_close.timestamp()
            else:
                self._status = 'close'
                self._expire_at = (self._market_am_open + timedelta(days=1)).timestamp()

        return

    def hq(self, *symbols):
        '''行情接口——默认使用新浪的行情接口
           :param symbols: [ 'sz150023','sz150022','sz159915']
           :return: 行情数据
        '''
        _symbols = []
        for s in symbols:
            if isinstance(s, (list, set, tuple)):
                _symbols.extend(s)
            else:
                _symbols.append(s)
        symbols = _symbols

        urls = []
        for i in range(0, len(symbols), _MAX_SINA_HQ_LIST):
            url = 'http://hq.sinajs.cn/?rn=%d&list=' % int(time.time())
            urls.append(url + ','.join(symbols[i:i + _MAX_SINA_HQ_LIST]))

        respones = self._thread_pools.imap(requests.get, urls)
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
        if 'volume' in _SINA_STOCK_KEYS and 'lasttrade' in _SINA_STOCK_KEYS and 'yclose' in _SINA_STOCK_KEYS:
            df.loc[df.volume == 0, 'lasttrade'] = df['yclose']
        return df

    def bar(self, symbol, start='', end='', ktype='D', adjtype='forward'):
        '''
        获取k线的函数
        :param symbol: 证券代码，如: sz150023,sz000001,sh000001
        :param start: 起始日期，datetime or '2016-01-01'
        :param end: 终止日期， datetime or '2016-03-31'
        :param ktype: k线频率, D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
        :param adjtype: 复权调整类型, forward-前复权 afterward-后复权 None-不复权，默认为:forward
        :return: 返回DataFrame
                 index : date
                 columns : [symbol, open, high, low, close, volume]
        '''
        if isinstance(start, str):
            if start == '':
                start = datetime.now().replace(month=1, day=1, hour=0, minute=0)
            else:
                start = datetime.strptime(start, '%Y-%m-%d')
        if isinstance(end, str):
            if end == '':
                end = datetime.now().replace(month=12, day=31, hour=0, minute=0)
            else:
                end = datetime.strptime(end, '%Y-%m-%d')
        ktype = ktype.upper()
        trans_map = {
            'D': 'day',
            'W': 'week',
            'M': 'month'
        }
        ktype = trans_map[ktype]

        data = []
        results = []

        for year in range(start.year, end.year + 1):
            kwars = {
                'year': year,
                'symbol': symbol,
                'ktype': ktype
            }
            results.append(self._thread_pools.apply_async(self._parser_bar, kwds=kwars))

        for result in results:
            result = result.get()
            data.extend(result)

        data = self._thread_pools.map(lambda x: x[:6], data)

        df = pd.DataFrame(data, columns=['date', 'open', 'close', 'high', 'low', 'volume'])
        df = df.set_index('date')
        df['symbol'] = symbol
        df = df.loc[df.index >= start.strftime('%Y-%m-%d')]
        df = df.loc[df.index <= end.strftime('%Y-%m-%d')]
        return df[['symbol', 'open', 'high', 'low', 'close', 'volume']]

    @retry(3)
    def _parser_bar(self, year, symbol, ktype):
        url = _BAR_URL_TEMPLATE % (year, symbol, ktype, year, year, random())
        r = requests.get(url)
        r.raise_for_status()
        d = r.text
        d = d.split('=')[1]
        d = json.loads(d)['data']

        if 'qfq%s' % ktype in d[symbol].keys():
            d = d[symbol]['qfq%s' % ktype]
        else:
            d = d[symbol][ktype]

        return d
