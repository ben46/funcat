# -*- coding: utf-8 -*-
#

from functools import reduce

import numpy as np
import talib
import datetime

from .context import ExecutionContext
from .utils import FormulaException, rolling_window, handle_numpy_warning
from .time_series import (
    MarketDataSeries,
    NumericSeries,
    BoolSeries,
    fit_series,
    get_series,
    get_bars,
    ensure_timeseries,
)


class OneArgumentSeries(NumericSeries):

    def __init__(self, series, arg):
        if isinstance(series, NumericSeries):
            series = series.series
            # try:
            series[series == np.inf] = np.nan
            series = talib.MA(series, arg)
        super(OneArgumentSeries, self).__init__(series)
        self.extra_create_kwargs["arg"] = arg


class MovingAverageSeries(NumericSeries):

    def __init__(self, series, arg):
        if isinstance(series, NumericSeries):
            series = series.series
            # try:
            series[series == np.inf] = np.nan
            series = talib.MA(series, arg)
        super(MovingAverageSeries, self).__init__(series)
        self.extra_create_kwargs["arg"] = arg


class WeightedMovingAverageSeries(NumericSeries):

    def __init__(self, series, arg):
        if isinstance(series, NumericSeries):
            series = series.series
            # try:
            series[series == np.inf] = np.nan
            series = talib.WMA(series, arg)
        super(NumericSeries, self).__init__(series)
        self.extra_create_kwargs["arg"] = arg


class ExponentialMovingAverageSeries(NumericSeries):

    def __init__(self, series, arg):
        if isinstance(series, NumericSeries):
            series = series.series
            # try:
            series[series == np.inf] = np.nan
            series = talib.EMA(series, arg)
        super(NumericSeries, self).__init__(series)
        self.extra_create_kwargs["arg"] = arg


class StdSeries(NumericSeries):

    def __init__(self, series, arg):
        if isinstance(series, NumericSeries):
            series = series.series
            # try:
            series[series == np.inf] = np.nan
            series = talib.STDDEV(series, arg)
        super(NumericSeries, self).__init__(series)
        self.extra_create_kwargs["arg"] = arg


class TwoArgumentSeries(NumericSeries):
    func = talib.STDDEV

    def __init__(self, series, arg1, arg2):
        if isinstance(series, NumericSeries):
            series = series.series

            try:
                series[series == np.inf] = np.nan
                series = self.func(series, arg1, arg2)
            except Exception as e:
                raise FormulaException(e)
        super(TwoArgumentSeries, self).__init__(series)
        self.extra_create_kwargs["arg1"] = arg1
        self.extra_create_kwargs["arg2"] = arg2


class SMASeries(TwoArgumentSeries):
    """同花顺专用SMA"""

    def func(self, series, n, _):
        results = np.nan_to_num(series).copy()
        # FIXME this is very slow
        for i in range(1, len(series)):
            results[i] = ((n - 1) * results[i - 1] + results[i]) / n
        return results


class SumSeries(NumericSeries):
    """求和"""

    def __init__(self, series, period):
        if isinstance(series, NumericSeries):
            series = series.series
            try:
                series[series == np.inf] = 0
                series[series == -np.inf] = 0
                series = talib.SUM(series, period)
            except Exception as e:
                raise FormulaException(e)
        super(SumSeries, self).__init__(series)
        self.extra_create_kwargs["period"] = period


class AbsSeries(NumericSeries):
    def __init__(self, series):
        if isinstance(series, NumericSeries):
            series = series.series
            try:
                series[series == np.inf] = 0
                series[series == -np.inf] = 0
                series = np.abs(series)
            except Exception as e:
                raise FormulaException(e)
        super(AbsSeries, self).__init__(series)


@handle_numpy_warning
def CrossOver(s1, s2):
    """s1金叉s2
    :param s1:
    :param s2:
    :returns: bool序列
    :rtype: BoolSeries
    """
    s1, s2 = ensure_timeseries(s1), ensure_timeseries(s2)
    series1, series2 = fit_series(s1.series, s2.series)
    cond1 = series1 > series2
    series1, series2 = fit_series(s1[1].series, s2[1].series)
    cond2 = series1 <= series2  # s1[1].series <= s2[1].series
    cond1, cond2 = fit_series(cond1, cond2)
    s = cond1 & cond2
    return BoolSeries(s)

@handle_numpy_warning
def CROSSUNDER(s1, s2):
    """s1金叉s2
    :param s1:
    :param s2:
    :returns: bool序列
    :rtype: BoolSeries
    """
    s1, s2 = ensure_timeseries(s1), ensure_timeseries(s2)
    series1, series2 = fit_series(s1.series, s2.series)
    cond1 = series1 < series2
    series1, series2 = fit_series(s1[1].series, s2[1].series)
    cond2 = series1 >= series2  # s1[1].series <= s2[1].series
    cond1, cond2 = fit_series(cond1, cond2)
    s = cond1 & cond2
    return BoolSeries(s)

def Ref(s1, n):
    return s1[n]


@handle_numpy_warning
def minimum(s1, s2):
    s1, s2 = ensure_timeseries(s1), ensure_timeseries(s2)
    if len(s1) == 0 or len(s2) == 0:
        raise FormulaException("minimum size == 0")
    series1, series2 = fit_series(s1.series, s2.series)
    s = np.minimum(series1, series2)
    return NumericSeries(s)


@handle_numpy_warning
def maximum(s1, s2):
    s1, s2 = ensure_timeseries(s1), ensure_timeseries(s2)
    if len(s1) == 0 or len(s2) == 0:
        raise FormulaException("maximum size == 0")
    series1, series2 = fit_series(s1.series, s2.series)
    s = np.maximum(series1, series2)
    return NumericSeries(s)


@handle_numpy_warning
def count(cond, n):
    # TODO lazy compute
    series = cond.series
    size = len(cond.series) - n
    try:
        result = np.full(size, 0, dtype=np.int)
    except ValueError as e:
        raise FormulaException(e)
    for i in range(size - 1, 0, -1):
        s = series[-n:]
        result[i] = len(s[s == True])
        series = series[:-1]
    return NumericSeries(result)


@handle_numpy_warning
def every(cond, n):
    return count(cond, n) == n


@handle_numpy_warning
def hhv(s, n):
    # TODO lazy compute
    series = s.series
    size = len(s.series) - n
    try:
        result = np.full(size, 0, dtype=np.float64)
    except ValueError as e:
        raise FormulaException(e)

    result = np.max(rolling_window(series, n), 1)

    return NumericSeries(result)


def ZTPRICE(close, max_zf):
    close = close.value
    max_zf = max_zf + 1
    new_price = round(close * max_zf, 2)

    def _get_abs(_price):
        return abs(_price / close - max_zf)

    if _get_abs(new_price + 0.01) < _get_abs(new_price):
        new_price = new_price + 0.01

    if _get_abs(new_price - 0.01) < _get_abs(new_price):
        new_price = new_price - 0.01
    zhangting = new_price

    def _get_abs_dt(_price):
        return abs(_price / close - 2 + max_zf)

    new_price = round(close * (2 - max_zf), 2)
    if _get_abs_dt(new_price + 0.01) < _get_abs_dt(new_price):
        print('add 0.01')
        new_price = new_price + 0.01
    if _get_abs_dt(new_price - 0.01) < _get_abs_dt(new_price):
        print('minuse 0.01')
        new_price = new_price - 0.01
    dieting = new_price
    return zhangting


def DTPRICE(close, max_zf):
    close = close.value

    max_zf = max_zf + 1
    new_price = round(close * max_zf, 2)

    def _get_abs(_price):
        return abs(_price / close - max_zf)

    if _get_abs(new_price + 0.01) < _get_abs(new_price):
        new_price = new_price + 0.01

    if _get_abs(new_price - 0.01) < _get_abs(new_price):
        new_price = new_price - 0.01
    zhangting = new_price

    def _get_abs_dt(_price):
        return abs(_price / close - 2 + max_zf)

    new_price = round(close * (2 - max_zf), 2)
    if _get_abs_dt(new_price + 0.01) < _get_abs_dt(new_price):
        print('add 0.01')
        new_price = new_price + 0.01
    if _get_abs_dt(new_price - 0.01) < _get_abs_dt(new_price):
        print('minuse 0.01')
        new_price = new_price - 0.01
    dieting = new_price
    return dieting


def MOD(a, b):
    return a % b


def FROMOPEN():
    now = datetime.datetime.now()
    # now = datetime.datetime.strptime('%d-%d-%d 7:36:00' % (now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S')
    # print(now)

    OPEN_AM = datetime.datetime.strptime('%d-%d-%d 09:30:00' % (now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S')
    CLOSE_AM = datetime.datetime.strptime('%d-%d-%d 11:30:00' % (now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S')

    OPEN_PM = datetime.datetime.strptime('%d-%d-%d 13:00:00' % (now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S')
    CLOSE_PM = datetime.datetime.strptime('%d-%d-%d 15:00:00' % (now.year, now.month, now.day), '%Y-%m-%d %H:%M:%S')

    if now.timestamp() < OPEN_AM.timestamp():
        return 0
    # 早上
    if CLOSE_AM.timestamp() >= now.timestamp() >= OPEN_AM.timestamp():
        return int((now.timestamp() - OPEN_AM.timestamp()) / 60)
    # 中午
    if OPEN_PM.timestamp() >= now.timestamp() >= CLOSE_AM.timestamp():
        return int((CLOSE_AM.timestamp() - OPEN_AM.timestamp()) / 60)
    # 下午
    if CLOSE_PM.timestamp() >= now.timestamp() >= OPEN_PM.timestamp():
        return int((now.timestamp() - OPEN_PM.timestamp()) / 60) + 120
    if now.timestamp() > CLOSE_PM.timestamp():
        return 240
    return 0


@handle_numpy_warning
def llv(s, n):
    # TODO lazy compute
    series = s.series
    size = len(s.series) - n
    try:
        result = np.full(size, 0, dtype=np.float64)
    except ValueError as e:
        raise FormulaException(e)

    result = np.min(rolling_window(series, n), 1)

    return NumericSeries(result)


@handle_numpy_warning
def iif(condition, true_statement, false_statement):
    series1 = get_series(true_statement)
    series2 = get_series(false_statement)
    cond_series, series1, series2 = fit_series(condition.series, series1, series2)

    series = series2.copy()
    series[cond_series] = series1[cond_series]

    return NumericSeries(series)


@handle_numpy_warning
def barslast(statement):
    series = get_series(statement)
    size = len(series)
    end = size
    begin = size - 1
    result = np.full(size, 1e16, dtype=np.int64)
    for s in series[::-1]:
        if s:
            result[begin:end] = range(0, end - begin)
            end = begin
        begin -= 1
    return NumericSeries(result)


def change(s, n=1):
    return s - Ref(s, n)


def valuewhen(statement, source, occurence=0):
    _barslast, _source = fit_series(barslast(statement).series, source.series)
    size = len(_barslast)
    result = np.full(size, 1e16, dtype=np.float)

    for idx in range(size):
        _i = _barslast[idx]
        # print(idx, series[size-_i-1], _i)
        if _i != 10000000000000000:
            result[idx] = _source[idx-1*_i]
            # result[idx] = _source[idx]
        else:
            result[idx] = 10000000000000000
        # print(idx,result[idx], _source[idx], _barslast[idx])
    return NumericSeries(result)

"""
defaul vlaue = 0
"""
def PivotHigh(source, left, right=0):
    right = right if right else left
    series = get_series(source)
    size = len(series)
    result = np.full(size, 0, dtype=np.float)
    for i in range(size):
        if i >= left + right:
            rolling = series[i - right - left:i + 1]# .values
            m = max(rolling)
            if series[i - right] == m:
                result[i] = m
    return NumericSeries(result)


"""
枢轴点 最低价, default value=0
"""
def PivotLow(source, left, right=0):
    right = right if right else left
    series = get_series(source)
    size = len(series)
    result = np.full(size, 0, dtype=np.float)
    for i in range(size):
        if i >= left + right:
            rolling = series[i - right - left:i + 1]  # .values
            m = min(rolling)
            if series[i - right] == m:
                result[i] = m
    return NumericSeries(result)

    # right = right if right else left
    # df['rollingLow'] = df['Low'].rolling(left+right).min()
    # df['pivot'] = 0.0
    # for i in range(len(df)):
    #     if i >= left+right:
    #         rolling = df['Low'][i-right-left:i+1].values
    #         m = min(rolling)
    #         if df['Low'][i-right] == m:
    #             df['pivot'].values[i] = m
    # return df['pivot']


'''
r：K线数据，字典或者数组
days：指标长度
name：使用哪一个字段，填’Close’即可，如果不填则代表r是数组而不是字典
变量r 字典结构图如下：
{
    {
        'Time': 0,
        'Close': 0,
        'Open': 0,
        'High': 0,
        'Low': 0,
        'Volume': 0,
    }
}
RMA，RSI中使用的移动平均线，它是指数加权移动平均线
'''
def rma(source, days):
    series = get_series(source)
    # rmas = [0 for i in range(len(series))]  # 创造一个和cps一样大小的集合
    size = len(series)
    rmas = np.full(size, 0, dtype=np.float)
    alpha = 1 / days

    for i in range(len(series)):
        if i < days - 1:
            rmas[i] = 0
        else:
            if rmas[i - 1]:
                rmas[i] = alpha * series[i] + (1 - alpha) * rmas[i - 1]
            else:
                ma = 0
                for i2 in range(i - days, i):  # 求平均值
                    ma += series[i2 + 1]
                rmas[i] = ma / days
    return NumericSeries(rmas)
