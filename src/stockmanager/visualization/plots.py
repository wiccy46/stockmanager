# All the visualization modules
# Should support both matplotlib and plotly backend.
import mplfinance as mpf
import plotly.graph_objects as go
from ..helpers import get_ohlc
from ._arg_validator import _process_kwargs, _valid_plot_kwargs
from itertools import cycle


# Backend should be set before that.
def plot_price(price, backend='matplotlib', **kwargs):
    """Plot price, by default use matplotlib's mplfinance as backend and ohlc as type.

    Parameters
    ----------
    price : pd.DataFrame
        price data frame
    backend : str
        matplotlib or plotly

    Other Parameters
    ----------------
    type : str
        'candle', 'candlestick', 'ohlc' or 'bars', 'line'
    title : str
        Title of the plot, suggest to use ticker.name
    mav : int or list
        Average, if list multiple mavg lines will be drawn
    """

    backend = backend.lower()
    if backend not in ('plotly', 'matplotlib'):
        raise AttributeError("Only accept matplotlib and plotly backend.")

    if backend == 'matplotlib':
        price_plot_with_matplotlib(price, **kwargs)
    else:
        price_plot_with_plotly(price, **kwargs)


def price_plot_with_matplotlib(price, **kwargs):
    """Based on mplfinance. But this is not interactive

    Parameters
    ----------
    price : pd.DataFrame
        price data frame
    """
    mpf.plot(price, **kwargs)


def price_plot_with_plotly(price, show_hours=True, **kwargs):
    """Use plotly for interactive plot.

    Parameters
    ----------
    price : pd.DataFrame
        price data frame
    """
    has_ohlc, ohlc = get_ohlc(price)  # Get ohlc for
    config = _process_kwargs(kwargs, _valid_plot_kwargs())
    config['type'] = config['type'].lower()  # Relax the spelling.
    # style = config['style']

    if show_hours:
        timeline_str = [p.strftime("%y-%m-%d (%H:%M:%S)") for p in price.index.to_list()]
    else:
        timeline_str = [p.strftime("%y-%m-%d") for p in price.index.to_list()]

    fig = go.Figure()
    if config['type'] == 'line':
        fig.add_trace(go.Scatter(x=timeline_str, y=price.Close,
                                 line=dict(color='royalblue'), name='Price'))
    elif config['type'] == 'candle' or config['type'] == 'candlestick':
        if has_ohlc:
            fig.add_trace(go.Candlestick(x=timeline_str,
                                         open=ohlc[0],
                                         high=ohlc[1],
                                         low=ohlc[2],
                                         close=ohlc[3],
                                         name='Price'))
        else:
            raise AttributeError('Try to plot candlestick but the data has no ohlc columns')
    elif config['type'] == 'ohlc' or config['type'] == 'bars':
        if has_ohlc:
            fig.add_trace(go.Ohlc(x=timeline_str,
                                  open=ohlc[0],
                                  high=ohlc[1],
                                  low=ohlc[2],
                                  close=ohlc[3],
                                  name='Price'))
        else:
            raise AttributeError('Try to plot ohlc but the data has no ohlc columns')

    mavgs = config['mav']
    if mavgs is not None:
        # Overlay moving average
        if isinstance(mavgs, int):
            mavgs = mavgs,  # convert to tuple
        if len(mavgs) > 7:
            mavgs = mavgs[0:7]  # take at most 7
        #
        # if style['mavcolors'] is not None:
        #     mavc = cycle(style['mavcolors'])
        # else:
        #     mavc = None

        for mav in mavgs:

            mavprices = price.Close.rolling(mav).mean().values
            # if mavc:
            #     ax1.plot(timeline_str, mavprices, color=next(mavc))
            # else:
            #     ax1.plot(timeline_str, mavprices)
            fig.add_trace(go.Scatter(x=timeline_str, y=mavprices,
                                     line=dict(color='royalblue'),
                                     name="MAvg " + str(mav)))

    fig.update_layout(title={'text': config['title'],
                             'xanchor': 'auto'},
                      yaxis_title='Price', xaxis=dict(tickangle=-90))
    fig.show()
