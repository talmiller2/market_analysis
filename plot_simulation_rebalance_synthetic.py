import matplotlib
from data_functions import load_stock_data, define_stock_parameters
from aux_functions import get_year_labels
from settings_functions import define_default_settings
from market_functions import simulate_portfolio_evolution
from cycler import cycler
import numpy as np

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
# date_start = '1999-12-30'
# date_start = '2000-01-01'
# date_start = '2001-01-01'
# date_start = '2002-01-01'
# date_start = '2003-01-01'
# date_start = '2010-01-01'
# date_start = '2011-01-01'

# date_end = '2001-01-01'
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

# stock_name_list += ['NDX100']
stock_name_list += ['NDX100TR']
# stock_name_list += ['QQQ']
# stock_name_list += ['TQQQ']

# stock_name_list += ['TLT']
stock_name_list += ['TLT-TR']
# stock_name_list += ['VUSTX']
# stock_name_list += ['VBTLX']
# stock_name_list += ['TMF']

### simulation section

# plot_sim = False
plot_sim = True

if plot_sim:
    settings = define_default_settings()
    settings['date_start'] = date_start
    settings['date_end'] = date_end
    # settings['ideal_portfolio_fractions'] = {'SP500': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VOO': 1.0}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 1.0}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TLT': 1.0}
    # settings['ideal_portfolio_fractions'] = {'TMF': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VUSTX': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VUSTX4': 1.0}
    # settings['ideal_portfolio_fractions'] = {'VOO': 0.5, 'QQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VOO': 0.5, 'TLT': 0.5}
    # settings['ideal_portfolio_fractions'] = {'VOO': 0.3, 'VUSTX': 0.7}
    settings['ideal_portfolio_fractions'] = {'SSO': 0.3, 'VUSTX2': 0.7}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 0.5, 'TQQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 0.5, 'TQQQ': 0.5}
    # settings['ideal_portfolio_fractions'] = {'UPRO': 0.5, 'TMF': 0.5}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 0.5, 'TMF': 0.5}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 0.5, 'VUSTX': 0.5}
    # settings['ideal_portfolio_fractions'] = {'QQQ': 0.85, 'VUSTX': 0.15}
    # settings['ideal_portfolio_fractions'] = {'QLD': 0.85, 'VUSTX2': 0.15}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 0.5, 'VUSTX3': 0.5}
    # settings['ideal_portfolio_fractions'] = {'TQQQ': 0.85, 'VUSTX3': 0.15}
    # settings['ideal_portfolio_fractions'] = {'QLD': 0.25, 'TQQQ': 0.25, 'VUSTX2': 0.25, 'VUSTX3': 0.25}
    # settings['margin_leverage_target'] = 1.1
    settings['margin_leverage_target'] = 2
    # settings['periodic_investment_interval'] = 'yearly'
    # settings['periodic_investment_interval'] = 'quarterly'
    # settings['initial_investment'] = 10
    # settings['periodic_investment'] = 1
    # settings['capital_gains_tax_percents'] = 0
    # settings['capital_gains_tax_percents'] = 5
    # settings['transaction_fee_percents'] = 0
    # settings['tax_scheme'] = 'FIFO'
    # settings['tax_scheme'] = 'LIFO'
    settings['tax_scheme'] = 'optimized'
    # settings['tax_scheme'] = 'none'
    # settings['rebalance_percent_deviation'] = 30
    # settings['rebalance_percent_deviation'] = 1
    settings['generate_synthetic_realization'] = True
    # settings['seed'] = np.random.randint(1e6)
    # settings['seed'] = 368397
    # settings['seed'] = 442194
    # settings['seed'] = 218161
    settings['seed'] = 808792
    data = simulate_portfolio_evolution(settings)

    # plots
    plt.figure(1)
    colors_components = ['b', 'g']
    for stock_name, color in zip(settings['ideal_portfolio_fractions'].keys(), colors_components):
        plt.plot(data[stock_name], label=data['underlying_index'][stock_name] + ' data', linewidth=1, color=color)
    label = 'sim'
    label += ' ' + str(settings['ideal_portfolio_fractions'])
    if settings['margin_leverage_target'] > 1:
        label += ' marginX' + str(settings['margin_leverage_target'])
    label += ' tax ' + settings['tax_scheme']
    # label += ', avg days buy ' + '{:.2f}'.format(data['average_monthly_buy_days']) + ' sell ' + '{:.2f}'.format(data['average_monthly_sell_days'])
    # label = 'sim tax ' + settings['tax_scheme'] + ' (total sell tax loss ' + '{:0.2f}'.format(data['total_sell_tax_loss_percents']) + '%)'
    # color = None
    color = 'k'
    # plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=2, color=color, zorder=1)
    plt.plot(data['total_portfolio_value'] - data['margin_debt'], label=label, linewidth=2, color=color, zorder=1)
    # plt.scatter(data['papers_buy_days'], data['portfolio_values_at_buy_days'], s=2, color=data['papers_status_colors'], zorder=2)
    # plt.plot(data['total_portfolio_value'] + data['cash_in_account'], label=label + ' + divs not reinvested', linewidth=2)
    # plt.plot(data['cash_in_account'], label='cash_in_account', linewidth=2)
    if settings['margin_leverage_target'] > 1:
        plt.plot(data['margin_debt'], label='margin debt', linewidth=2, color='c')
    plt.plot(data['gains'], label='gains', linewidth=2, color='m')
    plt.plot(data['taxes_paid'], label='tax', linewidth=2, color='r')
    # plt.yscale('log')
    plt.xticks(data['inds_years'], data['label_years'])
    plt.xlabel('years')
    # plt.ylabel('yield')
    # plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(2)
    for stock_name, color in zip(settings['ideal_portfolio_fractions'].keys(), colors_components):
        plt.plot(data['portfolio_fractions'][stock_name], label=stock_name, linewidth=2, color=color)
        plt.plot(settings['ideal_portfolio_fractions'][stock_name] + np.zeros(len(data['dates'])), '--',
                 linewidth=2, color=color)
    plt.xticks(data['inds_years'], data['label_years'])
    plt.title('portfolio fractions')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(3)
    plt.plot(data['margin_leverage'], linewidth=2)
    plt.title('margin leverage')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()