import matplotlib.pyplot as plt
import numpy as np
import os
import re
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
                   logx=False, xlim=[3.6, 500], ylim=[0, 0.85], 
                   legend=None):
    f, ax = plt.subplots(nrows=1, ncols=1,
                         figsize=(8, 8), dpi=96)
    for d in dfs:
        dat = dfs[d] 
        # ax.plot(dat.loc[:,col], dat.loc[:,'r_sq'])
        ax.plot(dat[col], dat['r_sq'])
    if logx:
        ax.semilogx()
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

