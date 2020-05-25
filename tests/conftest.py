# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for stockmanager.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import os
import pytest
from pandas import read_csv, to_datetime, DataFrame
from stockmanager import Ticker, Portfolio


@pytest.fixture(scope="module")
def rootdir():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def dummy_price(rootdir):
    path = ''.join([rootdir, '/dummy_data/dummy_price.csv'])
    df = read_csv(path, index_col=0)
    df['Datetime'] = to_datetime(df.index)
    df = df.set_index('Datetime')
    return df


@pytest.fixture(scope="module")
def sb():
    return Ticker(symbol='MSFT')


@pytest.fixture(scope="session")
def empty_portfolio():
    return Portfolio()


@pytest.fixture(scope="session")
def dummy_portfolio():
    p = Portfolio()
    d = {'Symbol':['AAPL', 'MSFT', 'ZM'],
         'Name': ['AA', 'MM', 'ZOOM'],
         'Price': ['10', '15', '5'],
    }
    p.summary = DataFrame(data=d)
    return p