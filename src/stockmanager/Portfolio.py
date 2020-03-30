from .Ticker import Ticker
import pandas as pd
from glob import glob
from os import mkdir
from time import strftime
import logging
_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Portfolio(object):
    """Porfolio is a class help you keep track of your trade record, holders, profit of multiple tickers, save record
    as a csv.

    There are two ways, you can either instantiate a new manager or pull a prerecorded record file.

    Examples
    --------

    """

    def __init__(self, read_file=None):
        #         self.path = './' if not data_folder else self._set_data_folder(data_folder)
        self._summary_colnames = ['Name', 'Symbol', 'Exchange', 'Holdings',
                                  'Price at Registration', 'Currency', 'Time of Entry']
        self.summary = pd.DataFrame(columns=self._summary_colnames)  # create an empty frame
        self._trade_record_colnames = ['Name', 'Symbol', 'Exchange', 'Type',
                                       'Amount', 'Price', 'Total value']
        self.trade_record = pd.DataFrame(columns=self._trade_record_colnames)
        self.ticker = None

    def add(self, symbol, holdings, date='now', from_csv=None, overwite=False):
        """A new record, this will overwrite whatever the current one. """
        if not isinstance(symbol, str) or not isinstance(holdings, int):
            raise TypeError("symbol needs to be str and holdings need to be int")
        else:
            # Maybe this is not necessary
            self.symbol = symbol
            self.holdings = holdings
            try:
                self.ticker = Ticker(self.symbol)
            except:  # Can have multiple exception possibilities
                raise (AttributeError("symbol not recognise, please use a valid ticker symbol"))

        now = strftime("%Y-%m-%d %H:%M")

        if self.symbol in self.summary.Symbol.values:
            self.summary.loc[self.summary['Symbol'] == self.symbol, ['Holdings']] = \
                self.summary.loc[self.summary['Symbol'] == self.symbol, ['Holdings']].Holdings[0] + self.holdings
        else:
            # Append to the last row.
            to_append = [self.ticker.name, self.symbol, self.ticker.company_information['exchange'],
                         self.holdings, self.ticker.current_price, self.ticker.currency, now]
            df_len = len(self.summary)
            self.summary.loc[df_len] = to_append

    def load(self, filepath, format='csv'):
        if format == 'csv':
            self.summary = pd.read_csv(filepath)
            return self
        else:
            raise AttributeError("Unsupported format, currently support: csv")

    def save(self, filepath, format='csv'):
        if format == 'csv':
            self.summary.to_csv(filepath)
            return self

    def register_trade(self, type, symbol, amount, price=None, price_at_time=None,
                       update_summary=True):
        """Register a trade record. """
        if not isinstance(type, str) or not isinstance(symbol, str) or not isinstance(amount, int):
            raise TypeError("type can only be buy or sell, or b and s, "
                            "symbol needs to be str and amount need to be int")
        type = type.lower()
        ticker = Ticker(symbol)
        self._trade_record_colnames = ['Name', 'Symbol', 'Exchange', 'Type',
                                       'Amount', 'Price', 'Total value']
        value = price * amount
        to_append = [ticker.name, self.symbol, ticker.company_information['exchange'],
                     type, amount, price, value]
        df_len = len(self.trade_record)
        self.trade_record.loc[df_len] = to_append
        if update_summary:
            # update self.summary here
            pass


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

#     def save(self, ticker=None):
#         """If you dont sepecify a ticker, save all to the dedicated data folder.
#         """
#         for key, value in self.record.items():
#             value.to_csv(self.stock_record_path + key + ".csv")

#     def merge(self, pd):
#         """Merge a new df to existing record. Take care of duplicate"""
#         return pd  # TODO add actual method.

#     def add_new_stock(self, ticker, name, holding, date, currency):
#         pass

#     def add_entry(self, ticker, amount, price, typ, name=None, date='today', ):
#         """add a buy/sell entry to the record.

#         Parameters
#         ----------
#         ticker : str
#             Ticker of the stock, this can later be used to request updated market info
#         amount : int
#             The amount of stocks in transaction
#         price : float
#             Price at the transaction
#         typ : str
#             Either 'buy' or 'sell'
#         name : None or str
#             If not set, try to find the name correspond to ticker.
#         date : str
#             By default it will get today as the transaction date, or yyyy-mm-dd format string.
#         """
#         typ = typ.lower()

