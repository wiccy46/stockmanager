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

    # or use get_recent() to get the recent days
    recent_info_pd = stock.get_recent(days=7)




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
