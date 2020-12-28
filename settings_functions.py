
import pandas as pd
import numpy as np
import copy
from scipy.interpolate import interp1d

def define_default_settings(settings=None):
    # define simulation settings for portfolio simulation
    if settings is None:
        settings = {}

    if 'date_start' not in settings:
        settings['date_start'] = '2003-01-01'

    if 'date_end' not in settings:
        settings['date_end'] = '2020-09-30'

    # if 'solid_stock_type' not in settings:
    #     settings['solid_stock_type'] = 'index'
    #     # settings['solid_stock_type'] = 'cash'
    #     # settings['solid_stock_type'] = 'bond'
    #
    # if 'index_type' not in settings:
    #     # settings['solid_stock_type'] = 'S&P500'
    #     settings['solid_stock_type'] = 'NDX100'
    #     # settings['solid_stock_type'] = 'TLT'
    #     # settings['solid_stock_type'] = 'TMF'

    if 'portfolio_fractions' not in settings:
        settings['portfolio_fractions'] = {}
        settings['portfolio_fractions']['SP500'] = 1.0

    if 'initial_investment' not in settings:
        settings['initial_investment'] = 1
        # settings['initial_investment'] = 20

    if 'periodic_investment' not in settings:
        # settings['periodic_investment'] = 1
        settings['periodic_investment'] = 0

    if 'periodic_investment_interval' not in settings:
        settings['periodic_investment_interval'] = 'monthly'
        # settings['periodic_investment_interval'] = 'quarterly'
        # settings['periodic_investment_interval'] = 'yearly'

    if 'leverage_factor' not in settings:
        # settings['leverage_factor'] = 2
        settings['leverage_factor'] = 3

    if 'capital_gains_tax_percents' not in settings:
        settings['capital_gains_tax_percents'] = 25

    if 'num_days_in_year' not in settings:
        settings['num_days_in_year'] = 365

    if 'num_trading_days_in_year' not in settings:
        settings['num_trading_days_in_year'] = 252

    return settings
