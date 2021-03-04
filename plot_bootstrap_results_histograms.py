import matplotlib
from data_functions import load_stock_data
from aux_functions import get_year_labels
import numpy as np
from cycler import cycler
import scipy.stats
import matplotlib.pyplot as plt
from settings_functions import define_default_settings
from market_functions import simulate_portfolio_evolution
import os
import matplotlib.cm as cm

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
# matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})

# plt.close('all')

# define the sets of runs to be plotted

color_list = []
year_start_list = []
investing_strategy_list = []
correlation_days_list = []
synthetic_period_years_list = []
tax_scheme_list = []
stock1_list = []
stock2_list = []
margin_lev_list = []
label_list = []
fracs_list = []

invest_strategy = 'single'
# invest_strategy = 'monthly'

synthetic_period_years = 10
# synthetic_period_years = 20

num_correlation_days = 5
# num_correlation_days = 1
# num_correlation_days = 10

# rebalance_percent = 10
rebalance_percent = 20
# rebalance_percent = 30
# rebalance_percent = 40
# rebalance_percent = 50ß

year1 = 1989
year2 = 2003

# tax_scheme = 'optimized'
# tax_scheme = 'LIFO'
# tax_scheme = 'FIFO'
tax_scheme = 'none'

# index_base = 'NDX100'
index_base = 'SP500'

if index_base == 'NDX100':
    index_stock = 'QQQ'
    index_X2_stock = 'QLD'
    index_X25_stock = 'QQQ2.5'
    index_X3_stock = 'TQQQ'
    index_X4_stock = 'QQQ4'
else:
    index_stock = 'VOO'
    index_X2_stock = 'SSO'
    index_X25_stock = 'VOO2.5'
    index_X3_stock = 'UPRO'
    index_X4_stock = 'VOO4'

bond_stock = 'VUSTX'
bond_X2_stock = 'VUSTX2'
bond_X25_stock = 'VUSTX2.5'
bond_X3_stock = 'VUSTX3'
bond_X4_stock = 'VUSTX4'

####  plot dependence on leveraged bond / index portfolios

year = year1
# year = year2

# color_list += ['b']
color_list += ['g']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_stock]
stock2_list += [index_stock]
margin_lev_list += [1]
label_list += ['100% VOO']
fracs_list += [1.0]
# label_list += ['50%/50% VUSTX/VOO']
# fracs_list += [0.5]


color_list += ['b']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_X2_stock]
stock2_list += [index_X2_stock]
margin_lev_list += [1]
label_list += ['100% SSO']
fracs_list += [1.0]
# label_list += ['50%/50% VUSTX2/SSO']
# fracs_list += [0.5]

color_list += ['r']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_X3_stock]
stock2_list += [index_X3_stock]
margin_lev_list += [1]
label_list += ['100% UPRO']
fracs_list += [1.0]
# label_list += ['50%/50% VUSTX3/UPRO']
# fracs_list += [0.5]


###########################

for ind_set, color in enumerate(color_list):
    print('set ' + str(ind_set))

    year_start = year_start_list[ind_set]
    investing_strategy = investing_strategy_list[ind_set]
    correlation_days = correlation_days_list[ind_set]
    synthetic_period_years = synthetic_period_years_list[ind_set]
    tax_scheme = tax_scheme_list[ind_set]
    stock1 = stock1_list[ind_set]
    stock2 = stock2_list[ind_set]
    margin_lev = margin_lev_list[ind_set]

    use_single_color = True
    # use_single_color = False

    # define the period from which the synthetic realization will be drawn
    if year_start == 1989:
        date_start = '1989-01-01'
    else:
        date_start = '2003-01-01'

    # date_end = '2010-01-01'
    # date_end = '2019-01-01'
    date_end = '2020-09-30'

    settings = define_default_settings()

    # save the result to plot later
    save_dir = ''
    # save_dir += 'simulations/'
    save_dir = '/Users/talmiller/Downloads/'
    # save_dir += 'simulations_slurm_2/'
    save_dir += 'simulations_slurm_3/'

    if investing_strategy == 'single':
        label_investment = 'investment_initial_1_periodic_0'
    else:
        label_investment = 'investment_initial_10_periodic_1'
    save_dir += label_investment
    save_dir += '_total_time_' + str(synthetic_period_years)
    save_dir += '_cd_' + str(correlation_days)
    save_dir += '_date_start_' + date_start
    save_dir += '_end_' + date_end
    save_dir += '_tax_' + tax_scheme
    if rebalance_percent != 20:
        save_dir += '_rebalance_percent_' + str(rebalance_percent)
    save_dir += '/'

    # frac_list = np.linspace(0, 1, 21)
    # frac_list = [1.0]
    # frac_list = [0.5]
    frac_list = [fracs_list[ind_set]]

    if margin_lev == 1:
        files_filtered = [
            stock1 + '_' + '{:0.2f}'.format(1 - frac) + '_' + stock2 + '_' + '{:0.2f}'.format(frac) + '.txt'
            for frac in frac_list]
    else:
        files_filtered = [
            stock1 + '_' + '{:0.2f}'.format(1 - frac) + '_' + stock2 + '_' + '{:0.2f}'.format(frac) + '_mX' + str(
                margin_lev) + '.txt'
            for frac in frac_list]

    label = ''
    # label += 'y' + date_start[0:4] + ': '
    # label += 'y' + date_start[0:4] + ', cd' + str(correlation_days) + ': '
    # label += 'y' + date_start[0:4] + ' ' + tax_scheme + ': '
    # label += 'y' + date_start[0:4] + ', rebalance@' + str(rebalance_percent) + '%: '
    # label += 'y' + date_start[0:4] + ', rebalance@' + str(rebalance_percent) + '%, ' + tax_scheme + ': '
    label += stock1 + '/' + stock2
    if margin_lev > 1:
        label += ' mX' + str(margin_lev)

    colors = cm.rainbow(np.linspace(0, 1, len(files_filtered)))

    for ind_file, file_name in enumerate(files_filtered):

        try:

            results_mat = np.loadtxt(save_dir + file_name)
            # yield_list = results_mat[:, 0]
            yield_list = results_mat[:, 1]
            yield_tax_free_list = results_mat[:, 1]
            if tax_scheme == 'none':
                yield_list = yield_tax_free_list
            min_yield_list = results_mat[:, 2]
            max_drawdown_list = results_mat[:, 3]

            # plot
            # label = None
            # label = file_name.split('.txt')[0]
            label = label_list[ind_set]
            # color = None

            plt.figure(1)
            plt.subplot(1,3,1)
            # percentile_max_hist = 99
            # bins = np.linspace(0, np.percentile(yield_list, percentile_max_hist), 50)
            bins = np.linspace(0, 20, 50)
            yield_risk = np.percentile(yield_list, 5)
            yield_median = np.percentile(yield_list, 50)
            # label_curr = '5%=' + '{:.2f}'.format(yield_risk) + ', 50%=' + '{:.2f}'.format(yield_median)
            label_curr = '{:.2f}'.format(yield_risk) + ' (5%), ' + '{:.2f}'.format(yield_median) + ' (50%)'
            plt.hist(yield_list, bins=bins, density=True, alpha=0.5, label=label_curr, color=color)
            plt.xlabel('yield')
            # plt.title('yield probability distribution')
            plt.legend()

            plt.subplot(1,3,2)
            percentile_max_hist = 100
            bins = np.linspace(0, np.percentile(min_yield_list, percentile_max_hist), 50)
            plt.hist(min_yield_list, bins=bins, density=True, alpha=0.5, label=label, color=color)
            plt.xlabel('minimal yield')
            plt.legend()

            plt.subplot(1,3,3)
            percentile_max_hist = 100
            bins = np.linspace(0, np.percentile(max_drawdown_list, percentile_max_hist), 50)
            plt.hist(max_drawdown_list, bins=bins, density=True, alpha=0.5, label=label, color=color)
            plt.xlabel('maximal drawdown')
            # plt.legend()

        except:
            print('failed ', file_name)
            pass

