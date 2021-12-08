import sys, os
from psd_processing import process_psd, get_sample_name  
from uptake_processing import process_uptake, make_files_samples_df
from best_width_at_pressure import make_correlation_df, find_best_width_at_pressure, graph_bwap
from paths import make_path
import datetime
import pandas as pd
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

print("Starting pyPUC")
print("""Please ensure you have your PSD and uptake data saved in the following
directory ./source_data/<project>/<uptake or psd>/<sorptive(s)>/. All
files should be .csv or .xlsx""")

project = input("Which project do you want to work on? ")
project_dir = f"./source_data/{project}/"
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
uptake_sorptive_prompt = f"""Which uptake sorptive do you want to use? Options = {uptake_sorptive_list} """
uptake_sorptive = input(uptake_sorptive_prompt)
while uptake_sorptive not in uptake_sorptive_list:
    print(f"'{uptake_sorptive}' not in {psd_dir}")
    uptake_sorptive = input(uptake_sorptive_prompt)
uptake_dir = make_path('source', project, uptake_sorptive, 'uptake')

psd_sorptive_list = [filename for filename in os.listdir(psd_dir) if os.path.isdir(os.path.join(psd_dir, filename))]
psd_sorptive_prompt = f"""Which psd sorptive do you want to use? Options = {psd_sorptive_list} """
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

while input(f"Would you like to create a loading dataframe? [y/n]") == "y":
    results_path = f"{make_path('result', project)}/{now}/"
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    p_start = float(input("Start pressure:\t "))
    p_stop = float(input("End pressure:\t "))
    p_step = float(input("Increment:\t "))
    loading_df = process_uptake(project, uptake_sorptive, 298, now,
                                ['DSLangmuir', 'TSLangmuir'],
                                p_start=p_start, p_stop=p_stop, p_step=p_step)
    break

while input("Would you like to creat the parameter dataframe? [y/n]") == "y":
    print("""A dataframe of parameters within pore ranges will now be created according to your input""")
    print("""Please width values in angstroms""")
    wstart = float(input("Start width:\t "))
    wstop = float(input("End width:\t "))
    wstep = float(input("Increment:\t "))
    psd_parameter = input("Input S for surface area and V for pore volume: ")

    param_df, data_dict = process_psd(project, psd_sorptive, psd_parameter, now,
                                      wstart=wstart, wstop=wstop, wstep=wstep)
    break

correlation_df_size = len(param_df) * len(loading_df)
while input(f"""Would you like to creat the parameter dataframe? \
            {correlation_df_size} regressions required. [y/n]""") == "y":
    correlation_df, n = make_correlation_df(loading_df, param_df, data_dict, now,
                                            to_csv=True)
    break

"""
loading_df.to_csv(f"{results_path}loading_df.csv")

param_df, data_dict = process_psd('0020_thria', 'n2', 'V', now, wstart =4,
                                  wstop=100)
param_df.to_csv(f"{results_path}param_df.csv")

correlation_df, n = make_correlation_df(loading_df, param_df, data_dict, now,
                                        to_csv=True)
correlation_df.to_csv(f"{results_path}correlation_df.csv")

bwap = find_best_width_at_pressure(correlation_df, to_csv=False)
graph_bwap(bwap, results_path)
bwap.to_csv(f"{results_path}best_width_at_pressure.csv")
"""
