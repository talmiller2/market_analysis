import matplotlib
from data_functions import load_stock_data, define_stock_parameters
from aux_functions import get_year_labels
from settings_functions import define_default_settings

from cycler import cycler

import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})

# plt.close('all')

# date_start = '1929-01-01'
date_start = '1986-01-01'
# date_start = '1989-01-01'
# date_start = '2000-01-01'
# date_start = '2003-01-01'
date_end = '2020-09-30'

stock_name_list = []
# stock_name_list += ['SP500']
# stock_name_list += ['SP500TR']
# stock_name_list += ['SPY']
stock_name_list += ['NDX100']
stock_name_list += ['NDX100TR']
# stock_name_list += ['QQQ']
# stock_name_list += ['TLT']5
# stock_name_list += ['VFINX']

plot_close_adjusted = False
# plot_close_adjusted = True

settings = define_default_settings()
expense_ratios, leverage_factors, underlying_index, dividend_yield = define_stock_parameters()


for stock_name in stock_name_list:
    dates, index_values = load_stock_data(stock_name, date_start, date_end,
                                          dividend_yield=dividend_yield, settings=settings)
    if plot_close_adjusted:
        _, index_adjusted_values = load_stock_data(stock_name, date_start, date_end, close_type='Adj Close')
    inds_years, label_years = get_year_labels(dates)

    # plots
    plt.figure(1)
    plt.plot(index_values, label=stock_name, linewidth=2)
    if plot_close_adjusted and stock_name not in ['SP500', 'SP500TR', 'NDX100', 'NDX100TR']:
        plt.plot(index_adjusted_values, label=stock_name + ' (TR)', linewidth=2)
    # plt.yscale('log')
    plt.xticks(inds_years, label_years, rotation='vertical')
    plt.ylabel('yield')
    plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
