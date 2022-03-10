import core.plots as plots
import core.utils as utils
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from core.labellines import labelLines
import pandas as pd
import numpy as np
import re

"""
Not working yet, problem with thin_dict. Use calc_0061.omega_gradient instead
"""
def new_dict(keys, old_dict):
    new_dict = {}
    for key in keys:
        if key in old_dict:
            new_dict[key] = old_dict[key]
    return new_dict

def thin_dict(data_dict,
              lim=2,
              min_width=3.6, max_width=50):
    for n in range(lim):
        for index, key in enumerate(data_dict):
            print(key)
            split_key = re.split(r'wmin|_wmax', key)
            for i, s in enumerate(split_key):
                print(i, s)
            print(split_key[2])
            """
            wmax = float(key.split('wmax')[1])
            wmin = float(key.split('wmin')[1].split('_')[0])
            if wmin < min_width or wmax > min_width or index % 2 == 0:
                if key not in drop_keys:
                    data_dict.pop(key)
    n=0
    while n <= lim:
        for index, key in enumerate(data_dict):
            print(index)
            print(key)
            for k in key.split('wmax'):
                print(k)
            wmax = float(key.split('wmax')[1])
            wmin = float(key.split('wmin')[1].split('_')[0])
            if wmin < min_width or wmax > min_width or index % 2 == 0:
                if key not in drop_keys:
                    data_dict.pop(key)
        n+=1
        """

    return data_dict

cmap = cm.get_cmap('copper')

fig, axs = plt.subplots(nrows=4, ncols=1,
                        figsize=(4, 11),
                        constrained_layout=True)

ax_lab = ['(a1)', '(a2)', '(b1)', '(b2)']

project = '0061_all'
path = utils.make_path('result', project)
correlation_df = pd.read_csv(f"{path}2202101349/correlation_df.csv")

data_core = utils.split_df(correlation_df, 'wmin', 'wmax')

trad_keys = ['wmin3.6_wmax7.0',
             'wmin7.0_wmax20',
             'wmin20_wmax100']

better_keys = ['wmin3.6_wmax10',
               'wmin10_wmax20',
               'wmin10_wmax100',
               'wmin20_wmax100',
               ]

trad = new_dict(trad_keys, data_core)
better = new_dict(better_keys, data_core)

new = thin_dict(data_core)
#for key in new:
#    print(key)

"""
ax_lab = ['(a1)', '(a2)', '(b1)', '(b2)']
xticks = [0.1, 1, 10, 40]
for i, a in enumerate(axs):
    a.semilogx()
    a.set_xlim(0.1, 40)
    a.set_xticks(xticks, labels=[f"{utils.format_num(x)}" for x in xticks])
    a.set_ylim(0, 0.9)
    a.set_ylabel("$r^2$")
    #if np.where(axs == a) == len(axs) - 1:
        #a.set_xlabel("$P\ /\ bar$")
    a.annotate(ax_lab[i], xy=(0.03, 0.9),
               xycoords='axes fraction')
axs[3].set_xlabel("$P\ /\ bar$")

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
