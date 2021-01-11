
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

    if 'ideal_portfolio_fractions' not in settings:
        settings['ideal_portfolio_fractions'] = {}
        settings['ideal_portfolio_fractions']['SP500'] = 1.0

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

    if 'rebalance_criterion' not in settings:
        settings['rebalance_criterion'] = 'percent_deviation'
        # settings['rebalance_criterion'] = 'quarterly'
        # settings['rebalance_criterion'] = 'yearly'
        # settings['rebalance_criterion'] = 'yearly'

    if 'rebalance_percent_deviation' not in settings:
        settings['rebalance_percent_deviation'] = 10.0
        # settings['rebalance_percent_deviation'] = 5.0

    if 'leverage_factor' not in settings:
        # settings['leverage_factor'] = 2
        settings['leverage_factor'] = 3

    if 'tax_scheme' not in settings:
        settings['tax_scheme'] = 'FIFO'
        # settings['tax_scheme'] = 'LIFO'
        # settings['tax_scheme'] = 'optimized'

    if 'capital_gains_tax_percents' not in settings:
        settings['capital_gains_tax_percents'] = 25
        # settings['capital_gains_tax_percents'] = 0

    if 'transaction_fee_percents' not in settings:
        # settings['transaction_fee_percents'] = 1.0
        settings['transaction_fee_percents'] = 0.1
        # settings['transaction_fee_percents'] = 0

    if 'num_days_in_year' not in settings:
        settings['num_days_in_year'] = 365

    if 'num_trading_days_in_year' not in settings:
        settings['num_trading_days_in_year'] = 252

    # monte carlo related settings

    if 'perform_bootstrap' not in settings:
        settings['perform_bootstrap'] = False

    if 'num_correlation_days' not in settings:
        settings['num_correlation_days'] = 5

    if 'synthetic_period_years' not in settings:
        # settings['synthetic_period_years'] = 10
        settings['synthetic_period_years'] = 35

    return settings
