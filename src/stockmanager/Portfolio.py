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
    # Add database version. 

    def __init__(self, read_file=None):
        #         self.path = './' if not data_folder else self._set_data_folder(data_folder)
        self._summary_colnames = ['Symbol', 'Name', 'Exchange', 'Holdings',
                                  'Price at Registration', 'Currency', 'Date']
        self.summary = pd.DataFrame(columns=self._summary_colnames)  # create an empty frame
        self._trade_record_colnames = ['Symbol', 'Sell', 'Buy', 'Price', 'Date', 'Total Sell', 'Total Buy']
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
            # Maybe this is not necessary
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
            to_append = [self.symbol, self.ticker.name, self.ticker.company_information['exchange'],
                         self.holdings, self.ticker.current_price, self.ticker.currency, now]
            df_len = len(self.summary)
            self.summary.loc[df_len] = to_append

    # def remove(self):
    #     # TODO remove a record in the summary. But put the remove data in a buffer for recovery
    #     pass

    def load(self, summary_path=None, record_path=None):
        """Load summary and record file. You can have a saved summary and record
        data using the save() method. The load method will load self.summary and 
        self.record if the file path is valid. 

        Parameters
        ----------
        summary_path : str, optional
            path including filename of the summary data. 
        record_path : str, optional
            path including filename of the record data.
        """
        if not summary_path and not record_path:
            raise AttributeError("No file given for either summary or record")
        if summary_path:
            self.summary = pd.read_csv(summary_path)
        if record_path:
            self.record = pd.read_csv(record_path)

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
            summary_name = ''.join(['summary.', format])
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


#     def _varify_folder(self):
#         """check if data folder exist if not create one."""
#         fn = [n.replace(self.path, '') for n in glob(self.path + '*/')]
#         if 'data/' in fn:
#             self.sub_path = self.path + 'data/'
#             self.stock_info_path = self.sub_path + 'stock_info/'
#             self.stock_record_path = self.sub_path + 'stock_record/'
#             # Remove the relative path in the string.
#             sub_fn = [n.replace(sub_path, '') for n in glob(sub_path + '*/')]
#             if 'stock_info/' not in sub_fn:
#                 _LOGGER.info("stock_info folder not found.")
#                 try:
#                     mkdir(sub_path + 'stock_info/')
#                 except OSError:
#                     raise OSError("Failed to create directory, check if path valid")

#             if 'stock_record/' not in sub_fn:
#                 _LOGGER.info("stock_record folder not found.")
#                 try:
#                     mkdir(sub_path + 'stock_record/')
#                 except OSError:
#                     raise OSError("Failed to create directory, check if path valid")
#         else:
#             try:
#                 mkdir(path + 'data/')
#                 mkdir(path + 'data/stock_info/')
#                 mkdir(path + 'data/stock_record/')
#             except OSError:
#                 raise OSError("Failed to create directory, check if path valid. ")

#     def _set_data_folder(self, path):
#         """Set the path Trade_Manager should look for
#         loading and storing stock info and trade record

#         Parameters
#         ----------
#         path : str
#             path to the data folder. If "data" folder not exist then create a folder.
#         """
#         pass

#     def load_csv(self, path, overwrite=False):
#         """The method look through the directory for all csv files and load them as your
#         trading recording dictionary. Each csv file is your record of a particular stock.
#         It will use the filename as the key, and the DataFrame converted from csv as values.
#         Results are updated/overwrite to self.record.

#         Parameters
#         ----------
#         path : str
#             Path of the folder, it will only load the csv files.

#         overwrite : bool
#             If true, overwrite self.record. Else, merge it instead

#         """
#         if not self.record:
#             self.record = pd.from_csv(path)
#         else:
#             if overwrite:
#                 self.record = pd.from_csv(path)
#             else:
#                 self.merge(pd.from_csv(path))

