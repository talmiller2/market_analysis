import matplotlib
from data_functions import load_stock_data
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
# date_start = '1989-01-01'
# date_start = '1993-01-29'
date_start = '1999-12-30'
# date_start = '2000-01-01'
# date_start = '2001-01-01'
# date_start = '2002-01-01'
# date_start = '2003-01-01'
date_end = '2020-09-30'
# date_end = '1996-09-30'

### plot data section

stock_name_list = []
stock_name_list += ['SP500']
stock_name_list += ['SP500TR']
# stock_name_list += ['SPY']
# stock_name_list += ['VOO']
# stock_name_list += ['IVV']
stock_name_list += ['NDX100']
stock_name_list += ['NDX100TR']
# stock_name_list += ['QQQ']
# stock_name_list += ['TLT']
# stock_name_list += ['TLT-TR']
# stock_name_list += ['VUSTX']
# stock_name_list += ['VBTLX']

# plot_data = False
plot_data = True

# plot_close_adjusted = False
plot_close_adjusted = True

if plot_data:
    for stock_name in stock_name_list:
        dates, index_values = load_stock_data(stock_name, date_start, date_end)
        if plot_close_adjusted:
            _, index_adjusted_values = load_stock_data(stock_name, date_start, date_end, close_type='Adj Close')
        inds_years, label_years = get_year_labels(dates)

        # plots
        plt.figure(1)
        plt.plot(index_values, label=stock_name, linewidth=1)
        if plot_close_adjusted and stock_name not in ['SP500', 'SP500TR', 'NDX100', 'NDX100TR']:
            plt.plot(index_adjusted_values, label=stock_name + ' (TR)', linewidth=2)
        # plt.yscale('log')
        plt.xticks(inds_years, label_years, rotation='vertical')
        plt.ylabel('yield')
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
    stock_name = 'VOO'
    # settings['portfolio_fractions'] = {stock_name_list[0]: 1.0}
    # settings['portfolio_fractions'] = {'VOO': 1.0}
    # settings['portfolio_fractions'] = {'QQQ': 1.0}
    settings['portfolio_fractions'] = {'VOO': 0.5, 'QQQ': 0.5}
    # settings['periodic_investment_interval'] = 'yearly'
    # settings['periodic_investment_interval'] = 'quarterly'
    # settings['capital_gains_tax_percents'] = 0
    # settings['capital_gains_tax_percents'] = 50
    # settings['transaction_fee_percents'] = 0
    # settings['tax_scheme'] = 'FIFO'
    # settings['tax_scheme'] = 'LIFO'
    settings['tax_scheme'] = 'optimized'
    data = simulate_portfolio_evolution(settings)

    # plots
    plt.figure(1)
    # label = stock_name + ' sim'
    label = stock_name + ' sim tax ' + settings['tax_scheme']
    # plt.plot(data['total_portfolio_value'], label=label, linewidth=2)
    plt.plot(data['total_portfolio_value'], label=label, linewidth=2, color='k', zorder=1)
    plt.scatter(data['papers_buy_days'], data['portfolio_values_at_buy_days'], s=2, color=data['papers_status_colors'], zorder=2)

    # plt.plot(data['total_portfolio_value'] + data['cash_in_account'], label=label + ' + divs not reinvested', linewidth=2)
    # plt.plot(data['cash_in_account'], label='cash_in_account', linewidth=2)
    # plt.yscale('log')
    # plt.xticks(inds_years, label_years, rotation='vertical')
    # plt.ylabel('yield')
    # plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
