# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for stockmanager.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import os
import pytest
from stockmanager import Ticker, Portfolio


@pytest.fixture
def rootdir():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def sb():
    return Ticker(symbol='MSFT')


@pytest.fixture(scope="session")
def empty_portfolio():
    return Portfolio()
