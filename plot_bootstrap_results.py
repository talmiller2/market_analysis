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

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
# matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})

# plt.close('all')

# color = None
# color = 'b'
color = 'g'
# color = 'r'
# color = 'k'

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

# frac_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# frac_list = [0.3]
# frac_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
frac_list = [0, 0.2, 0.4, 0.6, 0.8, 1]

settings = define_default_settings()

# save the result to plot later
save_dir = 'simulations/'
save_dir += 'lower_res/'
# save_dir += 'investment_initial_' + str(settings['initial_investment'])
# save_dir += '_periodic_' + str(settings['periodic_investment']) + '/'
save_dir += 'period_' + str(settings['synthetic_period_years'])
save_dir += '_cd_' + str(settings['num_correlation_days'])
save_dir += '_date_start_' + date_start
save_dir += '/'

file_names = os.listdir(save_dir)
for file_name in file_names:
    # if 'QLD' in file_name:
    if 'TQQQ' in file_name:
        label = file_name.split('yields_')[1]
        label = label.split('.txt')[0]

        yield_list = np.loadtxt(save_dir + file_name)


        # calculate numeric percentiles
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
            yield_err_high = np.percentile(yield_percentile_err_list, bootstrap_err_CL)
            # yield_err = np.std(yield_percentile_err_list)

            yield_percentiles += [yield_percentile]
            yield_percentiles_err_low += [yield_err_low]
            yield_percentiles_err_high += [yield_err_high]
            # yield_percentiles_err += [yield_err]


        # plot
        plt.figure(1)
        # plt.scatter(yield_percentiles[0], yield_percentiles[1], label=file_name)
        plt.errorbar(yield_percentiles[0], yield_percentiles[1],
                     yerr=np.array([[yield_percentiles_err_low[1]], [yield_percentiles_err_high[1]]]),
                     xerr=np.array([[yield_percentiles_err_low[0]], [yield_percentiles_err_high[0]]]),
                     label=label,
                     color=color)
        # plt.errorbar(yield_percentiles[0], yield_percentiles[1],
        #              yerr=yield_percentiles_err[1],
        #              xerr=yield_percentiles_err[0],
        #              label=label)
        #
        # label ='boot %=' + str(yield_percentiles_numeric_string)
        # plt.hist(yield_list, bins=bins, density=True, alpha=0.5, label=label, color=color)
        #
        # label = 'fit %=' + str(yield_percentiles_fit_string) + ', pl=' + str(chance_to_lose)
        # plt.plot(x, pdf, label=label, color=color)
        # plt.title('yield after ' + str(settings['synthetic_period_years']) + ' years')

        plt.xlabel('yield 5% percentile')
        plt.ylabel('yield 50% percentile')
        plt.title('50% vs 5% probability yields')
        plt.grid(True)
        plt.legend()
