import pytest
import stockmanager 
from unittest import mock
import os
from pandas import read_csv, to_datetime


# path = ''.join([os.path.dirname(os.path.abspath(__file__)), '/dummy_data/dummy_price.csv'])
# df = read_csv(path, index_col=0)
# df['Datetime'] = to_datetime(df.index)
# df = df.set_index('Datetime')

@mock.patch('stockmanager.visualization.mpf.plot')
def test_plot_mplbackend(pathplot, dummy_price):
    stockmanager.visualization.plot_price(dummy_price)


@mock.patch('stockmanager.visualization.go.Figure')
@mock.patch('stockmanager.visualization.go.Figure.add_trace')
def test_plot_plotly_backend(fig, figat, dummy_price):
    stockmanager.visualization.plot_price(dummy_price, backend='plotly')


