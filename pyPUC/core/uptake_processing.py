# -*- coding: utf-8 -*-
"""
Module for processing multiple gas uptake isotherms. Use this to generate 
model isotherms from a set of experimental isotherm (using pygaps), then 
generate point isotherms from these isotherms with identical pressure points.
"""

import pygaps, os, numbers
import pandas as pd
import numpy as np
from pathlib import Path
from core.utils import make_path, read_data 
import datetime

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
                   positive = True, increasing = True):
    """
    Removes any bad datapoints from isotherm; automatically removes non-numeric
    and NaN. Options for removing decreasing pressures,
    negative pressures/loadings.

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

    Returns
    -------
    data : dataframe
        Cleaned isotherm.

    """
    data.columns = ['P', 'Conc.'] # so we can work with later
    # drop all non numeric and NaN
    data = data.dropna()
    data = (data
            .drop(data.columns, axis=1)
            .join(data[data.columns]
                  .apply(pd.to_numeric, errors='coerce')))
    data = data[data[data.columns]
                .notnull().all(axis=1)]
    data.reset_index(drop=True, inplace=True) # otherwise row comparison breaks

    # make list of negative/decreasing values.
    to_drop = [] 
    for index, row in data.iterrows():
        P = data.loc[index, 'P']
        Conc = data.loc[index, 'Conc.']
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

    to_drop = list(set(to_drop)) # make sure rows are unique.
    for t in to_drop: # drop all bad rows.
        data.drop(labels=t, axis=0, inplace=True)
    
    return data

def make_model_isotherm_dict(path, temperature, 
                             project=None, adsorbate=None, 
                             guess_models=['TSLangmuir', 
                                          'DSLangmuir'],
                             p_start=0.01, p_stop=20.00, p_step=0.01,
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
        data = read_data(f"{path}{files_samples.file[i]}")

        # data = pd.read_excel(path_to_file, engine='openpyxl')
        if clean_isos == True: # remove any bad data
            data = pd.DataFrame(clean_isotherms(data))
        if cut_data is not None:
            if cut_data > 0:
                data = data[data['P'] < cut_data]
            else:
                print('invalid value for cut_data, please input a pressure')
                continue

        data['P'] = data['P'].multiply(0.001) # assume data in mbar, convert to bar
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
            temperature_unit='K',

            material = files_samples.loc[i, 'sample'],
            adsorbate = adsorbate,
            temperature = temperature,
            )

        # then atempt to fit models to point isotherm
        model_iso = pygaps.ModelIsotherm.from_pointisotherm(
                                        isotherm,
                                        branch='ads',
                                        model=guess_models,
                                        verbose=verbose
                                        )
        # and generate a point isotherm
        pressure_points = np.arange(p_start, p_stop, p_step)
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
    print("...done")
    return loading_df
    
def make_report(project, sorptive, temperature, guess_models,
          p_start, p_stop, p_step):
    """
    Generates a report file for the current analysis.

    Parameters
    ----------

    Returns
    -------
    """
    path = make_path('source', project, sorptive, 'uptake')
    date_time = datetime.datetime.now().strftime('%H:%M on %y-%m-%d')
    header = f"""
                Loading DataFrame generated at {date_time}
                ------------------------------------------------
                """
    body = f"""
                Project name = {project}, Sorptive = {sorptive}, T = {temperature} K
                Models used = {guess_models}, Number of isotherms = {len(os.listdir(path))}
                Pressure range = {p_start} - {p_stop} bar, with increment {p_step}
                """
    report = f"{header}{body}"
    return report

def process_uptake(project, sorptive, temperature, now,
                    guess_models, p_start=0.01, p_stop=10.00, p_step=0.01):
    path = make_path('source', project, sorptive, 'uptake')
    data = make_model_isotherm_dict(path, temperature, 
                                 guess_models, adsorbate=sorptive, 
                                 p_start=p_start, 
                                  p_stop=p_stop, p_step=p_step, 
                                 clean_isos=True)
    results_path = f"{make_path('result', project, sorptive)}{now}/"
    
    print(f"""Generating loading DataFrame 
          Project = {project}
          Sorptive = {sorptive}
          Temperature = {temperature} K
          Models used = {guess_models}
          ...
          """
         )
    loadings = loading_df(data)
    
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    loadings.to_csv(f"{results_path}loading_df.csv")

    report = make_report(project, sorptive, temperature, guess_models,
                         p_start, p_stop, p_step)
    report_txt = open(f"{results_path}loading_report.txt", 'w')
    report_txt.write(report)
    report_txt.close()
    return loadings 

def main(project, sorptive, temperature,
         guess_models, p_start=0.01, p_stop=10.00):
    now_1 = datetime.datetime.now()
    now = now_1.strftime('%y%m%d%H%M')
    path = make_path('source', project, sorptive, 'uptake')
    data_dict = make_model_isotherm_dict(path, temperature, 
                                         guess_models, adsorbate=sorptive, 
                                         p_start=p_start, p_stop=p_stop,
                                         clean_isos=True)
    loadings = loading_df(data_dict)
    results_path = f"{make_path('result', project, sorptive)}{now}/"
    print(results_path)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    loadings.to_csv(f"{results_path}loading_df.csv")

    report = make_report(project, sorptive, temperature, guess_models,  p_start, p_stop, 0.1)
    report_txt = open(f"{results_path}loading_report.txt", 'w')
    report_txt.write(report)
    report_txt.close()
    return loadings

if __name__ == '__main__':
    # for testing
    
    project = '0010_dualiso_co2'
    sorptive = 'co2'
    temperature = 291 
    guess_models = ['DSLangmuir', 'TSLangmuir',]
    p_start, p_stop = 0.01, 5.00
    loadings = main(project, sorptive, temperature,
                    guess_models, 
                    p_start=p_start, p_stop=p_stop
                    )

