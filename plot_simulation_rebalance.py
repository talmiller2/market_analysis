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
# date_start = '1997-01-01'
# date_start = '1999-12-30'
# date_start = '2000-01-01'
# date_start = '2001-01-01'
# date_start = '2002-01-01'
# date_start = '2003-01-01'
# date_start = '2007-01-01'
# date_start = '2010-01-01'
# date_start = '2011-01-01'

# date_end = '1996-01-01'
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
# stock_name_list += ['SSO']
# stock_name_list += ['UPRO']

# stock_name_list += ['NDX100']
stock_name_list += ['NDX100TR']
# stock_name_list += ['QQQ']
# stock_name_list += ['QLD']
# stock_name_list += ['TQQQ']

# stock_name_list += ['TLT']
# stock_name_list += ['TLT-TR']
# stock_name_list += ['VUSTX']
stock_name_list += ['VUSTX-TR']
# stock_name_list += ['VBTLX']
# stock_name_list += ['UBT']
# stock_name_list += ['TMF']

# stock_name_list += ['TM']
# stock_name_list += ['BMW.DE']
# stock_name_list += ['F']
# stock_name_list += ['GM']

# plot_data = False
plot_data = True
#
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
        plt.plot(index_values, label=stock_name, linewidth=1, color=None)
        if plot_close_adjusted and stock_name not in ['SP500', 'SP500TR', 'NDX100', 'NDX100TR']:
            plt.plot(index_adjusted_values, label=stock_name + ' (TR)', linewidth=1, color=None)
        # plt.yscale('log')
        plt.xticks(inds_years, label_years, rotation='vertical')
        plt.ylabel('yield')
        # plt.title('Stock Data')
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
    # settings['ideal_portfolio_fractions'] = {'NDX100': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QLD': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 0.0, 'QLD': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TLT': 1.0}
    # settings['ideal_portfolio_fractions'] = {'UBT': 1.0}
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
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 0.5, 'QQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 0.65, 'QQQ': 0.35}
    # settings['ideal_portfolio_fractions'] = {'VUSTX2': 0.5, 'QLD': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX2': 0.65, 'QLD': 0.35}
    settings['ideal_portfolio_fractions'] = {'VUSTX3': 0.5, 'TQQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VUSTX3': 0.65, 'TQQQ': 0.35}
    settings['periodic_investment_interval'] = 'monthly'
    # settings['periodic_investment_interval'] = 'yearly'
    # settings['periodic_investment_interval'] = 'quarterly'
    # settings['initial_investment'] = 1
    # settings['periodic_investment'] = 1

    # settings['rebalance_percent_deviation'] = 20.0
    # settings['rebalance_percent_deviation'] = 20.1
    # settings['rebalance_percent_deviation'] = 19.9
    # settings['rebalance_percent_deviation'] = 19.5
    # settings['rebalance_percent_deviation'] = 20.5

    # settings['capital_gains_tax_percents'] = 0
    # settings['capital_gains_tax_percents'] = 5
    # settings['transaction_fee_percents'] = 0
    # settings['tax_scheme'] = 'FIFO'
    # settings['tax_scheme'] = 'LIFO'
    settings['tax_scheme'] = 'optimized'
    # settings['tax_scheme'] = 'none'
    data = simulate_portfolio_evolution(settings)

    # plots
    plt.figure(1)
    # label = 'sim tax ' + settings['tax_scheme']
    # label = 'sim tax ' + settings['tax_scheme'] + ' (total sell tax loss ' + '{:0.2f}'.format(data['total_sell_tax_loss_percents']) + '%)'
    # label = 'sim: ' + str(settings['ideal_portfolio_fractions'])
    label = 'sim tax: ' + settings['tax_scheme']
    # label += ' reb@' + str(settings['rebalance_percent_deviation']) + '%'
    # plt.plot(data['total_portfolio_value'], label=label, linewidth=2)
    # plt.plot(data['total_portfolio_value'], label=label, linewidth=2, color='k', zorder=1)
    # plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=2, color='k', zorder=1)
    color = 'k'
    # color = 'c'
    # color = 'b'
    # color = 'g'
    # color = 'r'
    plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=2, color=color)
    # plt.scatter(data['papers_buy_days'], data['portfolio_values_at_buy_days'], marker='o', s=5, color=data['papers_status_colors'], zorder=2)
    # plt.plot(data['total_portfolio_value'] + data['cash_in_account'], label=label + ' + divs not reinvested', linewidth=2)
    # plt.plot(data['cash_in_account'], label='cash_in_account', linewidth=2, color='')
    # plt.plot(data['taxes_paid'], label='total tax paid', linewidth=2, color=None)
    # plt.plot(data['gains'], label='gains', linewidth=2, color=None)
    plt.plot(data['gains'], label='gains', linewidth=2, color=color, linestyle='--')
    # plt.yscale('log')
    inds_years, label_years = get_year_labels(data['dates'])
    plt.xticks(inds_years, label_years, rotation='vertical')
    # plt.ylabel('yield')
    # plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(2)
    for stock_name in data['portfolio_fractions'].keys():
        plt.plot(data['portfolio_fractions'][stock_name], label=stock_name, linewidth=2)
    plt.xticks(inds_years, label_years, rotation='vertical')
    plt.title('portfolio fractions')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(4)
    plt.plot(data['drawdown'], label=label, linewidth=2)
    # plt.xticks(inds_years, label_years, rotation='vertical')
    plt.title('drawdown')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

