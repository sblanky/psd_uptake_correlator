import core.utils as utils
import core.plots as plots
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

project = '0061_all'
data_dir = utils.make_path('result', project)
data_dir = f"{data_dir}2202101349/twap/"
dat_V = pd.read_csv(f"{data_dir}0.csv")
data_dir = f"{utils.make_path('result', project)}S/twap/"
dat_S = pd.read_csv(f"{data_dir}0.csv")

fig, axs = plt.subplots(nrows=2, ncols=2,
                        figsize=(7.5, 5),
                        constrained_layout=True)

plots.annotate_axs(axs, xy=(0.88, 0.05))
data_dict = {}
data_dict['V'] = dat_V
data_dict['S'] = dat_S

colors=['tab:purple', 'tab:olive']
markers=['^', '^']
for col, param in enumerate(data_dict):
    dat = data_dict[param]
    axs[0, col].scatter(dat.p, dat.m,
                        ec=colors[col],
                        fc='none',
                        marker=markers[col],
                        clip_on=False)
    if param == 'V':
        ylabel = "$\\dfrac{\\rm{d}\\it{U}}{\\rm{d} \\it{V_{\Omega}}}\ \\rm{/\ mmol\ cm^{-3}}$"
    elif param == 'S':
        ylabel = "$\\dfrac{\\rm{d} \\it{U}}{\\rm{d} \\it{S_{\Omega}}}\ \\rm{/\ mmol\ m^{-2}}$"
    axs[0, col].set_ylabel(ylabel)
    axs[0, col].set_ylim(0, max(dat.m*1.05))
    axs[0, col].set_xlim(0, max(dat.p*1.05))

    dat['p_m'] = dat.p / dat.m
    axs[1, col].scatter(dat.p, dat.p_m,
                        ec=colors[col],
                        fc='none',
                        marker=markers[col],
                        clip_on=False)
    axs[1, col].set_xlabel("$P\ \\rm{/\ bar}$")
    axs[1, col].set_xlim(0, max(dat.p)*1.05)
    axs[1, col].set_ylim(0, max(dat.p_m)*1.05)

    slope, intercept, r_value, p_value, std_err = linregress(dat.p, dat.p_m)
    x_line = np.linspace(min(dat.p), max(dat.p), 100)
    y_line = slope * x_line + intercept
    axs[1, col].plot(x_line, y_line,
                     color=colors[col])
    slope = utils.format_num(slope)
    intercept = utils.format_num(intercept)
    axs[1, col].annotate("$m = $" + f"{slope}\n" + "$c = $" + f"{intercept}",
                         xy=(0.03, 0.84), xycoords='axes fraction')

    if param == 'V':
        ylabel = "$\\dfrac{\\rm{d}\\it{V_{\Omega}}}{\\rm{d}\\it{U}}\\it{P}\ \\rm{/\ bar \cdot cm^{3}\ mmol^{-1}}$"
    elif param == 'S':
        ylabel = "$\\dfrac{\\rm{d}\\it{S_{\Omega}}}{\\rm{d}\\it{U}}\\it{P}\ \\rm{/\ bar \cdot cm^{3}\ mmol^{-1}}$"
    axs[1, col].set_ylabel(ylabel)

plots_dir = f"{utils.make_path('result', project)}plots/"
fig.savefig(f"{plots_dir}d_gradient.png",
            dpi=300, bbox_inches='tight')
