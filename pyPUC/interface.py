#!/usr/bin/env python3
print("Starting pyPUC...")

import sys, os
from core.psd_processing import process_psd, get_sample_name
from core.uptake_processing import process_uptake, make_files_samples_df
from core.best_width_at_pressure import make_correlation_df, top_widths_at_pressure
from core.utils import make_path
import datetime
import pandas as pd
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

print("""Please ensure you have your PSD and uptake data saved in the following
directory ./source_data/<project>/<uptake or psd>/<sorptive(s)>/. All
files should be .csv or .xlsx""")

project_dir = f"./source_data/"
project_dir_list = [filename for filename in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, filename))]
print("\nAvailable projects: ")
for f in project_dir_list:
    print(f)
project = input("Which project do you want to work on? ")
project_dir = f"{project_dir}{project}/"
psd_dir = f"{project_dir}psd/"
uptake_dir = f"{project_dir}uptake/"

while os.path.exists(project_dir) == False:
    print(f"{project_dir} does not exist in ./source_data/")
    project = input("Which project do you want to work on? ")
    project_dir = f"./source_data/{project}/"
    psd_dir = f"{project_dir}psd/"
    uptake_dir = f"{project_dir}uptake/"
while os.path.exists(psd_dir) == False:
    print(f"""{project_dir} doesn't contain psd folder. Please add a psd
folder or choose a different folder.""")
    project = input("Which project do you want to work on? ")
    psd_dir = make_path('source', project, application='psd')
    uptake_dir = f"{project_dir}uptake/"
while os.path.exists(uptake_dir) == False:
    print(f"""'{project_dir}' doesn't contain uptake folder. Please add
an uptake folder or choose a different folder.""")
    project = input("Which project do you want to work on? ")
    uptake_dir = make_path('source', project, application='uptake')

uptake_sorptive_list = [filename for filename in os.listdir(uptake_dir) if os.path.isdir(os.path.join(uptake_dir, filename))]
print("\nAvailable uptake sorptives: ")
for f in uptake_sorptive_list:
    print(f)
uptake_sorptive_prompt = "Which uptake sorptive do you want to use? "
uptake_sorptive = input(uptake_sorptive_prompt)
while uptake_sorptive not in uptake_sorptive_list:
    print(f"'{uptake_sorptive}' not in {psd_dir}")
    uptake_sorptive = input(uptake_sorptive_prompt)
uptake_dir = make_path('source', project, uptake_sorptive, 'uptake')

psd_sorptive_list = [filename for filename in os.listdir(psd_dir) if os.path.isdir(os.path.join(psd_dir, filename))]
print("\nAvailable psd sorptives: ")
for f in psd_sorptive_list:
    print(f)
psd_sorptive_prompt = f"""Which psd sorptive do you want to use? """
psd_sorptive = input(psd_sorptive_prompt)
while psd_sorptive not in psd_sorptive_list:
    print(f"'{psd_sorptive}' not in {psd_dir}")
    psd_sorptive = input(psd_sorptive_prompt)
psd_dir = make_path('source', project, psd_sorptive, 'psd')

uptake_samples = list(make_files_samples_df(uptake_dir).loc[:,'sample'])
psd_samples = []
for s in os.listdir(psd_dir):
    psd_samples.append(get_sample_name(s, psd_dir))

while uptake_samples != psd_samples:
    print(f"sample name mismatch:\nuptake:\t{uptake_samples}\npsd:\t{psd_samples}")
    C = input("please adjust files in directory. Input C to continue. ") 
    if C == 'C':
        uptake_samples = list(make_files_samples_df(uptake_dir).loc[:, 'sample'])
        psd_samples = []
        for s in os.listdir(psd_dir):
            psd_samples.append(get_sample_name(s, psd_dir))
        continue

while input("\nWould you like to create the loading dataframe? [y/n] ") == "y":
    results_path = f"{make_path('result', project)}/{now}/"
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    p_start = float(input("Start pressure:\t "))
    p_stop = float(input("End pressure:\t "))
    p_step = float(input("Increment:\t "))
    guess_models = ['Langmuir', 'DSLangmuir', 'TSLangmuir',
                    'GAB', 'Freundlich', 'DR', 'Toth', 
                   ]
    loading_df = process_uptake(project, uptake_sorptive, 298, now,
                                guess_models, 
                                p_start=p_start, p_stop=p_stop, i=p_step)
    loading_df.to_csv(f"{results_path}loading_df.csv")
    break

while input("\nWould you like to create the parameter dataframe? [y/n] ") == "y":
    print("""A dataframe of parameters within pore ranges will now be created according to your input""")
    print("""Please width values in angstroms""")
    wstart = float(input("Start width:\t "))
    wstop = float(input("End width:\t "))
    wstep = float(input("Increment:\t "))
    psd_parameter = input("Input S for surface area and V for pore volume: ")

    param_df, data_dict = process_psd(project, psd_sorptive, psd_parameter, now,
                                      wstart=wstart, wstop=wstop, i=wstep)
    param_df.to_csv(f"{results_path}param_df.csv")
    break

correlation_df_size = len(param_df) * len(loading_df)
while input("\nWould you like to create the correlation dataframe?\n" 
            f"{correlation_df_size} regressions required. [y/n] ") == "y":
    correlation_df, n = make_correlation_df(loading_df, param_df, data_dict,
                                            now)
    correlation_df.to_csv(f"{results_path}correlation_df.csv")
    break

while input("\nWould you like to calculate the best n pore size ranges at each pressure? [y/n] ") == "y":
    depth = int(input("Please input n: "))
    twap = top_widths_at_pressure(depth, correlation_df, graph=False)
    twap_path = f"{results_path}twap/"
    if not os.path.exists(twap_path):
        os.makedirs(twap_path)
    for d in twap:
        twap[d].to_csv(f"{twap_path}{d}.csv")
    break
