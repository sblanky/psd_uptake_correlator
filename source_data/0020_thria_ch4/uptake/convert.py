# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 14:03:05 2021

@author: pcxtsbl
"""
import os
import pandas as pd
import numpy as np

path = '.'
files = os.listdir(path)
files.remove('ch4')
files.remove('convert.py')

rows_to_drop = list(range(0, 16))
#rows_to_drop = np.array(rows_to_drop)
print(rows_to_drop)
for f in files:
    dat = pd.read_excel(f)
    dat.drop(range(0,16), inplace=True)
    dat.drop(range(105, 109), inplace=True)
    dat.columns = ['P', 'Conc.']
    dat.to_excel('./ch4/'+f+'.xlsx')
    print(dat)