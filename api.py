# -*- coding: utf-8 -*-
import numpy as np

from .time_series import MarketDataSeries
from .func import (
    SumSeries,
    AbsSeries,
    StdSeries,
    SMASeries,
    MovingAverageSeries,
    WeightedMovingAverageSeries,
    ExponentialMovingAverageSeries,
    CrossOver,
    minimum,
    maximum,
    every,
    count,
    hhv,
    llv,
    Ref,
    iif,
    ZTPRICE,
CROSSUNDER,
DTPRICE,
MOD,
FROMOPEN,
barslast,
valuewhen,
change,
PivotHigh,
PivotLow,
rma,

)
from .context import (
    symbol,
    set_current_security,
    set_current_date,
    set_start_date,
    set_data_backend,
    set_current_freq,
)
from .helper import select


# create open high low close volume datetime
for name in ["open", "high", "low", "close", "volume", "datetime"]:
    dtype = np.float64 if name != "datetime" else np.uint64
    cls = type("{}Series".format(name.capitalize()), (MarketDataSeries, ), {"name": name, "dtype": dtype})
    obj = cls(dynamic_update=True)
    for var in [name[0], name[0].upper(), name.upper()]:
        globals()[var] = obj

VOL = VOLUME
PIVOTLOW = PivotLow
PIVOTHIGH = PivotHigh
MA = MovingAverageSeries
WMA = WeightedMovingAverageSeries
EMA = ExponentialMovingAverageSeries
SMA = SMASeries

SUM = SumSeries
ABS = AbsSeries
STD = StdSeries

CROSS =CROSSOVER= CrossOver
REF = Ref
MIN = minimum
MAX = maximum
EVERY = every
COUNT = count
HHV = hhv
LLV = llv
IF = IIF = iif

S = set_current_security
T = set_current_date
BARSLAST=barslast
CHANGE = change
__all__ = [
"rma",
    "OPEN", "O",
    "HIGH", "H",
    "LOW", "L",
    "CLOSE", "C",
    "VOLUME", "V", "VOL",
    "DATETIME",
    "CROSSUNDER",
    "SMA",
    "MA",
    "EMA",
    "WMA",

    "SUM",
    "ABS",
    "STD",

    "CROSS","CROSSOVER",
    "REF",
    "MAX",
    "MIN",
    "EVERY",
    "COUNT",
    "HHV",
    "ZTPRICE",
    "DTPRICE",
    "MOD",
    "FROMOPEN",
    "BARSLAST",
    "CHANGE",
    "change",
    "PivotLow",
    "PIVOTLOW",
    "PIVOTHIGH",
    "valuewhen",
    "PivotHigh",

    "LLV",
    "IF", "IIF",

    "S",
    "T",

    "select",
    "symbol",
    "set_current_security",
    "set_current_date",
    "set_start_date",
    "set_data_backend",
    "set_current_freq",
]
