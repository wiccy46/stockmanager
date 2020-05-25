============
stockmanager
============


Manager, Analyze, Stimulate stock information.

.. image:: https://travis-ci.com/wiccy46/stockmanager.svg?branch=master
    :target: https://travis-ci.com/wiccy46/stockmanager


Installation
============

Using pip::

    pip install stockmanager

Example
=======

Load a stock info::

    from stockmanager import Ticker

    mystock = Ticker(symbol='MSFT')  # Give a ticker string

    # result is a pandas DataFrame
    info_pd = mystock.get_price(start='2020-03-01', end='2020-03-19')

    # Or use period and interval
    # valid period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # valid interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    info_pd = mystock.get_price(period='1mo', interval='1d')

    earnings = mystock.get_earings(freq='yearly')
    cashflow = mystock.get_cashflow(freq='quarterly')
    balancesheet = mystock.get_balancesheet()

Other attributes: institutional_holders, major_holders, mutual_fund_holders,
sustainability, company_information,

Visualization:

    from stockmanager import Ticker, visualization

    mystock = Ticker(symbol='MSFT')  # Give a ticker string
    # result is a pandas DataFrame
    info_pd = mystock.get_price(start='2020-03-01', end='2020-03-19')

    # Accept matplotlib and plotly (interactive) backend 
    visualization.plot_price(info_pd)

    # or use plotly
    visualization.plot_price(info_pd, backend='plotly')

Portfolio is a class that let you add holdings of certain stocks and add trade 
records. It has two main attributes, 

* Portfolio.summary as your holding summary
* Portfolio.record as a table of all the trade record. 

Example: 

    from stockmanager import Portfolio

    myportfolio = Portfolio()
    myportfolio.add('AAPL', holdings=200)
    myportfolio.add('ZM', holdings=200)
    myportfolio.summary # This is a DataFrame view of your holdings.

    # typ is buy or sell, price by default will try to get the current price
    # update_summary will modified self.summary according to amount. 
    myportfolio.trade(typ='buy'|'sell', symbol='AAPL', amount=20,
                      prince=200., update_summary=True)
    
    myportfolio.save(filepath='./', summary_name='portfolio',
                     record_name='record', format='csv')
    
    myportfolio.load(summary_path='./portfolio.csv', record_path='./record.csv')



