from stockmanager import StockBase
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

sb = StockBase('MSFT')

def test_attribute():
    assert sb._base_url == 'https://query1.finance.yahoo.com'
    assert sb._scrape_url == 'https://finance.yahoo.com/quote'

def test_getprice():
    result = sb.get_price()
    assert type(result) is pd.DataFrame

    # Start and end date will include both dates if possible.
    result = sb.get_price(start='2020-01-01', end='2020-01-31')
    first_day = result.index.values[0]
    first_day = pd.to_datetime(first_day)
    first_day = first_day.date().strftime('%Y-%m-%d')

    last_day = result.index.values[-1]
    last_day = pd.to_datetime(last_day)
    last_day = last_day.date().strftime('%Y-%m-%d')

    assert first_day == '2020-01-02'  # because 01-01 is offday
    assert last_day == '2020-01-31'

    # since the very beginning --> max period
    a = sb.get_price(period='max')
    b = sb.get_price(period=None, start=None)
    fd_a = a.index.values[0]
    fd_b = b.index.values[0]
    assert fd_a == fd_b

    # start/ end as date time.

    # different period and interval.

def test_get_general_info():
    # general_info = sb.get_general_info()
    pass