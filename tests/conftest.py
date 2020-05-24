# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for stockmanager.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import pytest

from stockmanager import Ticker



@pytest.fixture(scope="module")
def sb():
    return Ticker(symbol='MSFT')

