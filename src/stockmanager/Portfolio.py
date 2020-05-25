""" Portfolio class. 
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

from .Ticker import Ticker
import pandas as pd
from glob import glob
import os
from os import mkdir
from time import strftime
import logging
_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Portfolio(object):
    """Porfolio is a class help you keep track of your trade record, holders,
    profit of multiple tickers, save record
    as a csv.

    There are two ways, you can either instantiate a new manager
    or pull a prerecorded record file.

    Examples
    --------

    """
    # TODO what happen if holding is reduced to 0, move holding to history
    # TODo take agency fee into account
    def __init__(self, read_file=None):
        self._summary_colnames = ['Symbol', 'Name', 'Exchange', 'Holdings',
                                  'Price at Registration', 'Currency', 'Date']
        # create an empty frame
        self.summary = pd.DataFrame(columns=self._summary_colnames)
        self._trade_record_colnames = ['Symbol', 'Sell', 'Buy', 'Price',
                                       'Date', 'Total Sell', 'Total Buy']
        self.record = pd.DataFrame(columns=self._trade_record_colnames)
        self.ticker = None
        self._remove_buffer = None

    @staticmethod
    def get_now():
        return strftime("%d.%m.%Y %H:%M")

    def add(self, symbol, holdings, date='now'):
        """A new record, this will overwrite whatever the current one.

        Parameters
        ----------
        symbol : str
            Ticker symbol
        holdings : int
            The amount of holdings to add.
        date : string. Optional
            Date information. Default is the current time of call
        """
        if not isinstance(symbol, str) or not isinstance(holdings, int):
            raise TypeError("symbol needs to be str and holdings need to be int")
        else:
            self.symbol = symbol
            self.holdings = holdings
            try:
                self.ticker = Ticker(self.symbol)
                self.ticker.get_fundamentals()
            except:  # Can have multiple exception possibilities
                raise (AttributeError("symbol not recognise, please use a valid ticker symbol"))

        now = self.get_now()
        if self.symbol in self.summary.Symbol.values:
            self.summary.loc[self.summary['Symbol'] == self.symbol, ['Holdings']] = \
                self.summary.loc[self.summary['Symbol'] == self.symbol, ['Holdings']].Holdings[0] + self.holdings
        else:
            # Append to the last row.
            to_append = [self.symbol, self.ticker.name,
                         self.ticker.company_information['exchange'],
                         self.holdings, self.ticker.current_price,
                         self.ticker.currency, now]
            df_len = len(self.summary)
            self.summary.loc[df_len] = to_append

    def remove(self, symbol):
        """Remove an stock from summary
        
        Parameters
        ----------
        symbol : str or list
            Ticker symbol(s) to be removed.
        """
        if isinstance(symbol, str):
            self.summary = self.summary[self.summary.Symbol != symbol]
        elif hasattr(symbol, '__iter__'):
            for s in symbol:
                self.summary = self.summary[self.summary.Symbol != s]
        else:
            raise TypeError("symbol must be str or list.")

    def load(self, summary_path='./portfolio.csv', record_path='./record.csv'):
        """Load summary and record file. You can have a saved summary and record
        data using the save() method. The load method will load self.summary and 
        self.record if the file path is valid. 

        Parameters
        ----------
        summary_path : str, optional
            path including filename of the summary data. By default it tries to
            look for porfolio.csv in the current directory.
        record_path : str, optional
            path including filename of the record data. By default it tries to
            look for record.csv in the current directory.
        """
        self.summary = pd.read_csv(summary_path)
        self.record = pd.read_csv(record_path)
        return self

    def save(self, filepath='./', summary_name=None,
             record_name=None, format='csv', index=False):
        """Save summary and trade record to files

        Parameters
        ----------
        filepath : str, optional
            Directory path, should end with /. Default is current directory.
        format : str, optional
            By default it will save as csv. #TODO add more date formats
        index : bool, optional
            Whether the dataframe index will be save as an extra column. Default is False
        """
        if filepath == '.':
            filepath = './'
        if summary_name is not None:
            if '.' in summary_name:
                raise AttributeError("use filename without extension")
            summary_name = ''.join([summary_name, '.', format])
        else:
            summary_name = ''.join(['portfolio.', format])
        if record_name is not None:
            if '.' in record_name:
                raise AttributeError("use filename without extension")
            record_name = ''.join([record_name, '.', format])
        else:
            record_name = ''.join(['records.', format])
        if format == 'csv':
            self.summary.to_csv(os.path.join(filepath, summary_name), index=index)
            self.record.to_csv(os.path.join(filepath, record_name), index=index)
            return self

    def trade(self, typ, symbol, amount, fee=None, price=None, update_summary=True):
        """Register a trade record.

        Parameters
        ----------
        typ : str
            Can only be 'buy' or 'sell'
        symbol : str
            Ticker symbol
        amount : int
            Trade amount
        fee : float or int, optional
            The amount of fee in the same currency. This is not fee ratio but the absolute value.
        price : float, optional
            Price at sell. If not specified, it will try to get the current price
        update_summary : bool, optional
            If True, will update self.summary
        """
        typ = typ.lower()
        _ticker = Ticker(symbol)
        _register_price = price or _ticker.current_price
        _fee = fee or 0.
        if typ == 'buy':
            _buy = int(amount)
            _sell = 0
            _delta = int(amount)
        elif typ == 'sell':
            _sell = int(amount)
            _buy = 0
            _delta = -1 * (amount)
        else:
            raise ValueError("typ can only be either buy or sell, case insensitive.")

        _total_buy = _buy * _register_price - _fee
        _total_sell = _sell * _register_price - _fee
        _now = self.get_now()
        to_append = [symbol, _sell, _buy, _register_price, _now, _total_sell, _total_buy]
        df_len = len(self.record)
        self.record.loc[df_len] = to_append
        self.record.sort_values(by=['Symbol', 'Time'], inplace=True)
        if update_summary:
            # update self.summary here
            # Check if summary has this:
            if symbol in set(self.summary['Symbol']):
                self.summary.loc[self.summary['Symbol'] == symbol, ['Holdings']] = \
                    self.summary.loc[self.summary['Symbol'] == symbol, ['Holdings']].Holdings[0] + _delta
                self.summary.loc[self.summary['Symbol'] == symbol, ['Price at Registration']] = _register_price
                self.summary.loc[self.summary['Symbol'] == symbol, ['Date']] = _now
            else:
                _LOGGER.warning("Symbol not in the summary. Register one for you")