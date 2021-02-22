#!/usr/bin/env python3

import argparse
import ast
import os
import numpy as np

from market_functions import simulate_portfolio_evolution

parser = argparse.ArgumentParser()
parser.add_argument('--settings', help='settings (dict) for the portfolio simulation algorithm',
                    type=str, required=True)
parser.add_argument('--bootstrap_params', help='parameters (dict) for the bootstrap simulation',
                    type=str, required=True)

args = parser.parse_args()
print('args.settings = ' + str(args.settings))
print('args.bootstrap_params = ' + str(args.bootstrap_params))
settings = ast.literal_eval(args.settings)
bootstrap_params = ast.literal_eval(args.bootstrap_params)

# define log file
os.makedirs(bootstrap_params['save_dir'], exist_ok=True)
log_file_path = bootstrap_params['save_dir'] + '/log_' + bootstrap_params['sim_name'] + '.txt'
log_file = open(log_file_path, 'w')

# perform bootstrap loop
yield_list = []
yield_tax_free_list = []
yield_min_list = []
max_drawdown_list = []
monthly_buy_days_list = []
monthly_sell_days_list = []

for ind_real in range(bootstrap_params['num_realizations']):
    settings['seed'] = np.random.randint(1e6) + ind_real
    print('seed = ' + str(settings['seed']), file=log_file)

    data = simulate_portfolio_evolution(settings)

    # label = 'real ' + str(ind_real) + ', yield=' + '{:0.2f}'.format(data['total_yield'])
    # print(label, file=log_file)

    yield_list += [data['total_yield']]
    yield_tax_free_list += [data['total_yield_tax_free']]
    yield_min_list += [data['yield_min']]
    max_drawdown_list += [data['max_drawdown']]
    monthly_buy_days_list += [data['average_monthly_buy_days']]
    monthly_sell_days_list += [data['average_monthly_sell_days']]

# results_mat = np.array([yield_list, yield_tax_free_list, yield_min_list, max_drawdown_list,
#                         monthly_buy_days_list, monthly_sell_days_list]).T
results_mat = np.array([yield_list, yield_tax_free_list, yield_min_list, max_drawdown_list]).T

# save results to file
save_file_path = bootstrap_params['save_dir'] + '/' + bootstrap_params['sim_name'] + '.txt'
# np.savetxt(save_file_path, yield_list)
np.savetxt(save_file_path, results_mat)

log_file.close()