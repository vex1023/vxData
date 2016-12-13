# vxData

中国A股市场的开源数据集合

## 数据介绍

### 1. 交易状态 ___（stock.market_status）___

```
from vxData import stock
print(stock.market_status)
# 返回当前市场交易状态: close, trading, break
```

### 2. 交易时间
```
from vxData import stock
# 最近交易日早上开盘时间
print(stock.market_am_open)

# 最近交易日早上收盘时间
print(stock.market_am_close)

# 最近交易日下午开盘时间
print(stock.market_fm_open)

# 最近交易日下午收盘时间
print(stock.market_fm_close)
```

### 3. 实时行情接口（___level 1___)

```
from vxData import stock

print(stock.hq('sz150023','sz150022'))

```

返回一个dataframe格式：

index：symbol

 
```
columns:[
    "name", "open", "yclose", "lasttrade", "high", "low", "bid", "ask",
    "volume", "amount", "bid1_m", "bid1_p", "bid2_m", "bid2_p", "bid3_m",
    "bid3_p", "bid4_m", "bid4_p", "bid5_m", "bid5_p", "ask1_m", "ask1_p",
    "ask2_m", "ask2_p", "ask3_m", "ask3_p", "ask4_m", "ask4_p", "ask5_m",
    "ask5_p", "date", "time", "status"
]
```

### 4. 历史行情接口

```
from vxData import stock

print(stock.bar('sz150023', start='2016-01-01', ktype='D')

```

返回一个dataframe格式:

index: date

```
columns:['date', 'open', 'close', 'high', 'low', 'volume']
```