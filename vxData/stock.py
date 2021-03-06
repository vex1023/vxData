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
from io import BytesIO
from random import random
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool as Pool
from vxUtils.decorator import retry
from vxData.cache import cache, TTLTimer

_MAX_SINA_HQ_LIST = 800

_SINA_STOCK_KEYS = [
    "name", "open", "yclose", "lasttrade", "high", "low", "bid", "ask",
    "volume", "amount", "bid1_m", "bid1_p", "bid2_m", "bid2_p", "bid3_m",
    "bid3_p", "bid4_m", "bid4_p", "bid5_m", "bid5_p", "ask1_m", "ask1_p",
    "ask2_m", "ask2_p", "ask3_m", "ask3_p", "ask4_m", "ask4_p", "ask5_m",
    "ask5_p", "date", "time", "status"]

_BAR_URL_TEMPLATE = \
    'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_day%s%s&param=%s,%s,%s-01-01,%s-12-31,640,%s&r=%s'

_KTYPE = {
    'D': 'day',
    'W': 'week',
    'M': 'month'
}

_ADJTYPE = {
    'forward': 'qfq',
    'afterward': 'hfq',
}

_TICK_COLUMNS = ['time', 'price', 'change', 'volume', 'amount', 'type']


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
        df['volume'] = df['volume'] // 100
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

        # 将start，end转换成datetime格式
        if isinstance(start, str):
            if start == '':
                start = datetime.now().replace(month=1, day=1, hour=0, minute=0)
            else:
                start = datetime.strptime(start, '%Y-%m-%d')
        if isinstance(end, str):
            if end == '':
                end = datetime.now().replace(hour=0, minute=0, microsecond=0)
            else:
                end = datetime.strptime(end, '%Y-%m-%d')

        # 判断是否需要使用最新的行情数据
        if (end.date() >= datetime.today().date()) and (self.market_status != 'close'):
            hq = self._thread_pools.apply_async(self.hq, args=([symbol]))
            need_update_hq = True
        else:
            need_update_hq = False

        ktype = _KTYPE[ktype.upper()]

        if adjtype:
            adjtype = _ADJTYPE[adjtype.lower()]
        else:
            adjtype = ''

        data = []
        results = []

        for year in range(start.year - 1, end.year + 1):
            kwargs = {
                'year': year,
                'symbol': symbol,
                'ktype': ktype,
                'adjtype': adjtype
            }
            results.append(self._thread_pools.apply_async(self._parser_bar, kwds=kwargs))

        for result in results:
            result = result.get()
            data.extend(result)

        data = self._thread_pools.map(lambda x: x[:6], data)

        df = pd.DataFrame(data, columns=['date', 'open', 'close', 'high', 'low', 'volume'], dtype='float')
        df = df.set_index('date')
        df = df.sort_index()
        if need_update_hq:
            hq = hq.get()
            date = hq.loc[symbol, 'date']
            bar_last_close = df.ix[-1, 'close']
            hq_yclose = hq.loc[symbol, 'yclose']
            if bar_last_close != hq_yclose:
                adj = hq_yclose / bar_last_close
                df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']] / adj

            df.loc[date, 'open'] = hq.loc[symbol, 'open']
            df.loc[date, 'close'] = hq.loc[symbol, 'lasttrade']
            df.loc[date, 'high'] = hq.loc[symbol, 'high']
            df.loc[date, 'low'] = hq.loc[symbol, 'low']
            df.loc[date, 'volume'] = hq.loc[symbol, 'volume']
        else:
            df = df.loc[df.index <= end.strftime('%Y-%m-%d')]

        df['symbol'] = symbol
        df['yclose'] = df['close'].shift(1)
        df['chg'] = df['close'].pct_change(1) * 100
        df['chg'] = df['chg'].round(2)
        df = df[['symbol', 'open', 'high', 'low', 'close', 'yclose', 'chg', 'volume']]

        df = df.loc[df.index >= start.strftime('%Y-%m-%d')]
        return df

    @cache(TTLTimer(hours=9))
    @retry(3)
    def _parser_bar(self, year, symbol, ktype, adjtype):
        url = _BAR_URL_TEMPLATE % (adjtype, year, symbol, ktype, year, year, adjtype, random())
        r = requests.get(url)
        r.raise_for_status()
        d = r.text
        d = d.split('=')[1]
        d = json.loads(d)['data']

        if '%s%s' % (adjtype, ktype) in d[symbol].keys():
            d = d[symbol]['%s%s' % (adjtype, ktype)]
        else:
            d = d[symbol][ktype]

        return d

    def mbar(self, symbol, ktype='1', adjtype='forward'):
        pass

    def tick(self, symbol, date=None):

        params = {'symbol': symbol, 'date': date}
        r = requests.get(url='http://market.finance.sina.com.cn/downxls.php', params=params)

        tick_xls = BytesIO(r.content)
        tick_val = tick_xls.getvalue()
        if tick_val.find(b'alert') != -1 or len(tick_val) < 20:
            df = pd.DataFrame([], columns=['date', 'symbol', 'type', 'price', 'change', 'amount'])
            df = df.set_index('date')
            return df
        else:
            df = pd.read_table(tick_xls, names=_TICK_COLUMNS, skiprows=[0], encoding='GBK')

        df['date'] = df['time'].apply(lambda x: '%s %s' % (date, x))
        df = df.set_index('date')
        d = {'买盘': 'B', '卖盘': 'S', '中性盘': 'M'}
        df['type'] = df['type'].apply(lambda x: d[x])
        df['symbol'] = symbol
        df = df.sort_index()

        return df[['symbol', 'type', 'price', 'change', 'amount']]
