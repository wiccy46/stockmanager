# Since mplfinance doesn't make arg_validator public, I copied to code. so that the same arguments can
# be shared on plotly backend.
# Link to original file: https://github.com/matplotlib/mplfinance/blob/master/src/mplfinance/_arg_validators.py
import warnings
import matplotlib.colors as mcolors
import io


# TODO, This can be greatly simplify just for this particular package.


def _warn_no_xgaps_deprecated(value):
    msg = "`no_xgaps` is deprecated:"\
          "Default value is now `no_xgaps=True`"\
          "However, to set `no_xgaps=False` and silence this warning,"\
          "use instead: `show_nontrading=True`."
    warnings.warn(msg, category=DeprecationWarning)
    return isinstance(value, bool)


def _mav_validator(mav_value):
    '''
    TODO can probably make it more flexible.

    Value for mav (moving average) keyword may be:
    scalar int greater than 1, or tuple of ints, or list of ints (greater than 1).
    tuple or list limited to length of 7 moving averages (to keep the plot clean).
    '''
    if isinstance(mav_value, int) and mav_value > 1:
        return True
    elif not isinstance(mav_value, tuple) and not isinstance(mav_value, list):
        return False

    if not len(mav_value) < 8:
        return False
    for num in mav_value:
        if not isinstance(num, int) and num > 1:
            return False
    return True


def _kwarg_not_implemented(value):
    ''' If you want to list a kwarg in a valid_kwargs dict for a given
        function, but you have not yet, or don't yet want to, implement
        the kwarg; or you simply want to (temporarily) disable the kwarg,
        then use this function as the kwarg validator
    '''
    raise NotImplementedError('kwarg NOT implemented.')


def _validate_vkwargs_dict(vkwargs):
    # Check that we didn't make a typo in any of the things
    # that should be the same for all vkwargs dict items:
    for key, value in vkwargs.items():
        if len(value) != 2:
            raise ValueError('Items != 2 in valid kwarg table, for kwarg "' + key + '"')
        if 'Default' not in value:
            raise ValueError('Missing "Default" value for kwarg "' + key + '"')
        if 'Validator' not in value:
            raise ValueError('Missing "Validator" function for kwarg "' + key + '"')


def _valid_plot_kwargs():
    '''
    Construct and return the "valid kwargs table" for the mplfinance.plot() function.
    A valid kwargs table is a `dict` of `dict`s.  The keys of the outer dict are the
    valid key-words for the function.  The value for each key is a dict containing
    2 specific keys: "Default", and "Validator" with the following values:
        "Default"      - The default value for the kwarg if none is specified.
        "Validator"    - A function that takes the caller specified value for the kwarg,
                         and validates that it is the correct type, and (for kwargs with
                         a limited set of allowed values) may also validate that the
                         kwarg value is one of the allowed values.
    '''

    vkwargs = {
        'type': {'Default': 'ohlc',
                 'Validator': lambda value: value in ['candle', 'candlestick', 'ohlc', 'bars', 'ohlc_bars', 'line',
                                                      'renko']},

        'volume': {'Default': False,
                   'Validator': lambda value: isinstance(value, bool)},

        'mav': {'Default': None,
                'Validator': _mav_validator},

        'renko_params': {'Default': dict(),
                         'Validator': lambda value: isinstance(value, dict)},

        'study': {'Default': None,
                  # 'Validator'   : lambda value: isinstance(value,dict) }, #{'studyname': {study parms}} example: {'TE':{'mav':20,'upper':2,'lower':2}}
                  'Validator': lambda value: _kwarg_not_implemented(value)},

        'marketcolors': {'Default': None,  # use 'style' for default, instead.
                         'Validator': lambda value: isinstance(value, dict)},

        'no_xgaps': {'Default': True,  # None means follow default logic below:
                     'Validator': lambda value: _warn_no_xgaps_deprecated(value)},

        'show_nontrading': {'Default': False,
                            'Validator': lambda value: isinstance(value, bool)},

        'figscale': {'Default': 1.0,  # scale base figure size up or down.
                     'Validator': lambda value: isinstance(value, float) or isinstance(value, int)},

        'figratio': {'Default': (8.00, 5.75),  # aspect ratio; will equal fig size when figscale=1.0
                     'Validator': lambda value: isinstance(value, (tuple, list)) and len(value) == 2 and isinstance(value[0], (float, int)) and isinstance(value[1], (float, int))},

        'linecolor': {'Default': 'k',  # line color in line plot
                      'Validator': lambda value: mcolors.is_color_like(value)},

        'title': {'Default': None,  # Plot Title
                  'Validator': lambda value: isinstance(value, str)},

        'ylabel': {'Default': 'Price',  # y-axis label
                   'Validator': lambda value: isinstance(value, str)},

        'ylabel_lower': {'Default': None,  # y-axis label default logic below
                         'Validator': lambda value: isinstance(value, str)},

        # 'xlabel'      : { 'Default'     : None,  # x-axis label, default is None because obvious it's time or date
        #                  'Validator'   : lambda value: isinstance(value,str) },

        'addplot': {'Default': None,
                    'Validator': lambda value: isinstance(value, dict) or (isinstance(value, list) and all([isinstance(d, dict) for d in value]))},

        'savefig': {'Default': None,
                    'Validator': lambda value: isinstance(value, dict) or isinstance(value, str) or isinstance(value, io.BytesIO)},

        'block': {'Default': True,
                  'Validator': lambda value: isinstance(value, bool)},

        'returnfig': {'Default': False,
                      'Validator': lambda value: isinstance(value, bool)},

        'return_calculated_values': {'Default': None,
                                     'Validator': lambda value: isinstance(value, dict) and len(value) == 0},

    }

    _validate_vkwargs_dict(vkwargs)

    return vkwargs


def _process_kwargs(kwargs, vkwargs):
    '''
    Given a "valid kwargs table" and some kwargs, verify that each key-word
    is valid per the kwargs table, and that the value of the kwarg is the
    correct type.  Fill a configuration dictionary with the default value
    for each kwarg, and then substitute in any values that were provided
    as kwargs and return the configuration dictionary.
    '''
    # initialize configuration from valid_kwargs_table:
    config = {}
    for key, value in vkwargs.items():
        config[key] = value['Default']

    # now validate kwargs, and for any valid kwargs
    #  replace the appropriate value in config:
    for key in kwargs.keys():
        if key not in vkwargs:
            raise KeyError('Unrecognized kwarg="' + str(key) + '"')
        else:
            value = kwargs[key]
            try:
                valid = vkwargs[key]['Validator'](value)
            except Exception as ex:
                ex.extra_info = 'kwarg "' + key + '" validator raised exception to value: "' + str(value) + '"'
                raise
            if not valid:
                import inspect
                v = inspect.getsource(vkwargs[key]['Validator']).strip()
                raise TypeError(
                    'kwarg "' + key + '" validator returned False for value: "' + str(value) + '"\n    ' + v)
        config[key] = value

    return config
