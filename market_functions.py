import numpy as np
from data_functions import load_stock_data, get_libor_rate, define_stock_parameters
from aux_functions import get_year_labels


def simulate_portfolio_evolution(settings):
    """
    Main function for the evolution of a portfolio
    """

    # load all necessary data for simulation
    settings, data = load_data(settings)

    # monte-carlo realization of synthetic date with bootstrap
    data = generate_synthetic_realization(settings, data)

    # initialize portfolio
    data = initialize_portfolio(settings, data)
    data = calculate_portfolio_fractions(settings, data, 0)

    # loop over days of simulation
    for ind_date, date in enumerate(data['dates']):
        if ind_date > 0 and data['simulation_status'] == 'nominal':

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
                data = sell_papers_for_tax(settings, data, ind_date)

    # track the open/closed papers for visualization
    data = track_paper_status(settings, data)

    # end of simulation period reached, calculate profit if entire portfolio sold now
    data = calculate_total_portfolio_yield(settings, data)

    # calculate additinal risk metrics during the simulation
    data = calculate_risk_metrics(settings, data)

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

    # check that portfolio fractions are all positive (and remove zeros if exist)
    stock_names = settings['ideal_portfolio_fractions'].keys()
    zero_stocks = []
    for stock_name in stock_names:
        if settings['ideal_portfolio_fractions'][stock_name] < 0:
            raise ValueError('negative portfolio fraction for ' + str(stock_name))
        elif settings['ideal_portfolio_fractions'][stock_name] == 0:
            zero_stocks += [stock_name]
    for stock_name in zero_stocks:
        settings['ideal_portfolio_fractions'].pop(stock_name)

    # stocks to be a part of the portfolio
    for stock_name in stock_names:
        index_name = underlying_index[stock_name]
        _, stock_values = load_stock_data(index_name, date_start, date_end,
                                          dividend_yield=dividend_yield, settings=settings)
        data[stock_name] = stock_values

    return settings, data


def generate_synthetic_realization(settings, data):
    """
    Exploring possible future scenarios we can generate synthetic data by monte-carlo / bootstrap sampling the past data.
    Can also take into account correlation between days by picking several days in a row from the data.
    Irrelevant for back-testing.
    """
    if settings['generate_synthetic_realization']:
        # generate random indices
        np.random.seed(settings['seed'])
        num_days_synthetic = settings['synthetic_period_years'] * settings['num_trading_days_in_year']
        high = len(data['dates']) - settings['num_correlation_days']
        size = int(np.ceil(1.0 * num_days_synthetic / settings['num_correlation_days']))
        inds_bootstrap = np.random.randint(low=1, high=high, size=size)

        # change the dates list to be as long as needed (the values themselves become meaningless)
        data['dates'] = [data['dates'][0] for _ in range(num_days_synthetic)]
        data['inds_years'] = [i for i in range(num_days_synthetic)
                              if np.mod(i, settings['num_trading_days_in_year']) == 0]
        data['label_years'] = [str(int(i / settings['num_trading_days_in_year'])) for i in range(num_days_synthetic)
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
    data['simulation_status'] = 'nominal'

    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    stock_names = ideal_portfolio_fractions.keys()

    # check fraction add up to 100%
    if sum([ideal_portfolio_fractions[stock_name] for stock_name in stock_names]) != 1.0:
        raise ValueError('portfolio_fractions do not add up to 100%')

    # check margin leverage is positive
    if settings['margin_leverage_target'] < 1.0:
        raise ValueError('margin_leverage_target must be greater than 1.')

    # buy the initial papers for the portfolio
    papers_dict = {}  # will contain all the paper purchases, different list per stock name
    for stock_name in stock_names:
        papers = []
        paper = {}
        paper['id'] = 0
        paper['stock_name'] = stock_name
        paper['value_at_buy'] = ideal_portfolio_fractions[stock_name] * settings['initial_investment'] \
                                * (1 - settings['transaction_fee_percents'] / 100.0) \
                                * settings['margin_leverage_target']
        paper['value_current'] = paper['value_at_buy']
        paper['date'] = data['dates'][0]
        paper['ind_day_at_buy'] = 0
        paper['status'] = 'open'
        papers += [paper]
        papers_dict[stock_name] = papers
    data['papers_dict'] = papers_dict
    data['total_portfolio_value'] = np.nan * np.zeros(len(data['dates']))
    data['total_portfolio_value'][0] = settings['initial_investment'] * settings['margin_leverage_target']
    data['total_investment'] = np.nan * np.zeros(len(data['dates']))
    data['total_investment'][0] = settings['initial_investment']

    data['portfolio_fractions'] = {}
    for stock_name in stock_names:
        data['portfolio_fractions'][stock_name] = np.nan * np.zeros(len(data['dates']))

    # initialize the gains that need to be tracked for taxes
    data['gains'] = np.nan * np.zeros(len(data['dates']))
    data['gains'][0] = 0

    # initialize the total taxes paid
    data['taxes_paid'] = np.nan * np.zeros(len(data['dates']))
    data['taxes_paid'][0] = 0

    # initialize the cash in account (will be accumulated due to dividends and then reinvested)
    data['cash_in_account'] = np.nan * np.zeros(len(data['dates']))
    data['cash_in_account'][0] = - settings['initial_investment'] * (settings['margin_leverage_target'] - 1.0)

    # initialize margin debt and leverage
    data['margin_debt'] = np.nan * np.zeros(len(data['dates']))
    data['margin_leverage'] = np.nan * np.zeros(len(data['dates']))
    data = calculate_margin_state(settings, data, 0)

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

    data['total_investment'][ind_date] = data['total_investment'][ind_date - 1]
    data['cash_in_account'][ind_date] = data['cash_in_account'][ind_date - 1]
    data['gains'][ind_date] = data['gains'][ind_date - 1]
    data['taxes_paid'][ind_date] = data['taxes_paid'][ind_date - 1]

    # add margin loan rate that decreases the cash further every day
    if data['cash_in_account'][ind_date] < 0:
        data['cash_in_account'][ind_date] *= 1 + settings['margin_rate_percents'] \
                                             / 100.0 / settings['num_trading_days_in_year']

    data = calculate_margin_state(settings, data, ind_date)

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
            if stock_name in ['VUSTX', 'TLT']:
                # phenomenological model to treat the time varying dividend of bonds
                curr_div_yield = dividend_yield[stock_name] + 0.5 * data['libor_rate'][ind_date]
            else:
                curr_div_yield = dividend_yield[stock_name]
            dividend_fraction = curr_div_yield / 100.0 / settings['num_trading_days_in_year']
            total_dividend_received = papers[ind_paper]['value_current'] * dividend_fraction
            data['gains'][ind_date] += total_dividend_received
            data['cash_in_account'][ind_date] += total_dividend_received

        papers_dict[stock_name] = papers
    data['papers_dict'] = papers_dict

    # evolve counters
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
    data['total_investment'][ind_date] += settings['periodic_investment']
    data['cash_in_account'][ind_date] += settings['periodic_investment']
    data = calculate_margin_state(settings, data, ind_date)

    # invest the cash to buy new papers
    if data['cash_in_account'][ind_date] > 0:
        ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
        stock_names = ideal_portfolio_fractions.keys()
        # split the cash between the stocks according to the ideal fractions
        cash_list = [ideal_portfolio_fractions[stock_name] for stock_name in stock_names]
        cash_list = data['cash_in_account'][ind_date] * np.array(cash_list)
        cash_list *= (1 - settings['transaction_fee_percents'] / 100.0)

        # buy new papers with the cash
        papers_dict = data['papers_dict']
        for stock_name, cash_portion in zip(stock_names, cash_list):
            if cash_portion > 0:
                paper = {}
                paper['id'] = len(papers_dict[stock_name]) + 1
                paper['stock_name'] = stock_name
                paper['value_at_buy'] = cash_portion
                paper['value_current'] = paper['value_at_buy']
                paper['date'] = data['dates'][ind_date]
                paper['ind_day_at_buy'] = ind_date
                paper['status'] = 'open'
                papers_dict[stock_name] += [paper]
        data['papers_dict'] = papers_dict

        # cash was used in total
        data['number_of_buy_days'] += 1
        data['cash_in_account'][ind_date] = 0

    return data


def check_rebalancing_criterion_reached(settings, data, ind_date):
    """
    check if it is time to rebalance based on different criteria
    """
    if settings['rebalance_criterion'] not in ['percent_deviation', 'monthly', 'quarterly', 'yearly']:
        raise ValueError('invalid rebalance_criterion: ' + str(settings['rebalance_criterion']))

    if settings['rebalance_criterion'] == 'percent_deviation':
        ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
        portfolio_fractions = data['portfolio_fractions']
        stock_names = portfolio_fractions.keys()
        for stock_name in stock_names:
            stock_percent_ideal = ideal_portfolio_fractions[stock_name] * 100.0
            stock_percent_curr = portfolio_fractions[stock_name][ind_date] * 100.0
            if abs(stock_percent_ideal - stock_percent_curr) > settings['rebalance_percent_deviation']:
                return True

    if settings['margin_leverage_target'] > 1:
        margin_deviation_percents = abs(data['margin_leverage'][ind_date] - settings['margin_leverage_target']) \
                                    / settings['margin_leverage_target'] * 100.0
        if margin_deviation_percents > settings['margin_leverage_percent_deviation']:
            return True

    days_between_rebalances = np.inf
    if settings['rebalance_criterion'] == 'monthly':
        days_between_rebalances = settings['num_trading_days_in_year'] / 12.0
    elif settings['rebalance_criterion'] == 'quarterly':
        days_between_rebalances = settings['num_trading_days_in_year'] / 4.0
    elif settings['rebalance_criterion'] == 'yearly':
        days_between_rebalances = settings['num_trading_days_in_year']
    if data['days_since_rebalance'] >= days_between_rebalances:
        return True

    return False


def rebalance_portfolio(settings, data, ind_date):
    """
    sell and buy stocks to rebalance the portfolio
    """
    data['number_of_buy_days'] += 1
    data['number_of_sell_days'] += 1
    data['days_since_rebalance'] = 0

    # when using margin leverage, calculate how much needs to be increased or reduced
    total_portfolio_value = data['total_portfolio_value'][ind_date]
    margin_debt = data['margin_debt'][ind_date]
    leverage_target = settings['margin_leverage_target']
    delta_loan = leverage_target * (total_portfolio_value - margin_debt) - total_portfolio_value

    # calculate how much needs to be bought or sold from each stock type
    papers_dict = data['papers_dict']
    ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
    portfolio_fractions = data['portfolio_fractions']
    transfers = {}
    stock_names = portfolio_fractions.keys()
    for stock_name in stock_names:
        # the algebraic solution below assumes transfers between the stocks + total value shift if margin debt is
        # changed, but neglecting transaction fee.
        transfers[stock_name] = total_portfolio_value \
                                * (ideal_portfolio_fractions[stock_name] - portfolio_fractions[stock_name][ind_date]) \
                                + ideal_portfolio_fractions[stock_name] * delta_loan

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

                    if paper['value_current'] >= amount_left_to_sell:
                        data['gains'][ind_date] += np.sign(paper_profit) * min(paper_profit, amount_left_to_sell)
                        papers[ind_paper]['value_current'] -= amount_left_to_sell
                        amount_left_to_sell = 0  # finished selling this stock type for rebalancing
                        break
                    else:
                        data['gains'][ind_date] += paper_profit
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
            paper['stock_name'] = stock_name
            paper['value_at_buy'] = amount_to_buy
            paper['value_current'] = paper['value_at_buy']
            paper['date'] = data['dates'][ind_date]
            paper['ind_day_at_buy'] = ind_date
            paper['status'] = 'open'
            papers_dict[stock_name] += [paper]

    data['papers_dict'] = papers_dict

    # update total portfolio value, cash and margin
    data['total_portfolio_value'][ind_date] += delta_loan
    data['cash_in_account'][ind_date] -= delta_loan
    data = calculate_margin_state(settings, data, ind_date)

    return data


def check_tax_criterion_reached(settings, data):
    """
    check if time to pay tax arrived
    """
    if settings['tax_scheme'] != 'none' and settings['capital_gains_tax_percents'] > 0:
        if data['days_since_start_of_year'] >= settings['num_trading_days_in_year']:
            data['days_since_start_of_year'] = 0
            return True
        else:
            return False
    else:
        return False


def sell_papers_for_tax(settings, data, ind_date):
    """
    sell papers for tax at end of year.
    sell different stock types according to their fraction of the portfolio.
    different tax schemes are possible.
    """
    if data['gains'][ind_date] > 0:
        data['number_of_sell_days'] += 1

        # globally take the transaction fees into account by effectively increasing the amount that needs to be sold
        gains = data['gains'][ind_date] / (1 - settings['transaction_fee_percents'] / 100.0)
        cgt = settings['capital_gains_tax_percents'] / 100.0

        # check if we even have enough money in the portfolio to pay the tax, otherwise it is game over since we can't
        # even pay the tax we are required. treat this edge case as total portfolio zero yield.
        if gains * cgt > data['total_portfolio_value'][ind_date]:
            print('gains = ' + str(gains))
            print('total_portfolio_value = ' + str(data['total_portfolio_value'][ind_date]))
            print('Taxes are greater than the entire portfolio, GAME OVER.')
            data['simulation_status'] = 'failed'
            return data

        papers_dict = data['papers_dict']
        ideal_portfolio_fractions = settings['ideal_portfolio_fractions']
        stock_names = ideal_portfolio_fractions.keys()
        for stock_name in stock_names:

            # splitting the tax to pay between the different stock types, for simplicity
            G = gains * data['portfolio_fractions'][stock_name][ind_date]

            # sort the papers in the order dictated by tax scheme
            papers = papers_dict[stock_name]
            indices_papers = sort_papers_by_tax_scheme(settings, data, stock_name)

            # sell papers in the order calculated above
            for ind_paper in indices_papers:

                paper = papers[ind_paper]
                if papers[ind_paper]['status'] == 'open':

                    V = paper['value_current']
                    P = paper['value_current'] - paper['value_at_buy']

                    G_transition = abs(P) * (1 - np.sign(P) * cgt) / cgt
                    if G <= G_transition:
                        delta_T = G * cgt / (1 - np.sign(P) * cgt)
                    else:
                        delta_T = (G + P) * cgt

                    if V > delta_T:
                        # the paper has enough value to cover the yearly gains
                        data['taxes_paid'][ind_date] += delta_T
                        G = 0
                        papers[ind_paper]['value_current'] -= delta_T
                        break
                    else:
                        # this paper does not have enough, so we fully sell it and continue to the next one
                        data['taxes_paid'][ind_date] += V
                        G = (delta_T - V) / cgt
                        papers[ind_paper]['value_current'] = 0
                        papers[ind_paper]['status'] = 'closed'

            papers_dict[stock_name] = papers

            # check tax was fully paid for this stock type
            if G != 0:
                print('Not enough value to pay off taxes for ' + stock_name + '. GAME OVER.')
                data['simulation_status'] = 'failed'
                return data

        data['papers_dict'] = papers_dict

        # recalculate the portfolio value and fractions
        data = calculate_portfolio_fractions(settings, data, ind_date)

        # reset margin debt and cash for next year
        data = calculate_margin_state(settings, data, ind_date)

        # tax year over, reset for next year (only for positive gains, losses carries over)
        data['gains'][ind_date] = 0

    return data


def sort_papers_by_tax_scheme(settings, data, stock_name=None):
    """
    Sort the papers in different orders according to the tax scheme
    """

    # pick a list of papers to sort
    if stock_name is not None:
        papers = data['papers_dict'][stock_name]
    else:
        papers = []
        for stock_name in data['papers_dict'].keys():
            papers += data['papers_dict'][stock_name]

    # sort by the requested method
    if settings['tax_scheme'] == 'FIFO':
        # past to future
        paper_date_indices = [paper['ind_day_at_buy'] for paper in papers]
        indices_papers = np.argsort(paper_date_indices)
    elif settings['tax_scheme'] == 'LIFO':
        # future to past
        paper_date_indices = [paper['ind_day_at_buy'] for paper in papers]
        indices_papers = np.argsort(paper_date_indices)[::-1]
    elif settings['tax_scheme'] in ['optimized', 'none']:
        # order the papers from least to most profitable at current date
        paper_profits = [paper['value_current'] - paper['value_at_buy'] for paper in papers]
        indices_papers = np.argsort(paper_profits)
    else:
        raise ValueError('invalid tax_scheme: ' + str(settings['tax_scheme']))

    return indices_papers


def calculate_portfolio_fractions(settings, data, ind_date):
    """
    add end of trading day, sum up the current fractions and total value
    """
    # print(ind_date)

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

    if curr_total_portfolio_value <= 0:
        print('portfolio is nulled. GAME OVER')
        data['simulation_status'] = 'failed'
        return data

    data['total_portfolio_value'][ind_date] = curr_total_portfolio_value
    # normalize portfolio_fractions_current to get fraction that sum up to one
    for stock_name in stock_names:
        portfolio_fractions[stock_name] /= curr_total_portfolio_value
        data['portfolio_fractions'][stock_name][ind_date] = portfolio_fractions[stock_name]

    return data


def calculate_margin_state(settings, data, ind_date):
    """
    update current margin debt and margin leverage
    """
    if data['cash_in_account'][ind_date] < 0:
        data['margin_debt'][ind_date] = - data['cash_in_account'][ind_date]
    else:
        data['margin_debt'][ind_date] = 0

    data['margin_leverage'][ind_date] = data['total_portfolio_value'][ind_date] \
                                        / (data['total_portfolio_value'][ind_date] - data['margin_debt'][ind_date])
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

    if data['simulation_status'] == 'nominal':
        total_profit = 0

        papers_dict = data['papers_dict']
        for stock_name in papers_dict.keys():
            papers = papers_dict[stock_name]
            for paper in papers:
                if paper['status'] == 'open':
                    total_profit += paper['value_current'] - paper['value_at_buy']

        # use carried over losses from previous years, if they exist
        if data['gains'][-1] < 0:
            total_profit += data['gains'][-1]

        # in the final sell, an overall loss will not earn a gain
        if total_profit < 0: total_profit = 0

        total_portfolio_after_sell = data['total_portfolio_value'][-1] * (
                    1 - settings['transaction_fee_percents'] / 100.0)
        total_portfolio_after_sell -= data['margin_debt'][-1]  # cover margin after total sell
        capital_gains_tax_to_pay = total_profit * settings['total_sell_capital_gains_tax_percents'] / 100.0

        data['total_yield'] = (total_portfolio_after_sell - capital_gains_tax_to_pay) / data['total_investment'][-1]
        data['total_yield_tax_free'] = total_portfolio_after_sell / data['total_investment'][-1]
        data['total_sell_tax_loss_percents'] = 100.0 * (1 - data['total_yield'] / data['total_yield_tax_free'])

    else:
        data['total_yield'] = -1.0
        data['total_yield_tax_free'] = -1.0
        data['total_sell_tax_loss_percents'] = 0

    return data


def calculate_risk_metrics(settings, data):
    """
    calculate risk metrics that characterize the volatility of the portfolio which is not important
    in the long run, but can be hard psychologically.
    """
    if data['simulation_status'] == 'nominal':

        yield_history = (data['total_portfolio_value'] - data['margin_debt']) / data['total_investment']
        data['yield_min'] = np.nanmin(yield_history)
        data['yield_max'] = np.nanmax(yield_history)

        yield_relative_to_cum_max = 0 * yield_history
        curr_max = 0
        for i, curr_yield in enumerate(yield_history):
            curr_max = np.nanmax([curr_max, curr_yield])
            yield_relative_to_cum_max[i] = curr_yield / curr_max
        data['drawdown'] = 1 - yield_relative_to_cum_max
        data['max_drawdown'] = np.max(data['drawdown'])

    else:
        data['yield_min'] = -1.0
        data['yield_max'] = 1.0
        data['max_drawdown'] = 2.0

    return data
