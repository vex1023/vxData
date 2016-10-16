# vxData

中国A股市场的开源数据集合

## 数据介绍
主要有以下几个类型的数据：
1. cal: 交易日期
2. symbol: 证券代码库
3. hq: 实时行情数据
4. nav: 基金净值数据
5. bar: K线数据

### 交易日历 ___（cal）___

1. market_status  : 获取市场当前的交易状态

```python
import vxData
print(vxData.cal.exchange_status())

```
返回当前市场交易状态 Opening, NoonBreak, Closed 
2. trade_day_of_mounth : 本月第几个交易日