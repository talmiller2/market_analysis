
import numpy as np

import matplotlib
from cycler import cycler
import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')

plt.rcParams.update({'font.size': 12})
matplotlib.rcParams.update({'axes.prop_cycle': cycler(color='bgrcmyk')})
plt.rcParams.update({'font.size': 12})

# plt.close('all')

cgt = 0.25
G_array = np.linspace(-1, 15, 100)

P_list = [-2, -1, 0, 1, 2]

for P in P_list:

    G_transition = (1 - np.sign(P) * cgt) / cgt * abs(P)

    delta_T = 0 * G_array
    for i, G in enumerate(G_array):
        if G <= 0:
            delta_T[i] = 0
        elif G <= G_transition:
            delta_T[i] = G * cgt / (1 - np.sign(P) * cgt)
        else:
            delta_T[i] = (G + P) * cgt

    plt.figure(1)
    plt.plot(G_array, delta_T, linewidth=2, label='$P$='+str(P))
    # plt.subplot(1, 3, 1)
    plt.xlabel('$G$')
    plt.ylabel('$\\Delta T$')
    # if synthetic_period_years == 10:
    #     plt.xlim([0, 2])
    # else:
    #     plt.xlim([0, 9])
    plt.grid(True)
    plt.legend()
