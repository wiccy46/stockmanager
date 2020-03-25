from stockmanager import Portfolio

myrecord = Portfolio()

def test_add():
    myrecord.add('MSFT', holdings=10000)
    assert myrecord.summary.loc[myrecord.summary['Symbol'] == 'MSFT'].Holdings[0] == 10000

    # Call add() again on the same ticker will add to the existing portfolio

    myrecord.add('MSFT', holdings=10000)
    assert myrecord.summary.loc[myrecord.summary['Symbol'] == 'MSFT'].Holdings[0] == 20000
