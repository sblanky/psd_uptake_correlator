import core.utils as utils
import pandas as pd
import numpy as np
import os

corr_dict = {}
split_dict = {}
project = '0080_dual'
path = utils.make_path('result', project)

sorptives = ['n2', 'o2', 'h2']
for s in sorptives:
    corr_dict[s] = pd.read_csv(f"{path}hpc/new/correlations/V/{s}_correlation_df.csv")
    split_dict[s] = utils.split_df(corr_dict[s], 'wmin', 'wmax')

#  wmax_list = [5.0, 7.0, 10, 20]
wmax_list = [15, 30, 50]
for s in sorptives:
    if s == 'h2':
        wmin = 3.0
    else:
        wmin = 3.6
    for wmax in wmax_list:
        if wmax > 10 and s == 'h2':
            print("wmax for h2 > 10,\ncontinuning to next value.")
            break
        else:
            key = f'wmin{wmin}_wmax{wmax}'
            print(f"{s}\n{key}\n")
            dat = split_dict[s][key]
            save_dir = f"{path}hpc/new/correlations/V/split/wmax{wmax}/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            dat.to_csv(f"{save_dir}{s}.csv")
