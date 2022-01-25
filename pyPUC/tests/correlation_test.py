from core.best_width_at_pressure import make_correlation_df
from core.psd_processing import make_data_dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

path = '/mnt/c/Users/pcxtsbl/Documents/pyPUC/results/0000_example/2201201007/'
loading_df = pd.read_csv(f'{path}loading_df.csv') 
param_df = pd.read_csv(f'{path}param_df.csv')

path = '/mnt/c/Users/pcxtsbl/Documents/pyPUC/source_data/0000_example/psd/n2h2/'
sample_names = ['A', 'B', 'C', 'D']
data_dict = make_data_dict(sample_names, path)

now = '202201251538'
df, n = make_correlation_df(loading_df, param_df, data_dict, now)
df.to_csv('df.csv')

for index, row in df.iterrows(): 
    f, ax = plt.subplots(nrows=1, ncols=1,
                         figsize=(8, 8), dpi=96)

    x = df.loc[index, 'x']
    y = df.loc[index, 'y']

    ax.scatter(x, y,
               ec='k', fc='none')

    x_line = np.linspace(min(x), max(x), 100)
    y_line = df.loc[index, 'm'] * x_line + df.loc[index, 'c']
    ax.plot(x_line, y_line, color='k')
    ax.annotate(f"{df.loc[index, 'r_sq']}", 
                xy=(0.85, 0.5), xycoords='axes fraction')
    path = f"./tests/out/{df.loc[index, 'p']}/"
    if not os.path.exists(path):
        os.makedirs(path)
    name = f"{df.loc[index, 'wmin']}_{df.loc[index, 'wmax']}.png"
    f.savefig(f"{path}{name}")
    plt.close(f)
