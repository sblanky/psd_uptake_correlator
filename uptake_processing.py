# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 15:08:23 2021

@author: pcxtsbl
"""

import pygaps
import pandas as pd
import os, sys
import numpy as np
import math as m
import datetime
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

def make_path(project, sorptive):
    path = "./source_data/"+project+"/uptake/"+sorptive+"\\"
    return path

def make_files_samples_df(path):
    '''
    Parameters
    ----------
    path : string
        where to find CO2 isotherms (.xlsx)

    Returns
    -------
    files_samples : dataframe
        filepaths for all CO2 isotherms within path
        names of samples

    '''
    #print(path)
    files = os.listdir(path)
    files_samples = pd.DataFrame(data=None)
    isotherm_files = []
    for file in files:
        if (".xlsx" in file):
            isotherm_files.append(file)
    files_samples.insert(loc=0, 
              column='file', 
              value=isotherm_files, 
              allow_duplicates=False)
    
    samples = []
    for file in isotherm_files:
        sample = file.split('.')[0]
        if sample not in samples:
            samples.append(sample)
    files_samples.insert(loc=1, 
              column='sample', 
              value=samples, 
              allow_duplicates=False)
    
    return files_samples   

def clean_isotherms(data,
                    increasing=True, positive=True,
                    isna=True):
    to_drop = []
    for index, row in data.iterrows():
        P = data.loc[index, 'P']
        Conc = data.loc[index, 'P']
        if increasing == True:
            if index > 0:
                previous_index = index-1
                P_previous = data.loc[previous_index, 'P']
                diff = P - P_previous
                if diff < 0:
                    to_drop.append(index)
        if positive == True:
            if P < 0 or Conc < 0:
                to_drop.append(index)
        if isna == True:
            if pd.isna(P) or pd.isna(Conc):
                to_drop.append(index)
   
    
    to_drop = list(set(to_drop)) 
    for t in to_drop:
        data.drop(labels=t, axis=0, inplace=True)
    return data

def make_model_isotherm_dict(path, temperature, 
                             project=None, adsorbate=None, 
                             guess_models=['TSLangmuir', 
                                          'DSLangmuir'],
                             p_start=0.01, p_stop=20.00,
                             cut_data=None,
                             write_csv=False, verbose=False,
                             clean_isos=True): 
    model_isotherm_dict = {}
    
    files_samples = make_files_samples_df(path)
    for i in files_samples.index:
        path_to_file = path+files_samples.file[i]
        data = pd.read_excel(path_to_file)
        data['P'] = data['P'].multiply(0.001)
        if clean_isos == True:
            data = pd.DataFrame(clean_isotherms(data))
        #print(data)
        #print(files_samples.file[i])
        #print(data)
        #data = data[data['P'] > 0]
        if cut_data is not None:
            if cut_data > 0:
                data = data[data['P'] < cut_data]
            else:
                print('invalid value for cut_data, please input a pressure')
                continue
        
        isotherm = pygaps.PointIsotherm(
            isotherm_data=data,
            pressure_key='P',
            loading_key='Conc.',
            
            material = files_samples.loc[i, 'sample'],
            adsorbate = adsorbate,
            temperature = temperature,
            )
        '''
        results_path = "./results/"+project+"/"+now+"/model_"+adsorbate+"_isotherms/"
        
        if not os.path.exists(results_path):
                os.makedirs(results_path)
        sys.stdout = open(results_path+'modeling_info.txt', 'a')
        with open(results_path+'modeling_info.txt', 'a') as f:
            f.write(files_samples.loc[i, 'sample']+':')
            '''
        
        model_iso = pygaps.ModelIsotherm.from_pointisotherm(
            isotherm,                                                   
            branch='ads',
            guess_model=['DSLangmuir', 'Toth'],
            verbose=verbose
            )
        
        '''
        base = 10
        start = m.log(p_start, base)
        stop = m.log(p_stop, base)
        pressure_points = np.logspace(start, stop, num = 50)
        print('pressure_points'+str(pressure_points))
        '''
        pressure_points = np.arange(p_start, p_stop, 1)
        new_pointisotherm = pygaps.PointIsotherm.from_modelisotherm(
            model_iso,
            pressure_points = pressure_points
            )
        
        # need to fix
        if write_csv == True:
            if not os.path.exists(results_path):
                os.makedirs(results_path)
            pygaps.isotherm_to_csv(
                isotherm = new_pointisotherm,
                path = results_path+isotherm.material+'.csv')
        
        model_isotherm_dict[isotherm.material] = new_pointisotherm.data()
        
    return model_isotherm_dict

def loading_df(data_dict):
    loading_df = pd.DataFrame()
    first = list(data_dict.values())[0]
    loading_df['pressure'] = first.pressure
    for d in data_dict: # add loadings for each sample
        colname = 'loading_'+d
        loading_df[colname] = data_dict[d].loading  
    loading_df = loading_df.dropna()
    return loading_df
    
def generate_loading_df(project, sorptive, temperature,
                        guess_models, p_start=0.01, p_stop=10.00, p_step=1,
                        clean_isos=True):
    path = make_path(project, sorptive)
    data_dict = make_model_isotherm_dict(path, temperature, 
                                         project=None, adsorbate=None, 
                                         guess_models=['TSLangmuir', 
                                                      'DSLangmuir'],
                                         p_start=0.01, p_stop=20.00,
                                         cut_data=None,
                                         write_csv=False, verbose=False,
                                         clean_isos=True)
    return(loading_df(data_dict))


def main(project, sorptive, temperature,
         guess_models, p_start=0.01, p_stop=10.00):
    path = make_path(project, sorptive)
    data_dict = make_model_isotherm_dict(path, temperature, 
                                         guess_models, 
                                         p_start=p_start, p_stop=p_stop,
                                         clean_isos=True)
    return loading_df(data_dict)  

if __name__ == '__main__':
    # for testing
    project = '0010_dualiso_co2'
    sorptive = 'co2'
    temperature = 291 
    guess_models = ['DSLangmuir', 'TSLangmuir',]
    loadings = main(project, sorptive, temperature,
                    guess_models, p_start=0.01, p_stop=5.00
                    )
    print(loadings)
    
    

    
    