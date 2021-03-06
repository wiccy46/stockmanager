""" Base stock class

Based on https://github.com/ranaroussi/yfinance/blob/master/yfinance/base.py

Copyright 2020- Jiajun Yang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
import pandas as pd
import time
import datetime
import json
import requests
from . import helpers
from warnings import warn

VALID_PERIOD = ['1d', '5d', '1mo', '3mo', '6mo',
                '1y', '2y', '5y', '10y', 'ytd', 'max']
VALID_INTERVAL = ['1m', '2m', '5m', '15m', '30m', '60m',
                  '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']


class Ticker():
    """Base class of stockmanager, 
    here it holds all basic infomation of a particular
    ticker. The information is requested from Yahoo Finance.

    Attributes
    ----------
    symbol : str
        ticker symbol, updating the symbol will update the fundamental, 
        e.g. Microsoft is MSFT.
    _base_url : str
        https://query1.finance.yahoo.com
    _scrape_url : str
        https://finance.yahoo.com/quote
    _price_request_content : dict
        Raw content of the web request.
    _fundamentals : bool
        Flag to check if get_fundamentals() is already successfully called.
    major_holders : pandas.DataFrame
        Major holders
    institutional_holders : pandas.DataFrame
        Top institutional holders
    mutual_fund_holder : pandas.DataFrame
        Top mutual fund holder
    company_information : dict
        General information of the company, 
        e.g. sector, fullTimeEmployees, website, etc.
    """

    # TODO add proxy
    # TODO dont run summary to save time. 
    def __init__(self, symbol, proxy=None):
        """ticker is a string name of the stock"""
        self._ticker_symbol = symbol.upper()
        self._base_url = 'https://query1.finance.yahoo.com'
        self._scrape_url = 'https://finance.yahoo.com/quote'
        self._fundamentals = False  
        self._recommendations = None  # TODO to be decided whether this necessary
        self._institutional_holders = None
        self._major_holders = None
        self._mutual_fund_holders = None
        self._sustainability = None
        self._calendar = None
        self._expirations = {}
        self._info = None
        self._proxy = proxy
        self._name = None
        self._current_price = None
        self._currency = None

        self._earnings = {
            "yearly": helpers.empty_df(),
            "quarterly": helpers.empty_df()}
        self._financials = {
            "yearly": helpers.empty_df(),
            "quarterly": helpers.empty_df()}
        self._balancesheet = {
            "yearly": helpers.empty_df(),
            "quarterly": helpers.empty_df()}
        self._cashflow = {
            "yearly": helpers.empty_df(),
            "quarterly": helpers.empty_df()}
        self.meta = []
        self.timestamp = []
        self.indicators = []

    @property
    def symbol(self):
        """ticker symbol."""
        return self._ticker_symbol

    @symbol.setter
    def symbol(self, symbol):
        self._ticker_symbol = symbol

    @property
    def institutional_holders(self):
        return self._institutional_holders

    @property
    def major_holders(self):
        return self._major_holders

    @property
    def mutual_fund_holders(self):
        return self._mutual_fund_holders

    @property
    def sustainability(self):
        return self._sustainability

    @property
    def company_information(self):
        return self._info

    @property
    def name(self):
        return self._name

    @property
    def current_price(self):
        try:
            url = '%s/%s' % (self._scrape_url, self._ticker_symbol)
            data = helpers.get_json(url, self._proxy)
            self._current_price = data['price']['regularMarketPrice']
            return self._current_price
        except:
            return self._current_price

    @property
    def currency(self):
        return self._currency

    def get_price(self, period="1mo", interval="1d",
                  start=None, end=None, timezone=None, format='df'):
        """Return a DataFrame of the ticker based on certain period and interval

        Examples
        --------
        Two ways of choosing the time range, 1) using period 2) start/end::

            from stockmanager import Ticker

            msft = StockBase('MSFT')
            df1 = msft.get_price(period='3mo', interval='1d')

            # or to use start and end
            df2 = msft.get_price(start='2020-01-01', end='2020-02-01')

        Parameters
        ----------
        period : str
            Time period to retrive, it can only be one of the following:
            1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval : str
            Interval of the desired period, it can only be one of the following:
            1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        start : None or str
            Use either period or start/end. If start/end is used,
            use yy-mm-dd format. start date will be included if possible
        end : None or str
            End date, yy-mm-dd, end date will be included if possible.
        timezone : None or str
            timezone for timestamp conversion. 
        format : str
            Indicate the return variable type. By default it is a pandas DataFrame.
            Other options are dict (returns the raw dictionary file). Or json
            (returns in json format)
        """
        # First get the time period right
        if start or period is None or period.lower() == "max":
            if start is None:
                start = -2208988800
            elif isinstance(start, str):
                start = np.datetime64(start)
                start = pd.to_datetime(start)
                start = int(start.timestamp())
            elif isinstance(start, datetime.datetime):
                start = int(time.mktime(start.timetuple()))
            else:
                raise(TypeError("start must be None, str, or datetime.dateime"))

            if end is None:
                end = int(time.time())
            elif isinstance(end, str):
                end = np.datetime64(end)
                end = pd.to_datetime(end) + datetime.timedelta(days=1)  # This is to include end date
                end = int(end.timestamp())
            elif isinstance(end, datetime.datetime):
                end = int(time.mktime(end.timetuple()))
            else:
                raise(TypeError("end must be None, str, or datetime.dateime"))

            params = {"period1": start, "period2": end}
        else:
            period = period.lower()
            if period not in VALID_PERIOD:
                raise(AttributeError("valid period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. "))
            params = {"range": period}

        if interval not in VALID_INTERVAL:
            raise(AttributeError("valid interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo"))
        params["interval"] = interval.lower()
        url = "{}/v8/finance/chart/{}".format(self._base_url, self._ticker_symbol)
        self._price_request_content = requests.get(url=url, params=params)

        # What if other language? Question, how to test it. 
        if "Will be right back" in self._price_request_content.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n")
        self._price_request_content = self._price_request_content.json()
        self._price_request_content = self._price_request_content["chart"]["result"][0]
        # Raw information from the request response. 
        self.meta = self._price_request_content['meta']
        self.timestamp = self._price_request_content['timestamp']
        self.indicators = self._price_request_content['indicators']
        self.prices = self.indicators["quote"][0]
        if format.lower() == "df":
            try:
                df = helpers.create_df(self._price_request_content, timezone)
                df.dropna(inplace=True)
            except Exception:
                raise RuntimeError("Error parsing content.")
            self.prices = df.copy()
        elif format.lower() == "json":
            # Dumping into a JSon formatted string. 
            self.prices = json.dumps(self.prices, sort_keys=True)
            # self.prices = json.loads(s)
        elif format.lower() == "dict":
            pass
        else:
            warn("unrecognised format, return as dict")
        return self.prices

    def get_fundamentals(self, kind=None, proxy=None):
        """"This part scrap information from the Yahoo Finance: 
        https://finance.yahoo.com/quote/YOUR_TICKER 

        It will try to get all fundamental information for more info than just prices.

        Attributes
        ----------
        * major_holders
        * institutional_holders
        * mutual_fund_holders
        * info
        * recommendations
        """
        def cleanup(data):
            df = pd.DataFrame(data).drop(columns=['maxAge'])
            for col in df.columns:
                df[col] = np.where(
                    df[col].astype(str) == '-', np.nan, df[col])

            df.set_index('endDate', inplace=True)
            try:
                df.index = pd.to_datetime(df.index, unit='s')
            except ValueError:
                df.index = pd.to_datetime(df.index)
            df = df.T
            df.columns.name = ''
            df.index.name = 'Breakdown'

            df.index = helpers.camel2title(df.index)
            return df

        # setup proxy in requests format
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        if self._fundamentals:
            # If already exist 
            return

        # get info and sustainability
        url = '%s/%s' % (self._scrape_url, self._ticker_symbol)
        data = helpers.get_json(url, proxy)

        # holders
        url_holders = "{}/{}/holders".format(self._scrape_url, self._ticker_symbol)

        holders = pd.read_html(url_holders)
        try:
            if len(holders) == 3:
                self._major_holders = holders[0]
                self._institutional_holders = holders[1]
                self._mutual_fund_holders = holders[2]
                if 'Date Reported' in self._institutional_holders:
                    self._institutional_holders['Date Reported'] = pd.to_datetime(
                        self._institutional_holders['Date Reported'])
            elif len(holders) == 2:
                self.self._major_holders = holders[0]
                self._institutional_holders = None
                self._mutual_fund_holders = holders[1]
        except:
            self._major_holders = None
            self._institutional_holders = None
            self._mutual_fund_holders = None

        self._all_holders = holders

        # sustainability
        d = {}
        if isinstance(data.get('esgScores'), dict):
            for item in data['esgScores']:
                if not isinstance(data['esgScores'][item], (dict, list)):
                    d[item] = data['esgScores'][item]

            s = pd.DataFrame(index=[0], data=d)[-1:].T
            s.columns = ['Value']
            s.index.name = '%.f-%.f' % (
                s[s.index == 'ratingYear']['Value'].values[0],
                s[s.index == 'ratingMonth']['Value'].values[0])

            self._sustainability = s[~s.index.isin(
                ['maxAge', 'ratingYear', 'ratingMonth'])]
        #
        # #  company info (be nice to python 2)
        self._info = {}
        items = ['summaryProfile', 'summaryDetail', 'quoteType',
                 'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
        for item in items:
            if isinstance(data.get(item), dict):
                self._info.update(data[item])

        self._info['regularMarketPrice'] = self._info['regularMarketOpen']
        self._info['logo_url'] = ""
        self._name = self._info['shortName']  # Company Name
        self._currency = self._info['currency']
        try:
            domain = self._info['website'].split(
                '://')[1].split('/')[0].replace('www.', '')
            self._info['logo_url'] = 'https://logo.clearbit.com/%s' % domain
        except Exception:
            pass

        # analyst recommendations
        try:
            rec = pd.DataFrame(
                data['upgradeDowngradeHistory']['history'])
            rec['earningsDate'] = pd.to_datetime(
                rec['epochGradeDate'], unit='s')
            rec.set_index('earningsDate', inplace=True)
            rec.index.name = 'Date'
            rec.columns = helpers.camel2title(rec.columns)
            self._recommendations = rec[[
                'Firm', 'To Grade', 'From Grade', 'Action']].sort_index()
        except Exception:
            pass

        # get fundamentals
        financials = helpers.get_json(url + '/financials', proxy)
        # generic patterns
        for key in (
            (self._cashflow, 'cashflowStatement', 'cashflowStatements'),
            (self._balancesheet, 'balanceSheet', 'balanceSheetStatements'),
            (self._financials, 'incomeStatement', 'incomeStatementHistory')
        ):

            item = key[1] + 'History'
            if isinstance(financials.get(item), dict):
                key[0]['yearly'] = cleanup(financials[item][key[2]])

            item = key[1] + 'HistoryQuarterly'
            if isinstance(financials.get(item), dict):
                key[0]['quarterly'] = cleanup(financials[item][key[2]])

        # earnings
        if isinstance(financials.get('earnings'), dict):
            earnings = financials['earnings']['financialsChart']
            df = pd.DataFrame(earnings['yearly']).set_index('date')
            df.columns = helpers.camel2title(df.columns)
            df.index.name = 'Year'
            self._earnings['yearly'] = df

            df = pd.DataFrame(earnings['quarterly']).set_index('date')
            df.columns = helpers.camel2title(df.columns)
            df.index.name = 'Quarter'
            self._earnings['quarterly'] = df

        self._fundamentals = True

    def get_cashflow(self, as_dict=False, freq='yearly'):
        """Get the cash flow yearly or quarterly

        Parameters
        ----------
        as_dict : False
            if True return dict else return DataFrame
        freq : str
            Either yearly or quarterly, spelling sensitive but case insensitive

        Returns
        -------
        pandas.DataFrame
            DataFrame of the cashflow in the desired frequency
        """
        freq = freq.lower()
        if freq != 'yearly' and freq != 'quarterly':
            raise AttributeError("freq can only be 'yearly' or 'quarterly'.")

        if as_dict:
            return self._cashflow[freq].to_dict()
        return self._cashflow[freq]

    def get_earnings(self, as_dict=False, freq="yearly"):
        """Get the earning yearly or quarterly

        Parameters
        ----------
        as_dict : False
            if True return dict else return DataFrame
        freq : str
            Either yearly or quarterly, spelling sensitive but case insensitive

        Returns
        -------
        pandas.DataFrame
            DataFrame of the earning in the desired frequency
        """
        freq = freq.lower()
        if freq != 'yearly' and freq != 'quarterly':
            raise AttributeError("freq can only be 'yearly' or 'quarterly'.")
        if as_dict:
            return self._earnings[freq].to_dict()
        return self._earnings[freq]
    
    def get_balancesheet(self, as_dict=False, freq="yearly"):
        """Get the balancesheet yearly or quarterly

         Parameters
         ----------
         as_dict : False
             if True return dict else return DataFrame
         freq : str
             Either yearly or quarterly, spelling sensitive but case insensitive

         Returns
         -------
         pandas.DataFrame
             DataFrame of the earning in the desired frequency
         """
        freq = freq.lower()
        if freq != 'yearly' and freq != 'quarterly':
            raise AttributeError("freq can only be 'yearly' or 'quarterly'.")
        if as_dict:
            return self._balancesheet[freq].to_dict()
        return self._balancesheet[freq]
