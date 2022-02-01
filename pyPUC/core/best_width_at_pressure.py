"""
Correlates volumes or surface area within all possible pore ranges to gas
uptakes at all pressures, in user-defined ranges.
"""

import datetime
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')
import os, sys, signal
import numpy as np
import pandas as pd
from scipy.stats import linregress
from core.utils import make_path, print_progress_bar
import matplotlib.pyplot as plt

def make_correlation_df(loading_df, param_df, data_dict, now,
                        results_path=None,
                        show_correlations=False):

    colnames = ['wmin', 'wmax', 'p', 'r_sq', 'm', 'c', 'x', 'y']
    correlation_df = pd.DataFrame(columns = colnames)
    n=0
    df_size = len(param_df) * len(loading_df)
    print(f"Calculating porosity-loading correlations. {df_size} correlations to perform")
    for index, row in param_df.iterrows():
        x = []
        wmin = row['wmin']
        wmax = row['wmax']
        for d in data_dict:
            x.append(row['param_'+d])
        x = np.array(x)
        r_sq_at_width = np.array([])
        for index, row in loading_df.iterrows():
            p = row['pressure']
            y = []
            for d in data_dict:
                y.append(row['loading_'+d])
            y = np.array(y)
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            r_sq = r_value**2
            np.append(r_sq_at_width, r_sq)
            colvalues = [wmin, wmax, p, r_sq, slope, intercept, x, y]
            correlation_one_row = pd.DataFrame([colvalues],
                                               columns=colnames)
            n+=1

            correlation_df = correlation_df.append(correlation_one_row,
                                                   ignore_index=True)
            print_progress_bar(n, df_size, '')

    correlation_df = correlation_df[correlation_df.p != 0.0]
    print(f"\ncorrelation_df finished!")

    return correlation_df, n  

def find_best_width_at_pressure(correlation_df, 
                                drop=False):
    print("Finding best pore width at all pressures.")
    colnames = ['wmin', 'wmax', 'p', 'r_sq', 'm', 'c', 'x', 'y']
    best_width_at_pressure = pd.DataFrame(columns=colnames)
    bwap = best_width_at_pressure

    for p in correlation_df.p.unique():
        rows = correlation_df[correlation_df['p']==p].index.tolist()
        best = 0
        for r in rows:
            r_sq = correlation_df.loc[r, 'r_sq']
            m = correlation_df.loc[r, 'm']
            c = correlation_df.loc[r, 'c']
            if r_sq > best:
                best = r_sq
                wmin = correlation_df.loc[r, 'wmin']
                wmax = correlation_df.loc[r, 'wmax']
                best_m = m
                best_c = c
                x = correlation_df.loc[r, 'x']
                y = correlation_df.loc[r, 'y']
                if drop:
                   correlation_df.drop(index=r, inplace=True) 

        colvalues = [wmin, wmax, p, best, best_m, best_c, x, y]
        add_to_bwap = pd.DataFrame([colvalues],
                                   columns=colnames)
        bwap = bwap.append(add_to_bwap,
                           ignore_index=True)

    print("...done")

    return bwap

def top_widths_at_pressure(depth, 
                           correlation_df, 
                           graph=True, show_correlations=False):
    twap = {}
    for d in range(depth):
         twap[d] = find_best_width_at_pressure(correlation_df,
                                          results_path, graph, show_correlations,
                                          drop=True)
    return twap

def graph_bwap(bwap, results_path):
    f, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=96)
    ax.plot(bwap.p, bwap.wmin,
            color='b', label='min')
    ax.plot(bwap.p, bwap.wmax,
            color='b', label='max')  
    ax.set_xlabel('Pressure / bar')
    ax.set_ylabel('Pore width / $\AA$')
    f.savefig(f"{results_path}optimum_pore_size.png", dpi=200)
    plt.close(f)

def correlation_requirements(correlation_df, 
                             positive_slope=True,
                             r_sq=None,
                             p=None,
                             w_range=None):

    if positive_slope == True:
        correlation_df = correlation_df[correlation_df['m'] > 0]

    if r_sq is not None: 
        if type(r_sq) == float and 0 <= r_sq <= 1 :
            correlation_df = correlation_df[correlation_df['r_sq'] > r_sq]
        else:
            print('Please use a number between 0 and 1 for r_sq')

    if p is not None:
        if type(p) == float or type(p) == int:
            if p > 0:
                correlation_df = correlation_df[correlation_df['p'] > p]
        else:
            print('Please use an number value for p')

    if w_range is not None:
        if type(w_range) == tuple:
            if len(w_range) == 1:
                correlation_df = correlation_df[correlation_df['wmin'] > w_range[0]]
            else:
                correlation_df = correlation_df[correlation_df['wmin'] > w_range[0]]
                print(correlation_df)
                correlation_df = correlation_df[correlation_df['wmax'] < w_range[1]]
        else:
            print('''
                  Variable w_range must be assigned as a tuple. See help for
                  more information.
                  ''')

    return correlation_df

def plot_correlations(df, results_path):
    for index, row in df.iterrows(): 
        f, ax = plt.subplots(nrows=1, ncols=1,
                             figsize=(8, 8), dpi=96)

        x = df.loc[index, 'x']
        y = df.loc[index, 'y']

        ax.scatter(x, y,
                   ec='k', fc='none')

        x_line = np.linspace(min(x), max(x), 100)
        y_line = df.loc[index, 'm'] * x_line + df.loc[index, 'c']
        ax.plot(x_line, y_line, color='k')
        ax.annotate(f"$r^2$ = {format(df.loc[index, 'r_sq'], '.2f')}", 
                    xy=(0.05, 0.95), xycoords='axes fraction')
        path = f"{results_path}/plots/correlations/{df.loc[index, 'p']}/"
        if not os.path.exists(path):
            os.makedirs(path)
        name = f"{df.loc[index, 'wmin']}_{df.loc[index, 'wmax']}.png"
        f.savefig(f"{path}{name}")
        plt.close(f)
