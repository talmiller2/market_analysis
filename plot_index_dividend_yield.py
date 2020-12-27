
import matplotlib
from aux_functions import get_dividend_yield, load_stock_data, get_year_labels
from cycler import cycler

import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})

plt.close('all')

date_start = '1986-01-01'
date_end = '2020-09-30'

index_name_list = []
index_name_list += ['SP500']
index_name_list += ['NDX100']

for index_name in index_name_list:
    dates, index_values = load_stock_data(index_name, date_start, date_end)
    # index_values /= index_values[0]
    inds_years, label_years = get_year_labels(dates)
    dividends = get_dividend_yield(dates, index_name=index_name)

    # plots
    plt.figure(1)
    plt.plot(dividends, label=index_name, linewidth=2)
    plt.xticks(inds_years, label_years, rotation='vertical')
    plt.ylabel('dividend yield %')
    plt.title('Dividends Data')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

