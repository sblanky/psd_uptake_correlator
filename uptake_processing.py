# -*- coding: utf-8 -*-
"""
Module for processing multiple gas uptake isotherms. Use this to generate 
model isotherms from a set of experimental isotherm (using pygaps), then 
generate point isotherms from these isotherms with identical pressure points.
"""

import pygaps
import pandas as pd
import numpy as np
import os

import datetime
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

def make_path(project, sorptive):
    """
    Generates path to uptake isotherms based on the project and sorptives.

    Parameters
    ----------
    project : string
        Which project to work on.
    sorptive : string
        Which uptake sorptive to use.

    Returns
    -------
    path : string
        Location of uptake isotherms.

    """
    
    return f"./source_data/{project}/{sorptive}\\"

def make_files_samples_df(path):
    """
    Generates a dataframe with two columns; 
    'sample' - the sample name
    'file' - path to to the isotherm file (.xlsx)
    
    Parameters
    ----------
    path : string
        where to find CO2 isotherms (.xlsx)

    Returns
    -------
    files_samples : dataframe
        filepaths for all CO2 isotherms within path
        names of samples

    """
    files = os.listdir(path)
    files_samples = pd.DataFrame(data=None)
    
    isotherm_files = []
    for file in files: # add uptake relative filepaths to isotherm_files
        if (".xlsx" in file): # but only if .xlsx
            isotherm_files.append(file)
    files_samples.insert(loc=0, 
              column='file', 
              value=isotherm_files, 
              allow_duplicates=False) # then add to files_samples dataframe
    
    samples = []
    for file in isotherm_files: # get sample name from filepath
        sample = file.split('.')[0] 
        if sample not in samples:
            samples.append(sample)
    files_samples.insert(loc=1, # then add this column to files_samples
              column='sample', 
              value=samples, 
              allow_duplicates=False)
    
    return files_samples   

def clean_isotherms(data,
                    increasing=True, positive=True,
                    isna=True):
    """
    Removes any bad datapoints from isotherm; i.e. decreasing pressures,
    negative pressures/loadings, and any NaN values.

    Parameters
    ----------
    data : dataframe
        Isotherm file to clean.
    increasing : boolean, optional
        If True, the resultant isotherm will only including increasing pressure 
        values. Set false if using desorption branch. 
        The default is True.
    positive : boolean, optional
        If True, only positive pressures and loadings will be included. 
        The default is True.
    isna : boolean, optional
        If true, NaN will be removed. 
        The default is True.

    Returns
    -------
    data : dataframe
        Cleaned isotherm.

    """
    
    to_drop = [] # will be filled with rows to remove
    for index, row in data.iterrows(): # check rows for bad values
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
   
    
    to_drop = list(set(to_drop)) # make sure rows are unique.
    for t in to_drop: # drop all bad rows.
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
    """
    Makes a dictionary of point model isotherms from experimental data in path.

    Parameters
    ----------
    path : string
        Location of experimental isotherms.
    temperature : int
        Experimental temperature, needed for pygaps.PointIsotherm().
    project : string, optional
        Current project dataset. 
        The default is None.
    adsorbate : string, optional
        Experimental adsorbate, needed for pygaps.PointIsotherm. 
        The default is None.
    guess_models : list, optional
        Models to use when fitting to experimental isotherm. 
        The default is ['TSLangmuir', 'DSLangmuir'].
    p_start : int, float, optional
        Initial pressure point of point isotherm generated from fit. 
        The default is 0.01.
    p_stop : int, float, optional
        final pressure point of point isotherm generated from fit.
        The default is 20.00.
    cut_data : int, float, optional
        Cuts experimental data at some pressure, to avoid using modeling to 
        all pressure points if not needed. 
        The default is None.
    write_csv : boolean, optional
        Writes a csv file of each generated point isotherm. The default is False.
    verbose : boolean, optional
        If true, the process of modelling will be displayed both in the console
        and as plots in plot window (if using IDE). 
        The default is False.
    clean_isos : boolean, optional
        If true, bad data will be removed from the isotherms. 
        The default is True.

    Returns
    -------
    model_isotherm_dict : dictionary
        A dictionary of point model isotherms generated from each experimental
        isotherm. Pressures will be identical for all isotherms in this 
        dictionary.

    """
    
    model_isotherm_dict = {}
    
    files_samples = make_files_samples_df(path)
    for i in files_samples.index:
        path_to_file = path+files_samples.file[i]
        data = pd.read_excel(path_to_file)
        data['P'] = data['P'].multiply(0.001) # assume data in mbar, convert to bar
        if clean_isos == True: # remove any bad data
            data = pd.DataFrame(clean_isotherms(data))
        if cut_data is not None:
            if cut_data > 0:
                data = data[data['P'] < cut_data]
            else:
                print('invalid value for cut_data, please input a pressure')
                continue
        
        isotherm = pygaps.PointIsotherm( # reading in data as point isotherm
            isotherm_data=data,
            pressure_key='P',
            loading_key='Conc.',
            
            pressure_mode='absolute',       
            pressure_unit='bar',            
            material_basis='mass',          
            material_unit='g',            
            loading_basis='molar',          
            loading_unit='mmol',
            
            material = files_samples.loc[i, 'sample'],
            adsorbate = adsorbate,
            temperature = temperature,
            )
        
        # then atempt to fit models to point isotherm
        model_iso = pygaps.ModelIsotherm.from_pointisotherm(
                                        isotherm,                                                   
                                        branch='ads',
                                        guess_model=guess_models,
                                        verbose=verbose
                                        )
        
        # and generate a point isotherm
        pressure_points = np.arange(p_start, p_stop, 1)
        new_pointisotherm = pygaps.PointIsotherm.from_modelisotherm(
            model_iso,
            pressure_points = pressure_points
            ) 
        
        if write_csv == True: # not working, fix later
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
    
    

    
    