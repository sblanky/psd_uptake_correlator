# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 15:28:15 2021

@author: pcxtsbl
"""

# data is currently fucked
# maybe it's not.
import datetime
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')
import os
import numpy as np
import pandas as pd
from scipy.stats import linregress

from uptake_processing import main as loading_df
from psd_processing import main as parameter_df

import signal
import matplotlib.pyplot as plt

def make_source_path(project):
    source_path = "./source_data/"+project+"/"
    return source_path, project

def make_results_path(project):
    results_path = "./results/"+project+"/"+now+"/"
    return results_path

def make_correlation_df(loading_df, param_df, data_dict, 
                        to_csv=False, results_path=None,
                        show_correlations=False):
    colnames = ['wmin', 'wmax', 'p', 'r_sq', 'm', 'c']
    correlation_df = pd.DataFrame(columns = colnames)
    n=0
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
            colvalues = [wmin, wmax, p, r_sq, slope, intercept]
            correlation_one_row = pd.DataFrame([colvalues],
                                               columns=colnames)
            if show_correlations == True:
                f, ax = plt.subplots(nrows=1, ncols=1, 
                                     figsize=(8,8), dpi=96)
                ax.scatter(x, y, ec='k', fc='none')
                x_line = np.linspace(min(x), max(x), 100)
                y_line = slope*x_line+intercept
                ax.plot(x_line, y_line, color='k')
                path_to_graphs = csv_path+'/graphs/'+str(wmin)+'-'+str(wmax)+'/'
                if not os.path.exists(path_to_graphs):
                    os.makedirs(path_to_graphs)
                f.savefig(path_to_graphs+'p'+str(p)+'_bar.png')
                plt.close(f)
            n+=1
            print(n)
            correlation_df = correlation_df.append(correlation_one_row,
                                                   ignore_index=True)
    correlation_df = correlation_df[correlation_df.p != 0.0]
    
    if to_csv == True:
        if not os.path.exists(results_path):
            os.makedirs(results_path)
        correlation_df.to_csv(results_path+'correlation_df.csv')
    
    return correlation_df, n  

def find_best_width_at_pressure(correlation_df, 
                                to_csv=True, results_path=None, 
                                graph=True, show_correlations=False):
    colnames = ['wmin', 'wmax', 'p', 'r_sq', 'm', 'c']
    best_width_at_pressure = pd.DataFrame(columns = colnames)
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
        colvalues = [wmin, wmax, p, best, best_m, best_c]
        add_to_bwap = pd.DataFrame([colvalues],
                                   columns=colnames)
        bwap = bwap.append(add_to_bwap,
                           ignore_index=True)
    if to_csv == True:
        if not os.path.exists(results_path):
            os.makedirs(results_path)
        bwap.to_csv(results_path+'best_width_at_pressure.csv')
        
    if graph == True:
        f, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=96)
        ax.plot(bwap.p, bwap.wmin,
                color='b', label='min')
        ax.plot(bwap.p, bwap.wmax,
                color='b', label='max')  
        ax.set_xlabel('Pressure / bar')
        ax.set_ylabel('Pore width / $\AA$')
        f.savefig(results_path+'optimum_pore_size.png',
                    dpi=200)
        plt.close(f)
    
    return bwap

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
