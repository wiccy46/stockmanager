from stockmanager import Portfolio
import pytest
import os
import time
from unittest import mock

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
    summary_path = os.path.join(rootdir, 'dummy_data', 'dummy.csv')
    record_path = os.path.join(rootdir, 'dummy_data', 'dummy_record.csv')
    empty_portfolio.load(summary_path=summary_path, record_path=record_path)
    assert empty_portfolio.summary['Symbol'][0] == 'MSFT'
    assert empty_portfolio.summary['Symbol'][1] == 'ZM'


def test_load_no_such_file(empty_portfolio, rootdir):
    with pytest.raises(FileNotFoundError):
        empty_portfolio.load()


# @mock.patch(Portfolio.to_csv)
# def test_save(empty_portfolio, rootdir):
#     path = os.path.join(rootdir, 'dummy_data')
#     empty_portfolio.save(filepath=path)
#     time.sleep(2)
#     os.remove(os.path.join(path, 'portfolio.csv'))
#     os.remove(os.path.join(path, 'records.csv'))


def test_remove_str(dummy_portfolio):
    dummy_portfolio.remove('AAPL')
    check = 'AAPL' in set(dummy_portfolio.summary.Symbol)
    assert check == False


def test_remove_list(dummy_portfolio):
    dummy_portfolio.remove(['AAPL', 'MSFT'])
    check = ('AAPL', 'MSFT') in set(dummy_portfolio.summary.Symbol)
    assert check == False

