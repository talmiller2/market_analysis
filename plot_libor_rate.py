
import matplotlib
from aux_functions import load_stock_data, get_libor_rate, get_year_labels
from cycler import cycler

import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})

plt.close('all')

# date_start = '1980-01-01'
date_start = '1986-01-01'
date_end = '2020-09-30'

dates, _ = load_stock_data('SP500', date_start, date_end)
inds_years, label_years = get_year_labels(dates)
libor_rate = get_libor_rate(dates)

# plots
plt.figure(1)
plt.plot(libor_rate, linewidth=2)
plt.xticks(inds_years, label_years, rotation='vertical')
plt.ylabel('libor rate %')
plt.title('LIBOR 1-month loan rate')
plt.grid(True)
plt.tight_layout()

