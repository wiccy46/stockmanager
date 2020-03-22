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

import requests
from . import helpers


VALID_PERIOD = ['1d', '5d', '1mo', '3mo', '6mo',
                '1y', '2y', '5y', '10y', 'ytd', 'max']
VALID_INTERVAL = ['1m', '2m', '5m', '15m', '30m', '60m',
                  '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']


class StockBase():
    """Base class of stockmanager, here it holds all basic infomation of a particular
    ticker. The information is requested from Yahoo Finance.

    Attributes
    ----------
    ticker : str
        ticker, e.g. Microsoft is MSFT.
    _base_url : str
        https://query1.finance.yahoo.com
    _scrape_url : str
        https://finance.yahoo.com/quote




    """

    # TODO add proxy
    def __init__(self, ticker):
        """ticker is a string name of the stock"""
        self.ticker = ticker.upper()
        self._base_url = 'https://query1.finance.yahoo.com'
        self._scrape_url = 'https://finance.yahoo.com/quote'
        self._fundamentals = False  # TODO to be added with get_fundamental()
        self._recommendations = None  # TODO to be decided whether this necessary
        self._institutional_holders = None
        self._sustainability = None
        self._calendar = None
        self._expirations = {}
        self._info = None

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

    # def get_recent(self, days=7):
    #     # TODO this is unnecessary
    #     today = datetime.datetime.date(datetime.datetime.now())
    #     previous = today - datetime.timedelta(days=days + 1)
    #     return self.get_stock_info(start=previous.strftime("%Y-%m-%d"), end=today.strftime("%Y-%m-%d"))

    def get_price(self, period="1mo", interval="1d",
                  start=None, end=None, timezone=None):
        """Return a DataFrame of the ticker based on certain period and interval

        Examples
        --------
        Two ways of choosing the time range, 1) using period 2) start/end::

            from stockmanager import StockBase

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
            TODO.
        """
        import pdb
        pdb.set_trace()
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
                end = pd.to_datetime(end) + datetime.timedelta(days=1) # This is to include end date
                end = int(end.timestamp())
            elif isinstance(end, datetime.datetime):
                end = int(time.mktime(end.timetuple()))
            else:
                raise(TypeError("end must be None, str, or datetime.dateime"))

            params = {"period1": start, "period2": end}
        else:
            period = period.lower()
            params = {"range": period}

        params["interval"] = interval.lower()
        url = "{}/v8/finance/chart/{}".format(self._base_url, self.ticker)
        content = requests.get(url=url, params=params)

        if "Will be right back" in content.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n")
        content = content.json()
        # TODO deal with errors:

        try: 
            df = helpers.create_df(content["chart"]["result"][0], timezone)
        except Exception:
            raise RuntimeError("Error parsing content.")

        df.dropna(inplace=True)
        self._df = df.copy()
        return df

    @property
    def df(self):
        return self._df

    def _get_fundamentals(self, kind=None, proxy=None):
        """"This part scrap information from the Yahoo Finance: 
        https://finance.yahoo.com/quote/YOUR_TICKER 

        It will try to get all fundamental information for more info than just prices.
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
        url = '%s/%s' % (self._scrape_url, self.ticker)
        data = helpers.get_json(url, proxy)

        # holders
        url = "{}/{}/holders".format(self._scrape_url, self.ticker)

        holders = pd.read_html(url)
        self._major_holders = holders[0]
        self._institutional_holders = holders[1]
        if 'Date Reported' in self._institutional_holders:
            self._institutional_holders['Date Reported'] = pd.to_datetime(
                self._institutional_holders['Date Reported'])

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

        # info (be nice to python 2)
        self._info = {}
        items = ['summaryProfile', 'summaryDetail', 'quoteType',
                 'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
        for item in items:
            if isinstance(data.get(item), dict):
                self._info.update(data[item])

        self._info['regularMarketPrice'] = self._info['regularMarketOpen']
        self._info['logo_url'] = ""
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
        data = helpers.get_json(url + '/financials', proxy)

        # generic patterns
        for key in (
            (self._cashflow, 'cashflowStatement', 'cashflowStatements'),
            (self._balancesheet, 'balanceSheet', 'balanceSheetStatements'),
            (self._financials, 'incomeStatement', 'incomeStatementHistory')
        ):

            item = key[1] + 'History'
            if isinstance(data.get(item), dict):
                key[0]['yearly'] = cleanup(data[item][key[2]])

            item = key[1] + 'HistoryQuarterly'
            if isinstance(data.get(item), dict):
                key[0]['quarterly'] = cleanup(data[item][key[2]])

        # earnings
        if isinstance(data.get('earnings'), dict):
            earnings = data['earnings']['financialsChart']
            df = pd.DataFrame(earnings['yearly']).set_index('date')
            df.columns = helpers.camel2title(df.columns)
            df.index.name = 'Year'
            self._earnings['yearly'] = df

            df = pd.DataFrame(earnings['quarterly']).set_index('date')
            df.columns = helpers.camel2title(df.columns)
            df.index.name = 'Quarter'
            self._earnings['quarterly'] = df

        self._fundamentals = True
        
    def get_general_info(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy)
        info = self._recommendations
        if as_dict:
            return info.to_dict()
        return info
    
    def get_earnings(self, proxy=None, as_dict=False, freq="yearly"):
        # Currently no information
        self._get_fundamentals(proxy)
        data = self._earnings[freq]
        if as_dict:
            return data.to_dict()
        return data
    
    def get_balancesheet(self, proxy=None, as_dict=False, freq="yearly"):
        # Currently no information
        self._get_fundamentals(proxy)
        data = self._balancesheet[freq]
        if as_dict:
            return data.to_dict()
        return data
            
    @property
    def company_info(self):
        return self._info     
