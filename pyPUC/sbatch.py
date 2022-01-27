"""
Use to run batch job, e.g. on an HPC. Modify to your needs.
"""

import sys, os
from core.psd_processing import process_psd, get_sample_name
from core.uptake_processing import process_uptake, make_files_samples_df
from core.best_width_at_pressure import make_correlation_df, top_widths_at_pressure
from core.utils import make_path
import datetime
import pandas as pd
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

project = '0000_example'
uptake_sorptive = 'co2'
psd_sorptive = 'n2h2'
parameter = 'V'

results_dir = make_path('result', project)
results_dir = f'{results_dir}{now}/'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

uptake_dir = make_path('source', project, uptake_sorptive, application='uptake')
psd_dir = make_path('source', project, psd_sorptive, application='psd')

guess_models = ['Langmuir', 'DSLangmuir', 'TSLangmuir',
                'GAB', 'Freundlich', 'DR', 'Toth', 
               ]

loading_df = process_uptake(project, uptake_sorptive, 291, now, guess_models,
                            p_start=1, p_stop=10, p_step=1,
                           )
loading_df.to_csv(f'{results_dir}loading_df.csv')

parameter_df, data_dict = process_psd(project, psd_sorptive, parameter, now,
                                      wstart=4, wstop=10, wstep=1
                                      )
parameter_df.to_csv(f'{results_dir}parameter_df.csv')

correlation_df, n = make_correlation_df(loading_df, parameter_df, data_dict, now,
                                     results_path=results_dir)
correlation_df.to_csv(f'{results_dir}correlation_df.csv')

twap = top_widths_at_pressure(2, correlation_df, graph=False)
twap_path = f"{results_dir}twap/"
if not os.path.exists(twap_path):
    os.makedirs(twap_path)
for d in twap:
    twap[d].to_csv(f"{twap_path}{d}.csv")

