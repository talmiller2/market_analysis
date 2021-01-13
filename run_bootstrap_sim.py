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
color = 'b'
# color = 'g'
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


# num_realizations = 1
# num_realizations = 5
# num_realizations = 50
# num_realizations = 100
# num_realizations = 100
# num_realizations = 200
num_realizations = 500
# num_realizations = 1000
# num_realizations = 2000
# num_realizations = 5000

# frac_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# frac_list = [0, 1]
# frac_list = [0.3]
# frac_list = [0.9]
frac_list = [1.0]
# frac_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
# frac_list = [0, 0.2, 0.4, 0.6, 0.8, 1]

# stock1_list = ['VOO', 'VOO']
# stock2_list = ['SSO', 'UPRO']
stock1_list = ['QQQ']
stock2_list = ['QLD']
# stock1_list = ['QQQ', 'QQQ']
# stock2_list = ['QLD', 'TQQQ']
# stock1_list = ['QQQ', 'QQQ', 'VOO', 'VOO']
# stock2_list = ['QLD', 'TQQQ', 'SSO', 'UPRO']
# stock1_list = ['VOO', 'QQQ']
# stock2_list = ['VUSTX', 'VUSTX']
# stock1_list = ['VOO', 'QQQ', 'QQQ', 'QQQ', 'VOO', 'VOO']
# stock2_list = ['VUSTX', 'VUSTX', 'QLD', 'TQQQ', 'SSO', 'UPRO']


for stock1, stock2 in zip(stock1_list, stock2_list):
    print('stock1 ' + stock1 + ', stock2 ' + stock2)
    for frac in frac_list:
        print('frac = ' + str(frac))

        settings = define_default_settings()
        settings['date_start'] = date_start
        settings['date_end'] = date_end
        # settings['ideal_portfolio_fractions'] = {'VOO': 1.0}
        # settings['ideal_portfolio_fractions'] = {'QQQ': 1.0}
        # settings['ideal_portfolio_fractions'] = {'TQQQ': 1.0}
        # settings['ideal_portfolio_fractions'] = {'QQQ': 1-frac, 'TQQQ': frac}
        # settings['ideal_portfolio_fractions'] = {'QQQ': 1-frac, 'QLD': frac}
        # settings['ideal_portfolio_fractions'] = {'VOO': 1-frac, 'UPRO': frac}
        # settings['ideal_portfolio_fractions'] = {'VOO': 1-frac, 'SSO': frac}
        # settings['ideal_portfolio_fractions'] = {'VOO': 1-frac, lev_stock: frac}
        settings['ideal_portfolio_fractions'] = {stock1: 1-frac, stock2: frac}
        settings['tax_scheme'] = 'optimized'
        settings['perform_bootstrap'] = True
        # settings['initial_investment'] = 10
        # settings['periodic_investment'] = 1
        settings['capital_gains_tax_percents'] = 0


        yield_list = []

        for ind_real in range(num_realizations):
            # print(ind_real)

            data = simulate_portfolio_evolution(settings)
            label = 'real ' + str(ind_real) + ', yield=' + '{:0.2f}'.format(data['total_yield'])
            print(label)
            yield_list += [data['total_yield']]

            # plots
            # plt.figure(1)
            # plt.plot(data['total_portfolio_value'] / data['total_investment'], label=label, linewidth=1)
            # plt.xticks(data['inds_years'], data['label_years'])
            # plt.xlabel('years')
            # plt.ylabel('yield')
            # plt.title('portfolio: ' + str(settings['ideal_portfolio_fractions']))
            # plt.legend()
            # plt.grid(True)

        # save the result to plot later
        save_dir = 'simulations/'
        # save_dir += 'lower_res/'
        save_dir += 'investment_initial_' + str(settings['initial_investment'])
        save_dir += '_periodic_' + str(settings['periodic_investment']) + '/'
        save_dir += 'period_' + str(settings['synthetic_period_years'])
        save_dir += '_cd_' + str(settings['num_correlation_days'])
        save_dir += '_date_start_' + date_start
        save_dir += '_no_tax'
        save_dir += '/'

        # save results to file
        os.makedirs(save_dir, exist_ok=True)
        file_name = 'yields'
        # for stock_name in settings['ideal_portfolio_fractions'].keys():
            # file_name += '_' + stock_name + '_' + str(settings['ideal_portfolio_fractions'][stock_name])
            # file_name += '_' + stock_name + '_' + '{:0.1f}'.format(settings['ideal_portfolio_fractions'][stock_name])
        file_name += '_' + stock1 + '_' + '{:0.1f}'.format(1-frac) \
                     + '_' + stock2 + '_' + '{:0.1f}'.format(frac)
        file_name += '.txt'
        np.savetxt(save_dir + file_name, yield_list)

        # calculate numeric percentiles
        percentiles = [5, 50, 95]
        yield_percentiles_numeric = [np.percentile(yield_list, p) for p in percentiles]
        yield_percentiles_numeric_string = ','.join(['{:0.2f}'.format(y) for y in yield_percentiles_numeric])

        # fit with lognormal
        fit_params = scipy.stats.lognorm.fit(yield_list)
        fit_dist = scipy.stats.lognorm(*fit_params)
        yield_percentiles_fit = [fit_dist.ppf(p/100.0) for p in percentiles]
        yield_percentiles_fit_string = ','.join(['{:0.2f}'.format(y) for y in yield_percentiles_fit])
        chance_to_lose = '{:0.2f}'.format(fit_dist.cdf(1.0) * 100) + '%'

        # bins = np.linspace(0,max(yield_list),50)
        bins = np.linspace(0,yield_percentiles_fit[-1],50)
        x = np.linspace(0, max(bins), 200)
        pdf = scipy.stats.lognorm.pdf(x, *fit_params)

        # plot
        plt.figure(2)

        label ='boot %=' + str(yield_percentiles_numeric_string)
        plt.hist(yield_list, bins=bins, density=True, alpha=0.5, label=label, color=color)

        label = 'fit %=' + str(yield_percentiles_fit_string) + ', pl=' + str(chance_to_lose)
        plt.plot(x, pdf, label=label, color=color)
        plt.title('yield after ' + str(settings['synthetic_period_years']) + ' years')
        plt.legend()
