import pandas as pd
import numpy as np
import copy
from scipy.interpolate import interp1d
from data_functions import load_stock_data, get_dividend_yield, get_libor_rate, define_stock_parameters
from aux_functions import get_year_labels


def simulate_portfolio_evolution(settings):
    """
    Main function for the evolution of a portfolio
    """

    # load all necessary data for simulation
    data = load_data(settings)

    # initialize portfolio
    data = initialize_portfolio(settings, data)

    # loop over days of simulation
    # for date in data['dates']:
    # for ind_date range(1, len(data['dates']):
    for ind_date, date in enumerate(data['dates']):
        if ind_date > 0:
            # print('ind_date', ind_date)

            # evolve the portfolio elements with the passing day stock changes
            data = evolve_portfolio_single_day(settings, data, ind_date)

            # check if cash invest criterion reached, invest to try and balance
            # each buy is added to the portfolio for later
            if check_invest_criterion_reached(settings, data):
                data = add_cash_to_portfolio(settings, data)

            # check if rebalancing criterion reached
            # buy/sell according to strategy and update the portfolio
            # save date of operation to calculate statistics of opeartions frequency
            if check_rebalancing_criterion_reached(settings, data):
                data = rebalance_portfolio(settings, data)

            # calculate yearly gains
            data = calculate_yearly_gains(settings, data)

            # check if tax criterion reached (end of year), sell some to withdraw for tax
            # save cumulative amount of paid tax
            if check_tax_criterion_reached(settings, data):
                data = sell_portfolio_for_tax(settings, data)

        # calculate leveraged/solid portions of the total portfolio components
        data = calculate_portfolio_fractions(settings, data, ind_date)

    # end of simulation period reached, calculate profit if entire portfolio sold now
    data = calculate_total_portfolio_profit(settings, data)

    return data


def load_data(settings):
    data = {}

    # general stock parameters
    expense_ratios, leverage_factors, underlying_index, dividend_yield = define_stock_parameters()
    data['expense_ratios'] = expense_ratios
    data['leverage_factors'] = leverage_factors
    data['underlying_index'] = underlying_index
    data['dividend_yield'] = dividend_yield

    # define the dates axis that will be mutual for all the portfolio ingredients
    date_start = settings['date_start']
    date_end = settings['date_end']
    dates, _ = load_stock_data('SP500', date_start, date_end)
    inds_years, label_years = get_year_labels(dates)
    data['dates'] = dates
    data['inds_years'] = inds_years
    data['label_years'] = label_years

    # load libor_rate (relevant to leveraged etf sim)
    libor_rate = get_libor_rate(dates)
    data['libor_rate'] = libor_rate

    # stocks to be a part of the portfolio
    stock_names = settings['portfolio_fractions'].keys()
    # for stock_name in stock_names:
    # _, stock_values = load_stock_data(stock_name, date_start, date_end)
    for stock_name in stock_names:
        index_name = underlying_index[stock_name]
        _, stock_values = load_stock_data(index_name, date_start, date_end)
        data[stock_name] = stock_values

    return data

def initialize_portfolio(settings, data):
    # first purchase of stocks according to the required fractions

    papers = []  # will contain all the market purchases

    portfolio_fractions = settings['portfolio_fractions']
    stock_names = portfolio_fractions.keys()

    # check fraction add up to 100%
    if sum([portfolio_fractions[stock_name] for stock_name in stock_names]) != 1.0:
        raise ValueError('portfolio_fractions do not add up to 100%')

    for stock_name in stock_names:
        paper = {}
        paper['id'] = len(papers)
        paper['stock_name'] = stock_name
        paper['price'] = data[stock_name][0]
        paper['value'] = portfolio_fractions[stock_name] * settings['initial_investment']
        paper['date'] = data['dates'][0]
        paper['num_day'] = 0
        papers += [paper]
    data['papers'] = papers

    data['total_portfolio_value'] = np.nan * np.zeros(len(data['dates']))
    data['total_portfolio_value'][0] = settings['initial_investment']

    return data


def evolve_portfolio_single_day(settings, data, ind_date):
    # evolve each portfolio asset according to the stock it tracks
    # evolve the leveraged assets, after taking the cut of expense-ratio and loan-rate (LIBOR).

    papers = data['papers']
    expense_ratios = data['expense_ratios']
    leverage_factors = data['leverage_factors']
    dividend_yield = data['dividend_yield']

    # for paper in papers:
    for ind_paper, paper in enumerate(papers):
        stock_name = paper['stock_name']
        market_factor = data[stock_name][ind_date] / data[stock_name][ind_date - 1]
        expense_ratio_factor = 1.0 - expense_ratios[stock_name] / 100.0 / settings['num_trading_days_in_year']
        dividend_factor = 1.0 + dividend_yield[stock_name] / 100.0 / settings['num_trading_days_in_year']
        paper_factor = market_factor * expense_ratio_factor * dividend_factor
        papers[ind_paper]['value'] *= paper_factor

    data['papers'] = papers
    return data


def check_invest_criterion_reached(settings, data):
    # TODO
    return data


def add_cash_to_portfolio(settings, data):
    # TODO
    return data


def check_rebalancing_criterion_reached(settings, data):
    # TODO
    return data


def rebalance_portfolio(settings, data):
    # TODO
    return data


def calculate_yearly_gains(settings, data):
    # TODO
    return data


def check_tax_criterion_reached(settings, data):
    # TODO
    return data


def sell_portfolio_for_tax(settings, data):
    # TODO
    return data


def calculate_portfolio_fractions(settings, data, ind_date):
    # TODO

    papers = data['papers']

    total_portfolio_value = 0
    for ind_paper, paper in enumerate(papers):
        total_portfolio_value += papers[ind_paper]['value']

    data['total_portfolio_value'][ind_date] = total_portfolio_value

    return data


def calculate_total_portfolio_profit(settings, data):
    # TODO

    return data
