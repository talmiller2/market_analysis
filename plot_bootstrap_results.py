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

invest_strategy = 'single'
# invest_strategy = 'monthly'

synthetic_period_years = 10
# synthetic_period_years = 20

num_correlation_days = 5
# num_correlation_days = 1

rebalance_percent = 10
# rebalance_percent = 20
# rebalance_percent = 30
# rebalance_percent = 40
# rebalance_percent = 50ß

year1 = 1989
year2 = 2003


tax_scheme = 'optimized'
# tax_scheme = 'LIFO'
# tax_scheme = 'FIFO'
# tax_scheme = 'no_tax'

index_base = 'NDX100'
# index_base = 'SP500'
if index_base == 'NDX100':
    index_stock = 'QQQ'
    index_X2_stock = 'QLD'
    index_X3_stock = 'TQQQ'
else:
    index_stock = 'VOO'
    index_X2_stock = 'SSO'
    index_X3_stock = 'UPRO'

bond_stock = 'VUSTX'
bond_X2_stock = 'VUSTX2'
bond_X3_stock = 'VUSTX3'

#### plot dependence on index / leveraged index portfolios

# color_list += ['b']
# year_start_list += [year1]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [index_stock]
# stock2_list += [index_X2_stock]
#
# color_list += ['g']
# year_start_list += [year1]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [index_stock]
# stock2_list += [index_X3_stock]
#
# color_list += ['r']
# year_start_list += [year2]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [index_stock]
# stock2_list += [index_X2_stock]
#
# color_list += ['k']
# year_start_list += [year2]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [index_stock]
# stock2_list += [index_X3_stock]


####  plot dependence on leveraged bond / index portfolios

year = year1
# year = year2

color_list += ['b']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_stock]
stock2_list += [index_stock]

color_list += ['g']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_X2_stock]
stock2_list += [index_X2_stock]

color_list += ['r']
year_start_list += [year]
investing_strategy_list += [invest_strategy]
correlation_days_list += [num_correlation_days]
synthetic_period_years_list += [synthetic_period_years]
tax_scheme_list += [tax_scheme]
stock1_list += [bond_X3_stock]
stock2_list += [index_X3_stock]

####  plot dependence on portfolio with leveraged index + different bond leverages

# year = year1
# # year = year2
#
# # curr_index = index_stock
# # curr_index = index_X2_stock
# curr_index = index_X3_stock
#
# color_list += ['b']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_stock]
# stock2_list += [curr_index]
#
# color_list += ['g']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_X2_stock]
# stock2_list += [curr_index]
#
# color_list += ['r']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_X3_stock]
# stock2_list += [curr_index]


#### plot both index leverage and bond leverage combinations (both years)

# stock1 = index_stock
# stock2 = index_X2_stock
# stock3 = bond_X2_stock
#
# # stock1 = index_stock
# # stock2 = index_X3_stock
# # stock3 = bond_X3_stock
#
# year = year1
#
# color_list += ['b']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['g']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock3]
# # stock2_list += [stock1]
# stock2_list += [stock2]
#
# year = year2
#
# color_list += ['r']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['orange']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock3]
# # stock2_list += [stock1]
# stock2_list += [stock2]

#### plot both index leverage and bond leverage combinations (both leverages)

# year = year1
# # year = year2
#
# stock1 = index_stock
# stock2 = index_X2_stock
# stock3 = bond_X2_stock
#
# color_list += ['b']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['g']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock3]
# # stock2_list += [stock1]
# stock2_list += [stock2]
#
#
# stock1 = index_stock
# stock2 = index_X3_stock
# stock3 = bond_X3_stock
#
# color_list += ['r']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['orange']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock3]
# # stock2_list += [stock1]
# stock2_list += [stock2]


####  plot dependence on tax scheme

# color_list += ['b']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_stock]
# stock2_list += [index_stock]
#
# color_list += ['g']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += ['FIFO']
# stock1_list += [bond_stock]
# stock2_list += [index_stock]
#
# color_list += ['r']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += ['LIFO']
# stock1_list += [bond_stock]
# stock2_list += [index_stock]
#
# color_list += ['k']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += ['no_tax']
# stock1_list += [bond_stock]
# stock2_list += [index_stock]

####  plot dependence on correlation days

# # stock1 = bond_stock
# # stock2 = index_stock
# stock1 = index_stock
# stock2 = index_X2_stock
#
# color_list += ['b']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['g']
# year_start_list += [1989]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [1]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]


####  plot dependence on total period

# # stock1 = bond_stock
# # stock2 = index_stock
# stock1 = index_stock
# stock2 = index_X2_stock
# stock3 = index_X3_stock
#
# # year = year1
# year = year2
#
# color_list += ['b']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [10]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['g']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [20]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock2]
#
# color_list += ['r']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [10]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock3]
#
# color_list += ['orange']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [20]
# tax_scheme_list += [tax_scheme]
# stock1_list += [stock1]
# stock2_list += [stock3]

####  plot dependence on rebalance percent

# year = year1
#
# color_list += ['b']
# # color_list += ['c']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_stock]
# stock2_list += [index_stock]
#
# color_list += ['g']
# # color_list += ['k']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_X2_stock]
# stock2_list += [index_X2_stock]
#
# color_list += ['r']
# # color_list += ['m']
# # color_list += ['c']
# year_start_list += [year]
# investing_strategy_list += [invest_strategy]
# correlation_days_list += [num_correlation_days]
# synthetic_period_years_list += [synthetic_period_years]
# tax_scheme_list += [tax_scheme]
# stock1_list += [bond_X3_stock]
# stock2_list += [index_X3_stock]


###########################

for ind_set, color in enumerate(color_list):
    year_start = year_start_list[ind_set]
    investing_strategy = investing_strategy_list[ind_set]
    correlation_days = correlation_days_list[ind_set]
    synthetic_period_years = synthetic_period_years_list[ind_set]
    tax_scheme = tax_scheme_list[ind_set]
    stock1 = stock1_list[ind_set]
    stock2 = stock2_list[ind_set]

    use_single_color = True
    # use_single_color = False

    # define the period from which the synthetic realization will be drawn
    if year_start == 1989:
        date_start = '1989-01-01'
    else:
        date_start = '2003-01-01'

    date_end = '2010-01-01'
    # date_end = '2019-01-01'
    # date_end = '2020-09-30'

    settings = define_default_settings()

    # save the result to plot later
    save_dir = ''
    # save_dir += 'simulations/'
    save_dir = '/Users/talmiller/Downloads/'
    save_dir += 'simulations_slurm/'
    # save_dir += 'simulations_slurm_2/'

    if investing_strategy == 'single':
        label_investment = 'investment_initial_1_periodic_0'
    else:
        label_investment = 'investment_initial_10_periodic_1/'
    save_dir += label_investment + '/'
    save_dir += 'period_' + str(synthetic_period_years)
    save_dir += '_cd_' + str(correlation_days)
    save_dir += '_date_start_' + date_start
    if date_end != '2020-09-30':
        save_dir += '_date_end_' + date_end
    if tax_scheme == 'no_tax':
        save_dir += '_no_tax'
    elif tax_scheme == 'FIFO':
        save_dir += '_tax_FIFO'
    elif tax_scheme == 'LIFO':
        save_dir += '_tax_LIFO'
    if rebalance_percent != 10:
        save_dir += '_rebalance_percent_20'
    save_dir += '/'

    # frac_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    frac_list = np.linspace(0, 1, 20)
    # frac_list = np.linspace(0, 1, 21)


    files_filtered = [stock1 + '_' + '{:0.2f}'.format(1-frac) + '_' + stock2 + '_' + '{:0.2f}'.format(frac) + '.txt'
                      for frac in frac_list]
    label = ''
    # label += 'y' + date_start[0:4] + ': '
    # label += 'y' + date_start[0:4] + ', cd' + str(correlation_days) + ': '
    label += 'y' + date_start[0:4] + ' ' + tax_scheme + ': '
    # label += 'y' + date_start[0:4] + ', rebalance@' + str(rebalance_percent) + '%: '
    # label += 'y' + date_start[0:4] + ', rebalance@' + str(rebalance_percent) + '%, ' + tax_scheme + ': '
    label += stock1 + '/' + stock2

    colors = cm.rainbow(np.linspace(0, 1, len(files_filtered)))

    for ind_file, file_name in enumerate(files_filtered):

        # prepare label for annotation
        # label_annotate = file_name.split('.txt')[0]
        label_annotate = file_name.split('.txt')[0].split('_')[-1]

        if not use_single_color:
            if color is not None:
                color = colors[ind_file]
            label = file_name.split('.txt')[0]

        try:

            yield_list = np.loadtxt(save_dir + file_name)

            # calculate numeric percentiles
            # percentiles = [10, 50, 95]
            percentiles = [5, 50, 95]
            # percentiles = [1, 50, 95]
            yield_percentiles = []
            yield_percentiles_err_low = []
            yield_percentiles_err_high = []
            yield_percentiles_err = []
            p_lose_err = []
            for percentile in percentiles:
                # calculate yield based on data
                yield_percentile = np.percentile(yield_list, percentile)

                # calculate yield based on fit to data
                # fit_params = scipy.stats.lognorm.fit(yield_list)
                # fit_dist = scipy.stats.lognorm(*fit_params)
                # yield_percentile = fit_dist.ppf(percentile / 100.0)

                # estimate numeric error with bootstrap
                # bootstrap_realizations = 100
                bootstrap_realizations = 300
                # bootstrap_realizations = 1000
                # bootstrap_err_CL = 95
                bootstrap_err_CL = 68
                yield_percentile_err_list = []
                for i in range(bootstrap_realizations):
                    inds_bootstrap = np.random.randint(low=1, high=len(yield_list), size=bootstrap_realizations)

                    # calculate yield based on data
                    yield_percentile_err_list += [np.percentile(yield_list[inds_bootstrap], percentile)]

                    # calculate yield based on fit to data
                    # fit_params = scipy.stats.lognorm.fit(yield_list[inds_bootstrap])
                    # fit_dist = scipy.stats.lognorm(*fit_params)
                    # yield_percentile_err_list += [fit_dist.ppf(percentile / 100.0)]

                yield_err_low = np.percentile(yield_percentile_err_list, 100 - bootstrap_err_CL)
                yield_err_low = abs(yield_percentile - yield_err_low)
                yield_err_high = np.percentile(yield_percentile_err_list, bootstrap_err_CL)
                yield_err_high = abs(yield_percentile - yield_err_high)
                yield_err = np.std(yield_percentile_err_list)

                yield_percentiles += [yield_percentile]
                yield_percentiles_err_low += [yield_err_low]
                yield_percentiles_err_high += [yield_err_high]
                yield_percentiles_err += [yield_err]

            # calculate probability to finish with less than the investement (yield<1)
            yield_cut_off = 1
            p_lose = len(np.where(yield_list < yield_cut_off)[0]) / len(yield_list)
            p_lose_err_list = []
            for i in range(bootstrap_realizations):
                inds_bootstrap = np.random.randint(low=1, high=len(yield_list), size=bootstrap_realizations)
                p_lose_err_list += [len(np.where(yield_list[inds_bootstrap] < yield_cut_off)[0]) / len(yield_list[inds_bootstrap])]
            p_lose_err_low = np.percentile(p_lose_err_list, 100 - bootstrap_err_CL)
            p_lose_err_low = abs(p_lose - p_lose_err_low)
            p_lose_err_high = np.percentile(p_lose_err_list, bootstrap_err_CL)
            p_lose_err_high = abs(p_lose - p_lose_err_high)

            # plot
            if use_single_color:
                if ind_file == 0:
                    label_curr = label
                else:
                    label_curr = None
            else:
                label_curr = label


            plt.figure(1)
            plt.scatter(yield_percentiles[0], yield_percentiles[1], color=color)
            text_dist = 0.02
            plt.annotate(label_annotate, (yield_percentiles[0] + text_dist, yield_percentiles[1] + text_dist), size=10, color=color)
            plt.errorbar(yield_percentiles[0], yield_percentiles[1],
                         yerr=np.array([[yield_percentiles_err_low[1]], [yield_percentiles_err_high[1]]]),
                         xerr=np.array([[yield_percentiles_err_low[0]], [yield_percentiles_err_high[0]]]),
                         label=label_curr,
                         color=color)
            # plt.errorbar(yield_percentiles[0], yield_percentiles[1],
            #              yerr=yield_percentiles_err[1],
            #              xerr=yield_percentiles_err[0],
            #              label=label_curr,
            #              color=color)


            # plt.figure(2)
            # plt.scatter(yield_percentiles[0], yield_percentiles[2], color=color)
            # plt.errorbar(yield_percentiles[0], yield_percentiles[2],
            #              yerr=np.array([[yield_percentiles_err_low[2]], [yield_percentiles_err_high[2]]]),
            #              xerr=np.array([[yield_percentiles_err_low[0]], [yield_percentiles_err_high[0]]]),
            #              label=label_curr,
            #              color=color)

            # plt.figure(3)
            # bins = np.linspace(0,yield_percentiles[-1],50)
            # x = np.linspace(0, max(bins), 200)
            # yield_percentiles_string = ','.join(['{:0.2f}'.format(y) for y in yield_percentiles])
            # label += ', boot %=' + yield_percentiles_string
            # plt.hist(yield_list, bins=bins, density=True, alpha=0.5, label=label, color=color)
            # plt.xlabel('yield')
            # plt.title('yield probability distribution')
            # plt.legend()

            # plt.figure(4)
            # plt.scatter(p_lose, yield_percentiles[1], color=color)
            # text_dist = 0.005
            # plt.annotate(label_annotate, (p_lose + text_dist, yield_percentiles[1] + text_dist), size=10, color=color)
            # plt.errorbar(p_lose, yield_percentiles[1],
            #              yerr=np.array([[yield_percentiles_err_low[1]], [yield_percentiles_err_high[1]]]),
            #              xerr=np.array([[p_lose_err_low], [p_lose_err_high]]),
            #              label=label_curr,
            #              color=color)
            #
            # plt.figure(5)
            # plt.scatter(p_lose, yield_percentiles[0], color=color)
            # text_dist = 0.005
            # plt.annotate(label_annotate, (p_lose + text_dist, yield_percentiles[0] + text_dist), size=10, color=color)
            # plt.errorbar(p_lose, yield_percentiles[0],
            #              yerr=np.array([[yield_percentiles_err_low[0]], [yield_percentiles_err_high[0]]]),
            #              xerr=np.array([[p_lose_err_low], [p_lose_err_high]]),
            #              label=label_curr,
            #              color=color)

        except:
            pass

    # joke
    # plt.scatter(3, 10, color='k')
    # plt.annotate('TSLA', (3 + text_dist, 10 + text_dist), size=20, color='k')
    # plt.scatter(-3, -10, color='k')
    # plt.annotate('BTC', (-3 + text_dist, -10 + text_dist), size=20, color='k')


    plt.figure(1)
    plt.xlabel('yield ' + str(percentiles[0]) + '% percentile')
    plt.ylabel('yield ' + str(percentiles[1]) + '% percentile')
    # plt.title('yields')
    # plt.title('yields after ' + str(synthetic_period_years) + ' years')
    plt.title('yields after ' + str(synthetic_period_years) + ' years (' + invest_strategy + ' investment)')
    plt.grid(True)
    plt.legend()

    # plt.figure(2)
    # plt.xlabel('yield ' + str(percentiles[0]) + '% percentile')
    # plt.ylabel('yield ' + str(percentiles[2]) + '% percentile')
    # plt.title('yields')
    # plt.grid(True)
    # plt.legend()

    # plt.figure(4)
    # plt.xlabel('p(yield<' + str(yield_cut_off) + ')')
    # plt.ylabel('yield ' + str(percentiles[1]) + '% percentile')
    # plt.title('yields after ' + str(synthetic_period_years) + ' years (' + invest_strategy + ' investment)')
    # plt.grid(True)
    # plt.legend()
    #
    # plt.figure(5)
    # plt.xlabel('p(yield<' + str(yield_cut_off) + ')')
    # plt.ylabel('yield ' + str(percentiles[0]) + '% percentile')
    # plt.title('yields after ' + str(synthetic_period_years) + ' years (' + invest_strategy + ' investment)')
    # plt.grid(True)
    # plt.legend()