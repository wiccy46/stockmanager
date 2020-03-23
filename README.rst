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

    from stockmanager import StockBase

    stock = StockBase('MSFT')  # Give a ticker string

    # result is a pandas DataFrame
    info_pd = stock.get_stock_info(start='2020-03-01', end='2020-03-19')

    # Or use period and interval
    # valid period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # valid interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    info_pd = stock.get_stock_info(period='1mo', interval='1d')

    earnings = stock.get_earings(freq='yearly')
    cashflow = stock.get_cashflow(freq='quarterly')
    balancesheet = stock.get_balancesheet()

Other attributes: institutional_holders, major_holders, mutual_fund_holders,
sustainability, company_information,


Description
===========

Initial commit, currently on have method to get stock info, recent roadmap:

* File saver for your personal stock
* Stocks class based on StockBase for multiple tickers
* Keep track of trades, report profit
* Analysis of stocks, visualization
* Trading simulation... to be decided.
* and more...


Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
