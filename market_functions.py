import pandas as pd
import numpy as np
import copy
from data_functions import load_stock_data, get_libor_rate, define_stock_parameters
from aux_functions import get_year_labels


def simulate_portfolio_evolution(settings):
    """
    Main function for the evolution of a portfolio
    """

    # load all necessary data for simulation
    data = load_data(settings)

    # monte-carlo realization of synthetic date with bootstrap
    data = bootstrap_data(settings, data)

    # initialize portfolio
    data = initialize_portfolio(settings, data)
    data = calculate_portfolio_fractions(settings, data, 0)

    # loop over days of simulation
    for ind_date, date in enumerate(data['dates']):
        if ind_date > 0:

            # calculate fractions of the total portfolio components
            data = calculate_portfolio_fractions(settings, data, ind_date)

            # evolve the portfolio elements with the passing day stock changes
            data = evolve_portfolio_single_day(settings, data, ind_date)

            # check if cash invest criterion reached, invest to try and balance
            # each buy is added to the portfolio for later
            if check_invest_criterion_reached(settings, data):
                data = add_cash_to_portfolio(settings, data, ind_date)

            # check if rebalancing criterion reached
            # buy/sell according to strategy and update the portfolio
            # save date of operation to calculate statistics of operations frequency
            if check_rebalancing_criterion_reached(settings, data, ind_date):
                data = rebalance_portfolio(settings, data, ind_date)

            # check if tax criterion reached (end of year), sell some to withdraw for tax
            # save cumulative amount of paid tax
            if check_tax_criterion_reached(settings, data):
                data = sell_papers_for_tax(settings, data)

    # track the open/closed papers for visualization
    data = track_paper_status(settings, data)

    # end of simulation period reached, calculate profit if entire portfolio sold now
    data = calculate_total_portfolio_yield(settings, data)

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
    dates, _ = load_stock_data('SP500', date_start, date_end)  # SP500 index has the "oldest" trading dates data
    inds_years, label_years = get_year_labels(dates)
    data['dates'] = dates
    data['inds_years'] = inds_years
    data['label_years'] = label_years

    # load libor_rate (relevant to leveraged etf sim)
    libor_rate = get_libor_rate(dates)
    data['libor_rate'] = libor_rate

    # stocks to be a part of the portfolio
    stock_names = settings['ideal_portfolio_fractions'].keys()
    for stock_name in stock_names:
        index_name = underlying_index[stock_name]
        _, stock_values = load_stock_data(index_name, date_start, date_end,
                                          dividend_yield=dividend_yield, settings=settings)
        data[stock_name] = stock_values

    return data


def bootstrap_data(settings, data):
    """
    Irrelevant for back-testing.
    Exploring possible future scenarios we can generate synthetic data by monte-carlo / bootstrap sampling the past data.
    Can also take into account correlation between days by picking several days in a row from the data.
    """
    if settings['perform_bootstrap']:
        # generate random indices
        num_days_synthetic = settings['synthetic_period_years'] * settings['num_trading_days_in_year']
        high = len(data['dates']) - settings['num_correlation_days']
        size = int(np.ceil(1.0 * num_days_synthetic / settings['num_correlation_days']))
        inds_bootstrap = np.random.randint(low=1, high=high, size=size)

        # change the dates list to be as long as needed (the values themselves become meaningless)
        data['dates'] = [data['dates'][0] for _ in range(num_days_synthetic)]
        data['inds_years'] = [i for i in range(num_days_synthetic)
                              if np.mod(i, settings['num_trading_days_in_year']) == 0]
        data['label_years'] = [str(int(i / 252)) for i in range(num_days_synthetic)
                               if np.mod(i, settings['num_trading_days_in_year']) == 0]

        # initialize synthetic data arrays
        stock_names = settings['ideal_portfolio_fractions'].keys()
        libor_rate_synth = np.zeros(len(data['dates']))
        data_synthetic = {}
        for stock_name in stock_names:
            data_synthetic[stock_name] = np.ones(len(data['dates']))

        for i, ind_bootstrap in enumerate(inds_bootstrap):
            for j in range(settings['num_correlation_days']):
                ind_synth = settings['num_correlation_days'] * i + j
                ind_data = ind_bootstrap + j
                if ind_synth < num_days_synthetic:
                    for stock_name in stock_names:
                        libor_rate_synth[ind_synth] = data['libor_rate'][ind_data]
                        data_synthetic[stock_name][ind_synth] = data_synthetic[stock_name][ind_synth - 1] \
                                                                * data[stock_name][ind_data] \
                                                                / data[stock_name][ind_data - 1]

        # overwrite the real data with the synthetic data
        data['libor_rate'] = libor_rate_synth
        for stock_name in stock_names:
            data[stock_name] = data_synthetic[stock_name]

    return data


def initialize_portfolio(settings, data):
    """
    first purchase of stocks according to the required fractions
    """
    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    stock_names = ideal_portfolio_fractions.keys()

    # check fraction add up to 100%
    if sum([ideal_portfolio_fractions[stock_name] for stock_name in stock_names]) != 1.0:
        raise ValueError('portfolio_fractions do not add up to 100%')

    # buy the initial papers for the portfolio
    papers_dict = {}  # will contain all the paper purchases, different list per stock name
    for stock_name in stock_names:
        papers = []
        paper = {}
        paper['id'] = len(papers)
        paper['value_at_buy'] = ideal_portfolio_fractions[stock_name] * settings['initial_investment'] \
                                * (1 - settings['transaction_fee_percents'] / 100.0)
        paper['value_current'] = paper['value_at_buy']
        paper['date'] = data['dates'][0]
        paper['ind_day_at_buy'] = 0
        paper['status'] = 'open'
        papers += [paper]
        papers_dict[stock_name] = papers
    data['papers_dict'] = papers_dict
    data['total_portfolio_value'] = np.nan * np.zeros(len(data['dates']))
    data['total_portfolio_value'][0] = settings['initial_investment']
    data['total_investment'] = np.nan * np.zeros(len(data['dates']))
    data['total_investment'][0] = settings['initial_investment']

    data['portfolio_fractions'] = {}
    for stock_name in stock_names:
        data['portfolio_fractions'][stock_name] = np.nan * np.zeros(len(data['dates']))

    # initialize the yearly gains that need to be tracked for taxes
    data['yearly_gains'] = 0

    # initialize the cash in account (will be accumulated due to dividends and then reinvested)
    data['cash_in_account'] = np.nan * np.zeros(len(data['dates']))
    data['cash_in_account'][0] = 0

    # initialize additional counters
    data['days_since_invest'] = 0
    data['days_since_rebalance'] = 0
    data['days_since_start_of_year'] = 0
    data['number_of_buy_days'] = 0
    data['number_of_sell_days'] = 0

    return data


def evolve_portfolio_single_day(settings, data, ind_date):
    """
    evolve each portfolio asset according to the stock it tracks
    evolve the leveraged assets, after taking the cut of expense-ratio and loan-rate (LIBOR).
    """

    papers_dict = data['papers_dict']
    expense_ratios = data['expense_ratios']
    leverage_factors = data['leverage_factors']
    dividend_yield = data['dividend_yield']
    data['cash_in_account'][ind_date] = data['cash_in_account'][ind_date - 1]
    data['total_investment'][ind_date] = data['total_investment'][ind_date - 1]

    for stock_name in papers_dict.keys():
        leverage_factor = leverage_factors[stock_name]
        stock_change_percents = 100 * (data[stock_name][ind_date] / data[stock_name][ind_date - 1] - 1)
        leverage_change_percents = leverage_factor * stock_change_percents
        expense_ratio_daily_percents = expense_ratios[stock_name] / settings['num_trading_days_in_year']
        libor_rate_daily_percents = (leverage_factor - 1) \
                                    * data['libor_rate'][ind_date] / settings['num_trading_days_in_year']
        paper_change_percents = leverage_change_percents - expense_ratio_daily_percents - libor_rate_daily_percents
        if paper_change_percents < -100:  # deal with case of total paper value loss
            paper_change_percents = -100
        paper_factor = 1 + paper_change_percents / 100.0

        papers = papers_dict[stock_name]
        for ind_paper, paper in enumerate(papers):
            papers[ind_paper]['value_current'] *= paper_factor

            # we assume the dividends are given on a daily basis for simplicity
            dividend_fraction = dividend_yield[stock_name] / 100.0 / settings['num_trading_days_in_year']
            total_dividend_received = papers[ind_paper]['value_current'] * dividend_fraction
            data['yearly_gains'] += total_dividend_received
            data['cash_in_account'][ind_date] += total_dividend_received
        papers_dict[stock_name] = papers
    data['papers_dict'] = papers_dict

    # evolove counters
    data['days_since_invest'] += 1
    data['days_since_rebalance'] += 1
    data['days_since_start_of_year'] += 1

    return data


def check_invest_criterion_reached(settings, data):
    """
    Count number of days until new cash or dividends are to be reinvested
    """
    if settings['periodic_investment_interval'] == 'monthly':
        days_between_invests = settings['num_trading_days_in_year'] / 12.0
    elif settings['periodic_investment_interval'] == 'quarterly':
        days_between_invests = settings['num_trading_days_in_year'] / 4.0
    elif settings['periodic_investment_interval'] == 'yearly':
        days_between_invests = settings['num_trading_days_in_year']
    else:
        raise ValueError('invalid periodic_investment_interval: ' + str(settings['periodic_investment_interval']))

    if data['days_since_invest'] >= days_between_invests:
        return True
    else:
        return False


def add_cash_to_portfolio(settings, data, ind_date):
    """
    add cash to account, on top of any dividends that were already given
    """
    data['days_since_invest'] = 0
    data['number_of_buy_days'] += 1
    data['cash_in_account'][ind_date] += settings['periodic_investment']
    data['total_investment'][ind_date] += settings['periodic_investment']

    # invest the cash to buy new papers, while trying to rebalance the portfolio as much as possible
    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    portfolio_fractions = data['portfolio_fractions']
    stock_names = ideal_portfolio_fractions.keys()
    cash_list = []
    for stock_name in stock_names:
        # using imperfect but simple heuristic that adds cash to all stocks,
        # but with greater weight to those that are under the wanted portfolio fraction.
        weight = ideal_portfolio_fractions[stock_name] / portfolio_fractions[stock_name][ind_date]
        cash_list += [weight]
    cash_list = np.array(cash_list)
    cash_list *= data['cash_in_account'][ind_date] / sum(cash_list)
    cash_list *= (1 - settings['transaction_fee_percents'] / 100.0)

    # buy new papers with the cash
    papers_dict = data['papers_dict']
    for stock_name, cash_portion in zip(stock_names, cash_list):
        if cash_portion > 0:
            paper = {}
            paper['id'] = len(papers_dict[stock_name]) + 1
            paper['value_at_buy'] = cash_portion
            paper['value_current'] = paper['value_at_buy']
            paper['date'] = data['dates'][ind_date]
            paper['ind_day_at_buy'] = ind_date
            paper['status'] = 'open'
            papers_dict[stock_name] += [paper]
    data['papers_dict'] = papers_dict

    # cash was used in total
    data['cash_in_account'][ind_date] = 0

    return data


def check_rebalancing_criterion_reached(settings, data, ind_date):
    """
    check if it is time to rebalance
    """

    if settings['rebalance_criterion'] == 'percent_deviation':
        deviation_frac = settings['rebalance_percent_deviation'] / 100.0
        ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
        portfolio_fractions = data['portfolio_fractions']
        stock_names = portfolio_fractions.keys()
        for stock_name in stock_names:
            frac = ideal_portfolio_fractions[stock_name]
            frac_curr = portfolio_fractions[stock_name][ind_date]
            if abs(frac_curr - frac) > deviation_frac:
                return True
        return False

    elif settings['rebalance_criterion'] == 'monthly':
        days_between_rebalances = settings['num_trading_days_in_year'] / 12.0
    elif settings['rebalance_criterion'] == 'quarterly':
        days_between_rebalances = settings['num_trading_days_in_year'] / 4.0
    elif settings['rebalance_criterion'] == 'yearly':
        days_between_rebalances = settings['num_trading_days_in_year']
    else:
        raise ValueError('invalid rebalance_criterion: ' + str(settings['rebalance_criterion']))

    if data['days_since_rebalance'] >= days_between_rebalances:
        return True
    else:
        return False


def rebalance_portfolio(settings, data, ind_date):
    """
    sell and buy stocks to rebalance the portfolio
    """
    data['number_of_buy_days'] += 1
    data['number_of_sell_days'] += 1
    data['days_since_rebalance'] = 0

    # calculate how much needs to be bought or sold from each stock type
    papers_dict = data['papers_dict']
    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    portfolio_fractions = data['portfolio_fractions']
    total_portfolio_value = data['total_portfolio_value'][ind_date]
    transfers = {}
    stock_names = portfolio_fractions.keys()
    for stock_name in stock_names:
        # the algebraic solution below assumes perfect sum-zero transfers between the stocks, neglecting transaction fee.
        transfers[stock_name] = total_portfolio_value \
                                * (ideal_portfolio_fractions[stock_name] - portfolio_fractions[stock_name][ind_date])

    # negative transfers are positions that need to be reduced in size, so sell papers
    for stock_name in stock_names:
        if transfers[stock_name] < 0:
            # amount that needs to be sold from this specific stock type
            amount_left_to_sell = abs(transfers[stock_name])
            # globally take the transaction fees into account by effectively increasing the amount that needs to be sold
            amount_left_to_sell /= (1 - settings['transaction_fee_percents'] / 100.0)

            # sort the papers in the order dictated by tax scheme
            indices_papers = sort_papers_by_tax_scheme(settings, data, stock_name)

            # sell papers in the order calculated above
            papers = papers_dict[stock_name]
            for ind_paper in indices_papers:
                paper = papers[ind_paper]
                if papers[ind_paper]['status'] == 'open':

                    # sell papers, but if the current paper is profitable, will be added to this year's gains
                    paper_profit = paper['value_current'] - paper['value_at_buy']
                    if paper_profit > 0:
                        data['yearly_gains'] += paper_profit

                    if paper['value_current'] >= amount_left_to_sell:
                        papers[ind_paper]['value_current'] -= amount_left_to_sell
                        amount_left_to_sell = 0  # finished selling this stock type for rebalancing
                        break
                    else:
                        amount_left_to_sell -= papers[ind_paper]['value_current']
                        papers[ind_paper]['value_current'] = 0
                        papers[ind_paper]['status'] = 'closed'
            papers_dict[stock_name] = papers

    # positive transfers are positions that need to be increased, so buy new papers accordingly
    for stock_name in stock_names:
        if transfers[stock_name] > 0:
            # amount that needs to be bought from this specific stock type
            amount_to_buy = abs(transfers[stock_name])
            # globally take the transaction fees into account by effectively reducing the amount that will be bought
            amount_to_buy *= (1 - settings['transaction_fee_percents'] / 100.0)

            # buy new paper
            paper = {}
            paper['id'] = len(papers_dict[stock_name]) + 1
            paper['value_at_buy'] = amount_to_buy
            paper['value_current'] = paper['value_at_buy']
            paper['date'] = data['dates'][ind_date]
            paper['ind_day_at_buy'] = ind_date
            paper['status'] = 'open'
            papers_dict[stock_name] += [paper]

    data['papers_dict'] = papers_dict

    return data


def check_tax_criterion_reached(settings, data):
    """
    check if time to pay tax arrived
    """
    if settings['capital_gains_tax_percents'] > 0:
        data['days_since_start_of_year'] += 1
        if data['days_since_start_of_year'] >= settings['num_trading_days_in_year']:
            data['days_since_start_of_year'] = 0
            return True
        else:
            return False
    else:
        return False


def sell_papers_for_tax(settings, data):
    """
    sell papers for tax at end of year.
    sell different stock types according to their fraction of the portfolio.
    different tax schemes are possible.
    """
    if data['yearly_gains'] > 0:
        data['number_of_sell_days'] += 1

        # total amount of tax to be paid for this year's gains
        tax_to_pay = data['yearly_gains'] * settings['capital_gains_tax_percents'] / 100.0
        # globally take the transaction fees into account by effectively increasing the amount of tax to be paid
        tax_to_pay /= (1 - settings['transaction_fee_percents'] / 100.0)

        # initialize the 'per stock' tax
        stock_tax_left_to_pay = 0

        papers_dict = data['papers_dict']
        ideal_portfolio_fractions = settings['ideal_portfolio_fractions']

        stock_names = ideal_portfolio_fractions.keys()
        for stock_name in stock_names:

            # amount of tax to be paid from a specific stock type
            stock_tax_left_to_pay += tax_to_pay * ideal_portfolio_fractions[stock_name]

            # sort the papers in the order dictated by tax scheme
            papers = papers_dict[stock_name]
            indices_papers = sort_papers_by_tax_scheme(settings, data, stock_name)

            # sell papers in the order calculated above
            for ind_paper in indices_papers:
                paper = papers[ind_paper]
                if papers[ind_paper]['status'] == 'open':

                    # sell papers for tax, but it the current paper is profitable, then tax must be paid for it as well.
                    paper_is_profitable = (paper['value_current'] > paper['value_at_buy'])
                    if paper_is_profitable:
                        amount_to_sell = stock_tax_left_to_pay / (1 - settings['capital_gains_tax_percents'] / 100.0)
                    else:
                        amount_to_sell = stock_tax_left_to_pay

                    if paper['value_current'] >= amount_to_sell:
                        papers[ind_paper]['value_current'] -= amount_to_sell
                        stock_tax_left_to_pay = 0
                        break
                    else:
                        stock_tax_left_to_pay -= papers[ind_paper]['value_current']
                        papers[ind_paper]['value_current'] = 0
                        papers[ind_paper]['status'] = 'closed'

            papers_dict[stock_name] = papers

        data['papers_dict'] = papers_dict

        # check tax was fully paid
        if stock_tax_left_to_pay != 0:
            raise ValueError('stock_tax_left_to_pay should be zero at this point. '
                             'stock_tax_left_to_pay = ' + str(stock_tax_left_to_pay))

    # tax year over, initialize for next year
    data['yearly_gains'] = 0

    return data


def sort_papers_by_tax_scheme(settings, data, stock_name):
    papers = data['papers_dict'][stock_name]
    if settings['tax_scheme'] == 'FIFO':
        # past to future
        indices_papers = [i for i in range(len(papers))]
    elif settings['tax_scheme'] == 'LIFO':
        # future to past
        indices_papers = [i for i in range(len(papers))][::-1]
    elif settings['tax_scheme'] == 'optimized':
        # order the papers from least to most profitable ar current date
        paper_profits = []
        for paper in papers:
            paper_profits += [paper['value_current'] - paper['value_at_buy']]
        paper_profits = np.array(paper_profits)
        indices_papers = np.argsort(paper_profits)
    else:
        raise ValueError('invalid tax_scheme: ' + str(settings['tax_scheme']))
    return indices_papers


def calculate_portfolio_fractions(settings, data, ind_date):
    """
    add end of trading day, sum up the current fractions and total value
    """
    papers_dict = data['papers_dict']
    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    stock_names = ideal_portfolio_fractions.keys()
    curr_total_portfolio_value = 0
    portfolio_fractions = {}
    for stock_name in stock_names:
        portfolio_fractions[stock_name] = 0
        papers = papers_dict[stock_name]
        for paper in papers:
            portfolio_fractions[stock_name] += paper['value_current']
        curr_total_portfolio_value += portfolio_fractions[stock_name]

    data['total_portfolio_value'][ind_date] = curr_total_portfolio_value
    # normalize portfolio_fractions_current to get fraction that sum up to one
    for stock_name in stock_names:
        portfolio_fractions[stock_name] /= curr_total_portfolio_value
        data['portfolio_fractions'][stock_name][ind_date] = portfolio_fractions[stock_name]

    return data


def track_paper_status(settings, data):
    """
    at end of simulation, track when papers were bought and their status
    """
    papers_buy_days = []
    papers_status_colors = []
    papers_dict = data['papers_dict']
    for stock_name in papers_dict.keys():
        papers = papers_dict[stock_name]
        for paper in papers:
            papers_buy_days += [paper['ind_day_at_buy']]
            if paper['status'] == 'open':
                papers_status_colors += ['g']
            else:
                papers_status_colors += ['r']
    portfolio_values_at_buy_days = data['total_portfolio_value'][papers_buy_days]

    data['papers_buy_days'] = papers_buy_days
    data['papers_status_colors'] = papers_status_colors
    data['portfolio_values_at_buy_days'] = portfolio_values_at_buy_days

    # collect some more transaction statistics
    data['average_monthly_buy_days'] = data['number_of_buy_days'] / len(data['dates']) \
                                       * (settings['num_trading_days_in_year'] / 12.0)
    data['average_monthly_sell_days'] = data['number_of_sell_days'] / len(data['dates']) \
                                        * (settings['num_trading_days_in_year'] / 12.0)
    return data


def calculate_total_portfolio_yield(settings, data):
    """
    at end of simulation, calculate profit if entire portfolio is sold (taking into account taxes and fees)
    """
    total_profit = 0

    papers_dict = data['papers_dict']
    for stock_name in papers_dict.keys():
        papers = papers_dict[stock_name]
        for paper in papers:
            if paper['status'] == 'open':
                paper_profit = paper['value_current'] - paper['value_at_buy']
                if paper_profit > 0:
                    total_profit += paper_profit

    total_portfolio_after_sell = data['total_portfolio_value'][-1] * (1 - settings['transaction_fee_percents'] / 100.0)
    capital_gains_tax_to_pay = total_profit * settings['capital_gains_tax_percents'] / 100.0

    data['total_yield'] = (total_portfolio_after_sell - capital_gains_tax_to_pay) / data['total_investment'][-1]
    data['total_yield_tax_free'] = total_portfolio_after_sell / data['total_investment'][-1]
    data['total_sell_tax_loss_percents'] = 100.0 * (1 - data['total_yield'] / data['total_yield_tax_free'])

    return data
