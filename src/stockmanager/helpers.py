import pandas as pd 
import numpy as np 
import re
import requests

try:
    import ujson as _json
except ImportError:
    import json as _json


def empty_df(index=[]):
    empty = pd.DataFrame(index=index, data={
        'Open': np.nan, 'High': np.nan, 'Low': np.nan,
        'Close': np.nan, 'Adj Close': np.nan, 'Volume': np.nan})
    empty.index.name = 'Date'
    return empty


def create_df(data, timezone=None):
    timestamps = data["timestamp"]
    all_prices = data["indicators"]["quote"][0]

    adjclose = all_prices["close"]
    if "adjclose" in data["indicators"]:
        adjclose = data["indicators"]["adjclose"][0]["adjclose"]

    quotes = pd.DataFrame({"Open": all_prices["open"],
                           "High": all_prices["high"],
                           "Low": all_prices["low"],
                           "Close": all_prices["close"],
                           "Adj Close": adjclose,
                           "Volume": all_prices["volume"]})

    quotes.index = pd.to_datetime(timestamps, unit="s")
    quotes.sort_index(inplace=True)

    if timezone is not None:
        quotes.index = quotes.index.tz_localize(timezone)
    return quotes


def camel2title(o):
    return [re.sub("([a-z])([A-Z])", r"\g<1> \g<2>", i).title() for i in o]


def get_json(url, proxy=None):
    html = requests.get(url=url, proxies=proxy).text

    if "QuoteSummaryStore" not in html:

        html = requests.get(url=url, proxies=proxy).text
        if "QuoteSummaryStore" not in html:
            return {}

    json_str = html.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()
    data = _json.loads(json_str)[
        'context']['dispatcher']['stores']['QuoteSummaryStore']

    # return data
    new_data = _json.dumps(data).replace('{}', 'null')
    new_data = re.sub(
        r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)\}', r'\1', new_data)

    return _json.loads(new_data)