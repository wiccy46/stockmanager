from stockmanager import StockBase
import pandas as pd
import pytest
import numpy as np
from datetime import datetime
from datetime import timedelta

sb = StockBase('MSFT')

# A better way should be a mock test. ....

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

def test_get_fundamental():
    assert type(sb.institutional_holders) is pd.DataFrame
    assert type(sb.major_holders) is pd.DataFrame
    assert type(sb.mutual_fund_holders) is pd.DataFrame
    assert type(sb.sustainability) is pd.DataFrame
    assert type(sb.company_information) is dict

def test_cashflow():
    cashflow = sb.get_cashflow()
    assert type(cashflow) is pd.DataFrame

    cashflow = sb.get_cashflow(as_dict=True)
    assert type(cashflow) is dict

    _ = sb.get_cashflow(freq='Quarterly')

    with pytest.raises(AttributeError):
        _ = sb.get_cashflow(freq='monthly')

def test_earings():
    earnings = sb.get_earnings()
    assert type(earnings) is pd.DataFrame

    earnings = sb.get_earnings(as_dict=True)
    assert type(earnings) is dict

    _ = sb.get_earnings(freq='Quarterly')

    with pytest.raises(AttributeError):
        _ = sb.get_earnings(freq='monthly')

def test_balancesheet():
    balancesheet = sb.get_balancesheet()
    assert type(balancesheet) is pd.DataFrame

    balancesheet = sb.get_balancesheet(as_dict=True)
    assert type(balancesheet) is dict

    _ = sb.get_balancesheet(freq='Quarterly')

    with pytest.raises(AttributeError):
        _ = sb.get_balancesheet(freq='monthly')