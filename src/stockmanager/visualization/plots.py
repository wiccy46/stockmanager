# All the visualization modules
# Should support both matplotlib and plotly backend.
import mplfinance as mpf
import plotly.graph_objects as go
from ..helpers import get_ohlc
from ._arg_validator import _process_kwargs, _valid_plot_kwargs


# Backend should be set before that.
def plot_price(price, backend='matplotlib', **kwargs):
    backend = backend.lower()
    if backend not in ('plotly', 'matplotlib'):
        raise AttributeError("Only accept matplotlib and plotly backend.")

    if backend == 'matplotlib':
        price_plot_with_matplotlib(price, **kwargs)

    else:
        fig = price_plot_with_plotly(price, **kwargs)
        return fig


def price_plot_with_matplotlib(price, **kwargs):
    """Based on mplfinance. But this is not interactive

    Parameters
    ----------
    price : pd.DataFrame
        price data frame
    """
    mpf.plot(price, **kwargs)


def price_plot_with_plotly(price, **kwargs):
    """Use plotly for interactive plot.

    Parameters
    ----------
    price : pd.DataFrame
        price data frame
    """
    show_hours = True
    has_ohlc, ohlc = get_ohlc(price)  # Get ohlc for

    config = _process_kwargs(kwargs, _valid_plot_kwargs())

    if show_hours:
        timeline_str = [p.strftime("%y-%m-%d (%H:%M:%S)") for p in price.index.to_list()]
    else:
        timeline_str = [p.strftime("%y-%m-%d") for p in price.index.to_list()]

    fig = go.Figure()
    if config['type'] == 'line':
        fig.add_trace(go.Scatter(x=timeline_str, y=price.Close,
                                 line=dict(color='royalblue')))
    elif config['type'] == 'candle' or config['type'] == 'candlestick':
        if has_ohlc:
            fig.add_trace(go.Candlestick(x=timeline_str,
                                         open=ohlc[0],
                                         high=ohlc[1],
                                         low=ohlc[2],
                                         close=ohlc[3]))
        else:
            raise AttributeError('Try to plot ohlc candlestick but the data has no ohlc columns')

    fig.update_layout(title={'text': config['title'],
                             'xanchor': 'auto'},
                      yaxis_title='Price', xaxis=dict(tickangle=-90))
    # fig.show()
    return fig
