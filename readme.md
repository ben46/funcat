# funcat跨平台开发工具
**可以把通达信,同花顺,文华财经,tradingview的代码移植到python**

极大的扩展了指标库, 广大量化研究者可以把海量的通达信,同花顺,文华财经
的代码放入python中做回测,做机器学习.
由于本人日常用tradingview也比较多, 
因此把tradingview上的Pine代码函数也一并移植了进来

本项目要和tushare联合使用,否则无法运行
[小弟维护的tushare库项目地址](https://github.com/ben46/tushare)

---------------------------------

[funcat源代码地址](https://github.com/cedricporter/funcat)

**小弟正在找工作, 大佬如果看中小弟, 请联系我ben02060846@qq.com**

# 如何安装
```commandline
git clone https://github.com/ben46/funcat.git
cd funcat
python install_funcat.py install
```

# 本人在funcat基础上增加了几个常用函数
#### CrossOver
上穿

#### CROSSUNDER
下穿

#### ZTPRICE
涨停价格

#### DTPRICE
跌停价格

#### MOD
余运算

#### FROMOPEN
距离开盘时间

#### barslast
上一次满足条件的时候,距离现在多少个k线
#### change
和上一个交易日相比的差值

#### valuewhen
上一次满足条件的时候,数组的值是多少

#### PivotHigh
上一个转折高点

#### PivotLow
#### rma

## 下面开始我的表演
为了达到演示效果, 我方出阵TSV指标, 用于提示风险股票, 
各位看官可以从中看到具体代码应该如何使用
```Python
LBR=1
set_start_date("2022-06-23")
S(code)  # 设置当前关注股票
T(datetime.datetime.now().strftime("%Y-%m-%d"))  # 设置当前观察日期

len = 13
l_ma = 3

rangeUpper = 100
rangeLower = 2

xxx = IF(C < C[1], V * (C - C[1]), 0)
yyy = IF(C > C[1], V * (C - C[1]), xxx)
rsi = SUM(yyy, len)  # tsv柱状图
osc = MA(rsi, l_ma)  # tsv  均线 checked

# Kumo   Cloud
conversionPeriods = 9
basePeriods = 26
laggingSpan2Periods = 52

def donchian(len):
    return (LLV(L, len) + HHV(H, len)) / 2

conversionLine = donchian(conversionPeriods)
baseLine = donchian(basePeriods)
leadLine1 = (conversionLine + baseLine) / 2 # checked
leadLine2 = donchian(laggingSpan2Periods) # checked

plFound1 = PIVOTLOW(osc, 5, LBR) != 0
plFound5 = PIVOTLOW(osc, 5, 5) != 0 # checked

phFound1 = PIVOTHIGH(osc, 5, LBR) != 0
phFound5 = PIVOTHIGH(osc, 5, 5) != 0

def _inRange(cond):
    bars = BARSLAST(cond)
    return (rangeLower <= bars) & (bars <= rangeUpper)

inRangeFind = plFound5 if LBR == 1 else phFound5[1]
plFound5_occur = 0 if LBR == 1 else 1

oscHL = (osc[LBR] > valuewhen(plFound5, osc[5], plFound5_occur)) & _inRange(inRangeFind)

priceLL = L[LBR] < valuewhen(plFound5, L[5], plFound5_occur)
bullCond = priceLL & oscHL & plFound1

oscLL = (osc[LBR] < valuewhen(plFound5, osc[5], plFound5_occur)) & _inRange(inRangeFind)

priceHL = L[LBR] > valuewhen(plFound5, L[5], plFound5_occur)
hiddenBullCond = priceHL & oscLL & plFound1

oscLH = (osc[LBR] < valuewhen(phFound5, osc[5], plFound5_occur)) & _inRange(inRangeFind)

priceHH = H[LBR] > valuewhen(phFound5, H[5], plFound5_occur)

bearCond = priceHH & oscLH & phFound1

oscHH = (osc[LBR] > valuewhen(phFound5, osc[5], plFound5_occur) )& _inRange(inRangeFind)

priceLH = H[LBR] < valuewhen(phFound5, H[5], plFound5_occur)

hiddenBearCond = priceLH & oscHH & phFound1
cond_short = hiddenBearCond | bearCond
cond_long = hiddenBullCond | bullCond
print('看空信号是否满足', cond_short)
print('看多信号是否满足', cond_long)
```



