import core.plots as plots
import core.utils as utils
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from core.labellines import labelLines
import pandas as pd
import numpy as np
import os

cmap = cm.get_cmap('copper')
def get_colors(cmap, n):
    array = np.arange(0, n, 1) / np.linalg.norm(np.arange(0, n, 1))
    colors = []
    for a in array:
        colors.append(cmap(a))
    return colors


fig, axs = plt.subplots(nrows=4, ncols=1,
                        figsize=(4, 11),
                        constrained_layout=True)

plots.annotate_axs(axs,
                   xy=(0.02, 0.92))
xticks = [0.1, 1.0, 2.0]
for i, a in enumerate(axs):
    a.semilogx()
    a.set_xlim(0.1, 2)
    a.set_xticks(xticks, labels=[f"{utils.format_num(x)}" for x in xticks])
    a.set_ylim(0, 1)
    a.set_ylabel("$r^2$")
    #if np.where(axs == a) == len(axs) - 1:
        #a.set_xlabel("$P\ /\ bar$")
#    a.annotate(ax_lab[i], xy=(0.03, 0.9),
#               xycoords='axes fraction')

project = '0080_dual'
path = f"{utils.make_path('result', project)}hpc/new/correlations/V/split/"
colors = ['blue', 'red', 'grey']
lines = ['dotted', 'dashed', 'solid']

sorptives = ['n2', 'o2', 'h2']

wmax_list = [5.0, 6.0, 7.0, 10]
for i, wmax in enumerate(wmax_list):
    for j, s in enumerate(sorptives):
        if wmax == 20 and s == 'h2':
            wmax = 10
        dat = pd.read_csv(f"{path}wmax{wmax}/{s}.csv")
        axs[i].plot(dat.p, dat.r_sq,
                    color=colors[j],
                    linestyle=lines[j]
                   )

axs[3].legend(labels=['$N_2$', '$O_2$', '$H_2$'],
              frameon=False)
axs[3].set_xlabel("$P\ \\rm{/\ bar}$")
fig.savefig(f"{utils.make_path('result', project)}hpc/new/plots/regions.png",
            dpi=300,
            bbox_inches='tight')

"""
n2_ultramicro = split_dict['n2']['wmin3.6_wmax7.0']
o2_ultramicro = split_dict[['wmin3.6_wmax7.0']

h2_dat = split_dict['h2']
h2_ultramicro = h2_dat['wmin3.0_wmax7.0']

for i, dat in enumerate([n2_ultramicro,
                         o2_ultramicro,
                         h2_ultramicro]):
    axs[0].plot(dat.p, dat.r_sq,
                color=colors[i])

fig.savefig(f"{path}hpc/new/plots/regions.png",
            dpi=300,
            bbox_inches='tight')

"""
"""
axs[3].set_xlabel("$P\ \\rm{/\ bar}$")

trad_keys = ['wmin3.6_wmax7.0',
             'wmin7.0_wmax20',
             'wmin20_wmax100']
labels = ['ultramicro',
          'supermicro',
          'meso']

colors = get_colors(cmap, 3)
for t in trad_keys:
    dat = data_dict[t]
    print(t)
    print(max(dat.r_sq))
    print(dat.loc[dat.index[dat.r_sq==max(dat.r_sq)], 'p'])
    axs[0].plot(dat.p, dat.r_sq,
                label=labels[trad_keys.index(t)],
                color=colors[trad_keys.index(t)])
print('\n')
xvals = [0.3, 4, 20]
labelLines(axs[0].get_lines(), zorder=2.5, xvals=xvals)

better_keys = ['wmin3.6_wmax10',
               'wmin10_wmax20',
               'wmin10_wmax100',
               'wmin20_wmax100',
               ]
labels = ['<10',
          '10-20',
          '>10',
          '>20']
colors = get_colors(cmap, 4)
for b in better_keys:
    dat = data_dict[b]
    print(b)
    print(max(dat.r_sq))
    print(dat.loc[dat.index[dat.r_sq==max(dat.r_sq)], 'p'])
    axs[1].plot(dat.p, dat.r_sq,
                label=labels[better_keys.index(b)],
                color=colors[better_keys.index(b)])
print('\n')

xvals=[1, 5, 12, 30]
labelLines(axs[1].get_lines(), zorder=2.5, xvals=xvals)

wmax_inc = {}
for key in data_dict:
    if 'wmin3.6_' in key:
        wmax_inc[key] = data_dict[key]

drop_keys = []

lim = 2
n = 0
max_width = 50
while n <= lim:
    for index, w in enumerate(wmax_inc):
        wmax = w.split('wmax')[1]
        if float(wmax) > max_width:
            drop_keys.append(w)
        if index % 2 == 0:
            if w not in drop_keys:
                drop_keys.append(w)

    for key in drop_keys:
        if key in wmax_inc:
            wmax_inc.pop(key)
    n+=1

wmax_inc.pop('wmin3.6_wmax35')
colors = get_colors(cmap, len(wmax_inc))
for i, w in enumerate(wmax_inc):
    dat = wmax_inc[w]
    print(w)
    print(max(dat.r_sq))
    print(dat.loc[dat.index[dat.r_sq==max(dat.r_sq)], 'p'])
    label = w.split('wmax')[1]
    axs[2].plot(dat.p, dat.r_sq,
                label=label,
                color=colors[i])
print('\n')

xvals = [10, 0.15, 0.3, 1.2, 2.5, 6, 10]
labelLines(axs[2].get_lines(), xvals=xvals, zorder=2.5)

wmax_inc = {}
drop_keys = []
for key in data_dict:
    if 'wmin7.0_' in key:
        wmax_inc[key] = data_dict[key]
        wmax = key.split('wmax')[1]
        if float(wmax) <= 7.0:
            drop_keys.append(key)

lim = 2
n = 0
max_width = 100
while n <= lim:
    for index, w in enumerate(wmax_inc):
        wmax = w.split('wmax')[1]
        if float(wmax) > max_width:
            drop_keys.append(w)
        if index % 2 == 0:
            if w not in drop_keys:
                drop_keys.append(w)

    for key in drop_keys:
        if key in wmax_inc:
            wmax_inc.pop(key)
    n+=1

drop_keys = ['wmin7.0_wmax40',
             'wmin7.0_wmax53',
             'wmin7.0_wmax69']

for key in drop_keys:
    if key in wmax_inc:
        wmax_inc.pop(key)

colors = get_colors(cmap, len(wmax_inc))
for i, w in enumerate(wmax_inc):
    dat = wmax_inc[w]
    print(w)
    print(max(dat.r_sq))
    print(dat.loc[dat.index[dat.r_sq==max(dat.r_sq)], 'p'])
    label = w.split('wmax')[1]
    axs[3].plot(dat.p, dat.r_sq, label=label,
                color=colors[i])
print('\n')

xvals = [0.8, 1.5, 3, 8, 16]
labelLines(axs[3].get_lines(), xvals=xvals, zorder=2.5)

#plt.set_cmap('viridis')


fig.savefig(f"{path}plots/correlation_change/corr_change_grid.png",
            bbox_inches='tight', dpi=300)
"""
