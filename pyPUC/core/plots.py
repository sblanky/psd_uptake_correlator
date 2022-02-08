import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import os
import re
import core.utils
import core.psd_processing
"""
Some default plotting tools.
"""
def bwap(bwap, results_path):
    f, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=96)
    ax.plot(bwap.p, bwap.wmin,
            color='b', label='min')
    ax.plot(bwap.p, bwap.wmax,
            color='b', label='max')  
    ax.set_xlabel('Pressure / bar')
    ax.set_ylabel('Pore width / $\AA$')
    f.savefig(f"{results_path}optimum_pore_size.png", dpi=200,
             bbox_inches='tight')
    plt.close(f)

def get_array_from_string(string):
    """
    Converts string of form str([<float> <float>]) to numpy array.

    Parameters
    ----------
    string : string
    
    Returns
    -------
    array : array
    """
    string = re.sub(r"\s+", ' ', string) # whitsespace
    # brackets
    string = string.replace('[', '')
    string = string.replace(']', '')
    array = np.fromstring(string, dtype=float, sep=' ')
    return array

def correlations(df, results_path,
                convert_string=False):
    """
    plots correlations from dataframe (correlation_df, twap, bwap).

    Parameters
    ----------
    df : DataFrame
    results_path : string
        where to save
    convert_string : bool
        Set true if df is read form file. Ensures array can be read.
        Default is False
    
    Returns
    -------
    None
    """
    for index, row in df.iterrows(): 
        f, ax = plt.subplots(nrows=1, ncols=1,
                             figsize=(8, 8), dpi=96)

        x = df.loc[index, 'x']
        y = df.loc[index, 'y']
        if convert_string:
            x = get_array_from_string(x)
            y = get_array_from_string(y)

        ax.scatter(x, y,
                   ec='k', fc='none')

        x_line = np.linspace(min(x), max(x), 100)
        y_line = df.loc[index, 'm'] * x_line + df.loc[index, 'c']
        ax.plot(x_line, y_line, color='k')
        r_sq = format(df.loc[index, 'r_sq'], '.2f')
        m = format(df.loc[index, 'm'], '.2f')
        c = format(df.loc[index, 'c'], '.2f')
        ax.annotate(f"$r^2$ = {r_sq}\nU = {m}V + {c}", 
                    xy=(0.05, 0.9), xycoords='axes fraction')
        ax.set_ylabel("U / $mmol g^{-1}$")
        ax.set_xlabel("V / $cm^3 g^{-1}$")
        p = df.loc[index, 'p']
        if p >= 10:
            p = format(p, '.2g')
        else:
            p = format(p, '#.2g')
        path = f"{results_path}/plots/correlations/{p}/"
        if not os.path.exists(path):
            os.makedirs(path)
        name = f"{format(df.loc[index, 'wmin'], '.1f')}_{format(df.loc[index, 'wmax'], '.1f')}.png"
        f.savefig(f"{path}{name}", dpi=200,
                 bbox_inches='tight')
        plt.close(f)

def vs_correlation(dfs, col, 
                   results_path, name,
                   xlabel='',
                   logx=False, xticks=None,
                   xlim=[3.6, 500], ylim=[0, 0.85], 
                   legend=None):
    f, ax = plt.subplots(nrows=1, ncols=1,
                         figsize=(8, 8), dpi=96)
    for d in dfs:
        dat = dfs[d] 
        ax.plot(dat[col], dat['r_sq'])
    if logx:
        ax.semilogx()
    if xticks is not None:
        ax.set_xticks(xticks, labels=[f"{x:.0f}" for x in xticks])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("$r^2$")
    if legend is None:
        ax.legend(dfs)
    else:
        ax.legend(legend)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    f.savefig(f"{results_path}{name}.png", 
              bbox_inches='tight')


def psd_fits(project, sorptive,
             dpi=300):
    path = core.utils.make_path('source', project,
                                sorptive, 'psd')

    data_dict = core.psd_processing.data_collect(path)

    fig, axs = plt.subplots(len(data_dict), 3, 
                            figsize=(12, 2.8 * len(data_dict)), 
                            dpi=96, sharex='col',
                            constrained_layout=True)

    for d, key in enumerate(data_dict):
        dat = data_dict[key]
        for a in [0, 2]:
            axs[d, a].semilogx()
        axs[d, 0].set_xlim(1e-7, 1)
        max_y = max(dat['AmountAdsorbed'])
        for a in [0, 1]:
            axs[d, a].set_ylim(0, max_y)
        axs[d, 0].set_ylim(0, max_y)
        axs[d, 1].set_xlim(0, 1)
        axs[d, 2].set_xlim(min(dat['w']), max(dat['w']))
        axs[d, 2].set_ylim(0, max(dat['dVdw']) * 1.1)
        for a in [0, 1, 2]:
            row = str(d+1)
            col = chr(a+97)
            axs[d, a].annotate(f'({col}{row})', 
                               xy=(0.89, 0.05), xycoords='axes fraction')
            if a in [0, 1]:
                axs[d, a].scatter(dat['PP0'], dat['AmountAdsorbed'],
                                  marker='^',
                                  color='k',
                                  fc='none',
                                  clip_on=False)
                axs[d, a].plot(dat['PP0'], dat['Fit'],
                               color='b',
                               clip_on=False)
                if a == 0: 
                    axs[d, a].set_ylabel("$Q\ /\ cm^3\ g^{-1}\ STP$")
            else:
                axs[d, a].plot(dat['w'], dat['dVdw'],
                               color='b',
                               clip_on=False)
                axs[d, a].set_ylabel("$PSD\ /\ cm^3\ g^{-1}\ \AA^{-1}$")
                axs[d, a].yaxis.tick_right()
                axs[d, a].yaxis.set_label_position('right')
                axs[d, a].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                xticks = [3.6, 10, 100]
                axs[d, a].set_xticks(xticks, labels=[f"{x:.0f}" for x in xticks])
            if d == len(data_dict) - 1:
                xlabel = ['$P/P_o$', '$P/P_o$', '$w\ /\ \AA$']
                axs[d, a].set_xlabel(xlabel[a])

    plt.savefig(f'{path}psd_plots.png',
                bbox_inches='tight',
                dpi=dpi)
