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

    with pytest.raises(TypeError):
        myrecord.add(symbol=12)  # Symbol needs to be tring.

    with pytest.raises(TypeError):
        myrecord.add('MSFT', holdings=28.3)  # Holdings has to be int

    with pytest.raises(AttributeError):
        r2 = Portfolio()
        r2.add('fdsafds', holdings=10000)

# def test_load():
#     print(os.path.dirname(os.path.abspath(__file__)))
#     dummy = Portfolio().load('./dummy_data/dummy.csv')
#     assert dummy.summary.shape[0] == 2

