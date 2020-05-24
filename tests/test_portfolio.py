from stockmanager import Portfolio
import pytest
import os

myrecord = Portfolio()

def test_add():
    myrecord.add('MSFT', holdings=10000)
    assert myrecord.summary.loc[myrecord.summary['Symbol'] == 'MSFT'].Holdings[0] == 10000

    # Call add() again on the same ticker will add to the existing portfolio

    myrecord.add('MSFT', holdings=10000)
    assert myrecord.summary.loc[myrecord.summary['Symbol'] == 'MSFT'].Holdings[0] == 20000


def test_add_wrong_param_type():
    with pytest.raises(TypeError):
        # Symbol not string
        myrecord.add(symbol=12)

    with pytest.raises(TypeError):
        # Holdings not int
        myrecord.add('MSFT', holdings=28.3)


def test_add_unrecognisable_symbol():
    with pytest.raises(AttributeError):
        r2 = Portfolio()
        r2.add('fdsafds', holdings=10000)


def test_load(empty_portfolio, rootdir):
    path = os.path.join(rootdir, 'dummy_data', 'dummy.csv')
    empty_portfolio.load(summary_path=path)
    assert empty_portfolio.summary['Symbol'][0] == 'MSFT'
    assert empty_portfolio.summary['Symbol'][1] == 'ZM'

    path = os.path.join(rootdir, 'dummy_data', 'dummy_record.csv')
    empty_portfolio.load(record_path=path)
    assert empty_portfolio.record['Symbol'][0] == 'MSFT'


def test_load_no_param(empty_portfolio, rootdir):
    with pytest.raises(AttributeError):
        empty_portfolio.load()

