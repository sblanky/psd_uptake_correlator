# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 14:05:39 2021

@author: pcxtsbl
"""

import pandas as pd
import numpy as np
import glob, re
import math as m
import os

def make_path(project, sorptives):
    path = "./source_data/"+project+"/psd/"+sorptives+"/"
    return path

# gets samples names from filenames
def get_sample_name(file, path):
    path = path[:-1]
    path = path+r"\\"
    sample_name = re.sub(path, '', file)
    sample_name = re.sub(re.escape('.CSV'), '', 
                         sample_name, flags=re.IGNORECASE)
    #sample_name = re.sub(' ', '', sample_name)
    #print(sample_name+'x')
    return sample_name

# create dictionary of DataFrames
def make_data_dict(sample_names, path):
    '''create dictionary of DataFrames
    '''
    data_dict = {}
    fields = ('w', 'dV/dw', 'V cum', 'dS/dw', 'S cum')
    for s in sample_names:
        #print(s)
        sample_df = pd.read_csv(path+s+".CSV", usecols=fields)
        #sample_df = pd.read_csv(s+".CSV", usecols=fields)
        sample_df.columns = sample_df.columns.str.replace('/', '')
        sample_df.columns = sample_df.columns.str.replace(' ', '')
        data_dict[s] = sample_df   
    return data_dict

# get files
def data_collect(path):
    files = glob.glob(path+'*.csv')
    #print(files)
    sample_names = []
    for file in files:
        sample_name = get_sample_name(file, path)
        #print(sample_name)
        if sample_name not in sample_names:
            sample_names.append(sample_name)
    data_dict = make_data_dict(sample_names, path)
    return data_dict

def find_parameter(sample_df, measure, 
                   wmin=0, wmax=500):
    measure_column = str(measure+'cum')
    w = sample_df['w']
    w_array = w.to_numpy()
    empty_col = np.isnan(w_array[0])
    if empty_col == True:
        return None
    else:
        rows_max = np.max(list(np.where(w<wmax)))
        if wmin <= 3: # prevents zero-sized array
            rows_min = 0
        else:
            rows_min = np.max(list(np.where(w<wmin)))
        max_value = sample_df.loc[rows_max, measure_column]
        min_value = sample_df.loc[rows_min, measure_column]
        parameter = max_value - min_value
        return parameter
    
def parameter_df(data_dict, 
                 wstart=3, wstop=50, wstep=1,
                 logstep=False, num=None,
                 to_csv=False, csv_path=None):
    
    param_cols = ['wmax', 'wmin']
    for d in data_dict:
        param_cols.append('param_'+d)
    param_df = pd.DataFrame(columns = param_cols)
    
    i = 0 
    # logstep part needs work. Only do linear for now.
    if logstep == True:
        if num == None:
            print('''
                  if you set logstep as true, you must also specify
                  number of points (num) to calculate.
                  ''')
        else:  
            base=10
            wstart = m.log(wstart, base)
            wstop = m.log(wstop, base)
            array = np.logspace(wstart, wstop, base=base, num=num)
    elif logstep == False:
        if wstep == None:
            print('No interval (wstep) entered for linear sequence.')
        else:
            array = np.arange(wstart, wstop, wstep) 
    for wmax in array[1:]: 
        for wmin in np.arange(wstart, wmax, wstep):
            param_df.loc[i, 'wmax'] = wmax
            param_df.loc[i, 'wmin'] = wmin
            for d in data_dict: # finds parameters between wmin and wmax,
                                # appends to df
                param = find_parameter(data_dict[d], measure='V',
                                       wmin=wmin, wmax=wmax)
                param_df.loc[i, 'param_'+d] = param
            i+=1 # counter to go through all possible values of wmin for wmax
            
    if to_csv == True:
        if csv_path == None:
            print('No path specified, can\'t save csv')
        # saves results to csv if wanted.
        else:   
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)
            param_df.to_csv(csv_path+'param_df.csv')
    return param_df

def main(project, sorptives, wstart=3, wstop=500, wstep=1):
    path = make_path(project, sorptives)
    data_dict = data_collect(path)
    print(data_dict.keys())
    param_df = parameter_df(data_dict, 
                            wstart=wstart, wstop=wstop, wstep=wstep)
    return param_df, data_dict

if __name__ == '__main__':
    # for testing
    project = '0010_dualiso_co2'
    sorptives = 'n2h2'
    param_df, data_dict = main(project, sorptives)
    print(param_df)

 