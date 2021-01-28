import matplotlib
from data_functions import load_stock_data, define_stock_parameters
from aux_functions import get_year_labels
from settings_functions import define_default_settings
from market_functions import simulate_portfolio_evolution
from cycler import cycler

import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})
# matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bcmygrk')})

# plt.close('all')

# date_start = '1929-01-01'
# date_start = '1986-01-01'
# date_start = '1987-01-01'
date_start = '1989-01-01'
# date_start = '1993-01-29'
# date_start = '1995-01-01'
# date_start = '1999-12-30'
# date_start = '2000-01-01'
# date_start = '2001-01-01'
# date_start = '2002-01-01'
# date_start = '2003-01-01'
# date_start = '2010-01-01'
# date_start = '2011-01-01'

# date_end = '1996-01-01'
# date_end = '1989-12-20'
# date_end = '1990-01-01'
# date_end = '1990-09-09'
# date_end = '1991-01-01'
# date_end = '1998-01-01'
# date_end = '2001-01-01'
# date_end = '2005-01-01'
date_end = '2020-09-30'
# date_end = '1996-09-30'

### plot data section

stock_name_list = []
# stock_name_list += ['SP500']
# stock_name_list += ['SP500TR']
# stock_name_list += ['SPY']
# stock_name_list += ['VOO']
# stock_name_list += ['IVV']
# stock_name_list += ['UPRO']

stock_name_list += ['NDX100']
stock_name_list += ['NDX100TR']
# stock_name_list += ['QQQ']
# stock_name_list += ['TQQQ']

# stock_name_list += ['TLT']
# stock_name_list += ['TLT-TR']
stock_name_list += ['VUSTX']
stock_name_list += ['VUSTX-TR']
# stock_name_list += ['VBTLX']
# stock_name_list += ['TMF']

plot_data = False
# plot_data = True

plot_close_adjusted = False
# plot_close_adjusted = True

settings = define_default_settings()
expense_ratios, leverage_factors, underlying_index, dividend_yield = define_stock_parameters()


if plot_data:
    for stock_name in stock_name_list:
        dates, index_values = load_stock_data(stock_name, date_start, date_end,
                                              dividend_yield=dividend_yield, settings=settings)
        if plot_close_adjusted:
            _, index_adjusted_values = load_stock_data(stock_name, date_start, date_end, close_type='Adj Close')
        inds_years, label_years = get_year_labels(dates)

        # plots
        plt.figure(1)
        plt.plot(index_values, label=stock_name, linewidth=1)
        if plot_close_adjusted and stock_name not in ['SP500', 'SP500TR', 'NDX100', 'NDX100TR']:
            plt.plot(index_adjusted_values, label=stock_name + ' (TR)', linewidth=1)
        # plt.yscale('log')
        # plt.xticks(inds_years, label_years, rotation='vertical')
        # plt.ylabel('yield')
        plt.title('Stock Data')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()


### simulation section

# plot_sim = False
plot_sim = True

if plot_sim:
    settings = define_default_settings()
    settings['date_start'] = date_start
    settings['date_end'] = date_end
    # settings['ideal_portfolio_fractions'] = {'SP500': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VOO': 1.0}
    # settings['ideal_portfolio_fractions'] = {'SSO': 1.0}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QLD': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 0.0, 'QLD': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TLT': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TMF': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VUSTX3': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VOO': 0.5, 'QQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VOO': 0.5, 'TLT': 0.5}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 0.5, 'TQQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 0.5, 'TMF': 0.5}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 0.5, 'TMF': 0.5}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 0.5, 'VUSTX3': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 0.5, 'VOO': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX2': 0.5, 'SSO': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX3': 0.5, 'UPRO': 0.5}
    settings['ideal_portfolio_fractions'] = {'VUSTX': 0.5, 'QQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX2': 0.5, 'QLD': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX3': 0.5, 'TQQQ': 0.5}
    # settings['periodic_investment_interval'] = 'yearly'
    # settings['periodic_investment_interval'] = 'quarterly'
    # settings['capital_gains_tax_percents'] = 0
    # settings['capital_gains_tax_percents'] = 5
    # settings['transaction_fee_percents'] = 0
    # settings['tax_scheme'] = 'FIFO'
    # settings['tax_scheme'] = 'LIFO'
    settings['tax_scheme'] = 'optimized'
    # settings['margin_leverage_target'] = 1.0
    # settings['margin_leverage_target'] = 1.5
    settings['margin_leverage_target'] = 2.0
    # settings['margin_leverage_target'] = 3.0
    # settings['margin_rate_percents'] = 5.0
    data = simulate_portfolio_evolution(settings)
    inds_years, label_years = get_year_labels(data['dates'])

    # plots
    plt.figure(1)
    # label = 'sim tax ' + settings['tax_scheme']
    # label = 'sim tax ' + settings['tax_scheme'] + ' (total sell tax loss ' + '{:0.2f}'.format(data['total_sell_tax_loss_percents']) + '%)'
    label = 'sim: ' + str(settings['ideal_portfolio_fractions'])
    if settings['margin_leverage_target'] > 0:
        label += ' margin leverage X' + str(settings['margin_leverage_target'])
    # color = 'k'
    color = 'b'
    plt.plot(data['total_portfolio_value'] - data['margin_debt'], color=color, label=label, linewidth=2)
    plt.plot(data['margin_debt'], linestyle='--', color=color, label='margin debt', linewidth=2)
    # plt.plot(data['total_portfolio_value'], label=label, linewidth=2, color='k', zorder=1)
    # plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=2, color='k', zorder=1)
    # plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=2, color=None)
    # plt.plot(data['total_portfolio_value'] - data['margin_debt'], label=label, linewidth=2, color=None)
    # plt.scatter(data['papers_buy_days'], data['portfolio_values_at_buy_days'], s=2, color=data['papers_status_colors'], zorder=2)
    # plt.plot(data['total_portfolio_value'] + data['cash_in_account'], label=label + ' + divs not reinvested', linewidth=2)
    # plt.plot(data['cash_in_account'], label='cash_in_account', linewidth=2)
    # plt.yscale('log')
    plt.xticks(inds_years, label_years, rotation='vertical')
    # plt.ylabel('yield')
    # plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(2)
    for stock_name in data['portfolio_fractions'].keys():
        plt.plot(data['portfolio_fractions'][stock_name], label=stock_name, linewidth=2)
    # plt.xticks(inds_years, label_years, rotation='vertical')
    plt.title('portfolio fractions')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(3)
    plt.plot(data['margin_leverage'], linewidth=2)
    # plt.xticks(inds_years, label_years, rotation='vertical')
    plt.title('margin leverage')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()