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

# color = None
# color = 'b'
color = 'g'
# color = 'r'
# color = 'orange'
# color = 'k'

use_single_color = True
# use_single_color = False

# define the period from which the synthetic realization will be drawn

# date_start = '1929-01-01'
# date_start = '1986-01-01'
date_start = '1987-01-01'
# date_start = '1989-01-01'
# date_start = '1993-01-29'
# date_start = '1999-12-30'
# date_start = '2000-01-01'
# date_start = '2001-01-01'
# date_start = '2002-01-01'
# date_start = '2003-01-01'

# date_end = '2001-01-01'
# date_end = '2015-01-01'
date_end = '2020-09-30'
# date_end = '1996-09-30'

settings = define_default_settings()

# save the result to plot later
save_dir = 'simulations/'
# save_dir += 'lower_res/'
# save_dir += 'investment_initial_' + str(settings['initial_investment'])
# save_dir += '_periodic_' + str(settings['periodic_investment']) + '/'
label_investment = 'investment_initial_1_periodic_0'
# label_investment = 'investment_initial_10_periodic_1/'
save_dir += label_investment + '/'
save_dir += 'period_' + str(settings['synthetic_period_years'])
save_dir += '_cd_' + str(settings['num_correlation_days'])
save_dir += '_date_start_' + date_start
save_dir += '_no_tax'
save_dir += '/'

file_names = os.listdir(save_dir)
files_filtered = []
# for file_name in file_names:
#     # if 'SSO' in file_name:
#     # if 'UPRO' in file_name:
#     # if 'VOO_1.0' in file_name:
#     # if 'VOO_0.0' in file_name:
#     # if 'QLD' in file_name:
#     if 'TQQQ' in file_name:
#     # if 'QQQ' in file_name:
#     # if 'VUSTX' in file_name and 'VOO' in file_name:
#     # if 'VUSTX' in file_name and 'QQQ' in file_name:
#     # if 'VUSTX' in file_name :
#         files_filtered += [file_name]

frac_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
# frac_list = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
# frac_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# frac_list = [0, 0.2, 0.4, 0.6, 0.8, 1]
# frac_list = [0, 0.1, 0.2]
# frac_list = [0, 0.1, 0.2, 0.9, 1.0]
# stock1 = 'VOO'
stock1 = 'QQQ'
stock2 = 'QLD'
# stock2 = 'TQQQ'
# stock2 = 'VUSTX'
files_filtered = ['yields_' + stock1 + '_' + '{:0.1f}'.format(1-frac)
                  + '_' + stock2 + '_' + '{:0.1f}'.format(frac) + '.txt'
                  for frac in frac_list]
# label = stock1 + '/' + stock2
label = label_investment + ': ' + stock1 + '/' + stock2

colors = cm.rainbow(np.linspace(0, 1, len(files_filtered)))

for ind_file, file_name in enumerate(files_filtered):
    if not use_single_color:
        color = colors[ind_file]
        label = file_name.split('yields_')[1]
        label = label.split('.txt')[0]

    try:
        yield_list = np.loadtxt(save_dir + file_name)

        # calculate numeric percentiles
        # percentiles = [10, 50, 95]
        percentiles = [5, 50, 95]
        yield_percentiles = []
        yield_percentiles_err_low = []
        yield_percentiles_err_high = []
        yield_percentiles_err = []
        for percentile in percentiles:
            # calculate yield based on data
            yield_percentile = np.percentile(yield_list, percentile)

            # calculate yield based on fit to data
            # fit_params = scipy.stats.lognorm.fit(yield_list)
            # fit_dist = scipy.stats.lognorm(*fit_params)
            # yield_percentile = fit_dist.ppf(percentile / 100.0)

            # estimate numeric error with bootstrap
            # bootstrap_realizations = 4
            bootstrap_realizations = 300
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

    except:
        pass

plt.figure(1)
plt.xlabel('yield ' + str(percentiles[0]) + '% percentile')
plt.ylabel('yield ' + str(percentiles[1]) + '% percentile')
plt.title('yields')
plt.grid(True)
plt.legend()

# plt.figure(2)
# plt.xlabel('yield ' + str(percentiles[0]) + '% percentile')
# plt.ylabel('yield ' + str(percentiles[2]) + '% percentile')
# plt.title('yields')
# plt.grid(True)
# plt.legend()