# encoding=utf-8

import unittest
import logging
from vxData import stock


class vxDataCase(unittest.TestCase):
    def test_API(self):
        print(stock.market_status)
        print(stock.market_am_open)
        print(stock.market_am_close)
        print(stock.market_fm_open)
        print(stock.market_fm_close)
        print(stock.hq('sz150023', 'sh000001', 'sh600036'))
        print(stock.bar('sz150023', start='2010-01-01', ktype='D'))
        print(stock.bar('sz150023', start='2010-01-01', ktype='W'))
        print(stock.bar('sz150023', start='2010-01-01', ktype='M'))
        print(stock.bar('sh510050', start='2010-01-01', ktype='D'))
        print(stock.bar('sh510050', start='2010-01-01', ktype='W'))
        print(stock.bar('sh510050', start='2010-01-01', ktype='M'))


if __name__ == '__main__':
    unittest.main()
