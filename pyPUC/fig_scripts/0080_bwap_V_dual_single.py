import core.utils as utils
import core.plots as plots
import glob
import pandas as pd
import os

bwap_dict = {}
project = '0080_dual'
source_dir = f"{utils.make_path('result', project)}hpc/new/"
dfs_dir = f"{source_dir}correlations/"

bwap_dict = {}
for m in ['S', 'V']:
    for filename in glob.glob(f"{dfs_dir}{m}/*bwap.csv"):
        key = f"{m}_{os.path.basename(filename)[:-4]}"
        bwap_dict[key] = pd.read_csv(filename)

new_dict = {}
keys_ordered = ['V_n2_bwap',  'S_n2_bwap',
                'V_n2h2_bwap', 'S_n2h2_bwap']


for key in keys_ordered:
    new_dict[key] = bwap_dict[key]

colors=['tab:purple', 'tab:olive',
        'tab:purple', 'tab:olive']
results_path = f"{source_dir}plots/"
plots.bwap_grid(new_dict, results_path,
                ylim=[[3.0, 20]],
                xlim=[[0.1, 20]],
                figsize=(8, 6),
                colors=colors,
                annotations=['$N_2,\ V$', '$N_2,\ V$',
                             '$N_2/H_2,\ S$', '$N_2/H_2,\ S$'],
                name='bwap_V_dual_single'
               )
