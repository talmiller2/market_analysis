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
from slurm_functions import get_script_bootstrap_slave
from slurmpy.slurmpy import Slurm

pwd = os.getcwd()
bootstrap_script = get_script_bootstrap_slave()

# slurm_kwargs = {'partition': 'core'}  # default
slurm_kwargs = {'partition': 'socket'}


main_folder = '/home/talm/code/market_analysis/simulations_slurm/'

# define the period from which the synthetic realization will be drawn

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

# date_end = '2001-01-01'
# date_end = '2015-01-01'
date_end = '2020-09-30'
# date_end = '1996-09-30'


# num_realizations = 1
# num_realizations = 5
# num_realizations = 10
# num_realizations = 50
# num_realizations = 100
# num_realizations = 100
# num_realizations = 200
# num_realizations = 500
# num_realizations = 1000
num_realizations = 2000
# num_realizations = 5000

# frac_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# frac_list = [0, 1]
# frac_list = [0.3]
# frac_list = [0.9]
# frac_list = [1.0]
# frac_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
frac_list = np.linspace(0, 1, 20)
# frac_list = [0, 0.2, 0.4, 0.6, 0.8, 1]

stock1_list = []
stock2_list = []

# stock1_list += [  'VOO', 'VOO',  'VOO']
# stock2_list += ['VUSTX', 'SSO', 'UPRO']
# stock1_list += [  'QQQ', 'QQQ',  'QQQ']
# stock2_list += ['VUSTX', 'QLD', 'TQQQ']
# stock1_list += [   'SSO',   'UPRO',    'QLD',   'TQQQ']
# stock2_list += ['VUSTX3', 'VUSTX3', 'VUSTX3', 'VUSTX3']
# stock1_list += [  'VOO', 'VOO', 'VOO', 'VOO',  'VOO', 'SSO', 'SSO', 'UPRO', 'UPRO']
# stock2_list += ['VUSTX', 'TLT', 'TMF', 'SSO', 'UPRO', 'TLT', 'TMF',  'TLT',  'TMF']
# stock1_list += [  'QQQ', 'QQQ', 'QQQ', 'QQQ',  'QQQ', 'QLD', 'QLD', 'TQQQ', 'TQQQ']
# stock2_list += ['VUSTX', 'TLT', 'TMF', 'QLD', 'TQQQ', 'TLT', 'TMF',  'TLT',  'TMF']

stock1_list += [ 'VOO',  'VOO']
stock2_list += [ 'SSO', 'UPRO']
stock1_list += [ 'QQQ',  'QQQ']
stock2_list += [ 'QLD', 'TQQQ']
stock1_list += ['VUSTX', 'VUSTX', 'VUSTX', 'VUSTX', 'VUSTX', 'VUSTX']
stock2_list += [  'VOO',   'SSO',  'UPRO',   'QQQ',   'QLD',  'TQQQ']
stock1_list += ['VUSTX2', 'VUSTX2', 'VUSTX2', 'VUSTX2', 'VUSTX2', 'VUSTX2']
stock2_list += [   'VOO',    'SSO',   'UPRO',    'QQQ',    'QLD',   'TQQQ']
stock1_list += ['VUSTX3', 'VUSTX3', 'VUSTX3', 'VUSTX3', 'VUSTX3', 'VUSTX3']
stock2_list += [   'VOO',    'SSO',   'UPRO',    'QQQ',    'QLD',   'TQQQ']


total_number_of_runs = len(frac_list) * len(stock1_list)
cnt = 0
for stock1, stock2 in zip(stock1_list, stock2_list):
    print('stock1 ' + stock1 + ', stock2 ' + stock2)
    for frac in frac_list:
        print('frac = ' + str(frac))

        settings = define_default_settings()
        settings['date_start'] = date_start
        settings['date_end'] = date_end
        settings['ideal_portfolio_fractions'] = {stock1: 1-frac, stock2: frac}
        settings['tax_scheme'] = 'optimized'
        settings['tax_scheme'] = 'FIFO'
        # settings['tax_scheme'] = 'LIFO'
        settings['perform_bootstrap'] = True
        # settings['synthetic_period_years'] = 20
        settings['initial_investment'] = 10
        settings['periodic_investment'] = 1
        # settings['capital_gains_tax_percents'] = 0
        # settings['num_correlation_days'] = 1

        # save the result to plot later
        save_dir = ''
        save_dir += 'investment_initial_' + str(settings['initial_investment'])
        save_dir += '_periodic_' + str(settings['periodic_investment']) + '/'
        save_dir += 'period_' + str(settings['synthetic_period_years'])
        save_dir += '_cd_' + str(settings['num_correlation_days'])
        save_dir += '_date_start_' + date_start
        if settings['tax_scheme'] != 'optimized':
            save_dir += '_tax_' + settings['tax_scheme']
        if settings['capital_gains_tax_percents'] == 0:
            save_dir += '_no_tax'
        save_dir += '/'
        save_dir = main_folder + '/' + save_dir
        print('save_dir: ' + str(save_dir))
        os.makedirs(save_dir, exist_ok=True)
        os.chdir(save_dir)

        sim_name = stock1 + '_' + '{:0.2f}'.format(1-frac) + '_' + stock2 + '_' + '{:0.2f}'.format(frac)
        print('sim_name : ' + str(sim_name))

        bootstrap_params = {}
        bootstrap_params['save_dir'] = save_dir
        bootstrap_params['sim_name'] = sim_name
        bootstrap_params['num_realizations'] = num_realizations

        command = bootstrap_script \
                  + ' --settings "' + str(settings) + '"' \
                  + ' --bootstrap_params "' + str(bootstrap_params) + '"'
        s = Slurm(sim_name, slurm_kwargs=slurm_kwargs)
        s.run(command)
        cnt += 1
        print('run # ' + str(cnt) + ' / ' + str(total_number_of_runs))

        os.chdir(pwd)

