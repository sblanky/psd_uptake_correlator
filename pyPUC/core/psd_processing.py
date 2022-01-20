import pandas as pd
import numpy as np
import math as m
import glob, re, os
from core.utils import make_path, print_progress_bar, read_data
import datetime
now_1 = datetime.datetime.now()
now = now_1.strftime('%y%m%d%H%M')

def get_sample_name(file, path):
    """
    Gets samples names from filenames.

    Parameters
    ----------
    file : string
        Individual file where PSD file is located.
    path : string
        Location of PSD files.

    Returns
    -------
    sample_name : string
        Name of sample.

    """
    # swap / for \ in path
    path = path[:-1]
    path = path+r"\\" 

    sample_name = re.sub(path, '', file) # remove path
    sample_name = re.sub(re.escape('.CSV'), '',  # remove .csv
                         sample_name, flags=re.IGNORECASE)
    return sample_name

def make_data_dict(sample_names, path):
    """
    Create a dictionary of PSD data for each sample

    Parameters
    ----------
    sample_names : list of strings
        Samples to include.
    path : string
        Location of sample files.

    Returns
    -------
    data_dict : Dictionary
        Dictionary of PSD data for all samples.

    """
    data_dict = {}

    # Select only pore width, surface area, pore volume columns
    fields = ('w', 'dV/dw', 'V cum', 'dS/dw', 'S cum')
    for s in sample_names:
        # read in sample file
        sample_df = read_data(f"{path}{s}.CSV")
        # change column names to be more usable later
        sample_df.columns = sample_df.columns.str.replace('/', '')
        sample_df.columns = sample_df.columns.str.replace(' ', '')
        # add to data_dict
        data_dict[s] = sample_df   
    
    return data_dict

def data_collect(path):
    """
    Finds sample PSD files in path, and passes to :func:`make_data_dict`
    to create dictionary of PSDs.

    Parameters
    ----------
    path : string
        Location of sample files..

    Returns
    -------
    data_dict : string
        Dictionary of PSD data for all samples.

    """
    print(f"starting determination of parameters from {path}")
    all_files = os.listdir(path)
    files = []
    for a in all_files:
        if re.search(re.escape(".csv"), a, flags=re.IGNORECASE):
            files.append(a)

    sample_names = []
    for file in files:
        sample_name = get_sample_name(file, path)
        if sample_name not in sample_names:
            sample_names.append(sample_name)
    data_dict = make_data_dict(sample_names, path)
    print("...done")
    return data_dict

def find_parameter(sample_df, measure, 
                   wmin=0, wmax=500):
    """
    Finds a textural parameter (pore volume or surface area) for a sample 
    within some pore width region.

    Parameters
    ----------
    sample_df : DataFrame
        Contains PSD for a sample.
    measure : string
        Use 'V' for pore volume and 'S' for surface area.
    wmin : num, optional
        Minimum pore width. The default is 0.
    wmax : num, optional
        Maximum pore width. The default is 500.

    Returns
    -------
    parameter : num
        Quantity of pore volume or pore width within selected pore width region.

    """
    measure_column = str(f"{measure}cum") # find 'S' or 'V' column in dataframe
    # find pore width ('w') column in df
    w = sample_df['w']
    w_array = w.to_numpy()
    # check if column is empty
    empty_col = np.isnan(w_array[0])
    if empty_col == True:
        return None
    # otherwise find the parameter
    else:
        # find location of closest value to wmax
        rows_max = np.max(list(np.where(w<wmax)))
        if wmin <= 3: # prevents zero-sized array
            rows_min = 0
        else:
            # find location of closest value to wmin
            rows_min = np.max(list(np.where(w<wmin)))
        # find value of S or V at wmin and wmax
        max_value = sample_df.loc[rows_max, measure_column]
        min_value = sample_df.loc[rows_min, measure_column]
        # and return difference
        parameter = max_value - min_value
        return parameter
    
def parameter_df(data_dict, 
                 wstart=3, wstop=50, wstep=1,
                 logstep=False, num=None,
                 to_csv=False, csv_path=None):
    """
    Makes a dataframe of textural parameters from a set of sample PSDs, i.e.
    determines the pore volume or surface area within every possible interval 
    of pore widths, within boundaries set by wstart, wstop, wstep.

    Parameters
    ----------
    data_dict : Dictionary
        Dictionary of PSD data for all samples.
    wstart : num, optional
        lower bound of pore width, w. The default is 3.
    wstop : num, optional
        Upper bound of pore width, w. The default is 50.
    wstep : num, optional
        Minimum interval between pore widths. The default is 1.
    logstep : boolean, optional
        If true, uses a logarithmic interval. The default is False.
    num : num, optional
        Use with logstep, defines number of points between wstart and wstop.
        The default is None.
    to_csv : boolean, optional
        Generates a csv file of the parameter dataframe if true.
        The default is False.
    csv_path : string, optional
        Where to save csv file. The default is None.

    Returns
    -------
    param_df : Dataframe
        Dataframe of parameters (S or V) between all possible pore width 
        intervals.

    """
    print(f"""Creating parameter DataFrame for for pore width ranges from {wstart} to {wstop}, increment = {wstep} angstroms...""")
    param_cols = ['wmax', 'wmin']
    for d in data_dict:
        param_cols.append(f"param_{d}")
    param_df = pd.DataFrame(columns = param_cols)

    i = 0
    if logstep: # logstep part needs work. Only do linear for now.
        if num is None:
            print('''
                  if you set logstep as true, you must also specify
                  number of points (num) to calculate.
                  ''')
        else:
            base=10
            wstart = m.log(wstart, base)
            wstop = m.log(wstop, base)
            array = np.logspace(wstart, wstop, base=base, num=num)
 
    elif logstep is False: # use a linear step
        if wstep is None:
            print('No interval (wstep) entered for linear sequence.')
        else:
            array = np.arange(wstart, wstop, wstep) 

    # real size of array 
    n = len(array) + 1
    # total number of width ranges to be calculated
    t = (np.math.factorial(n) / np.math.factorial(n - 2)) / 2
    for wmax in array[1:]: 
        for wmin in np.arange(wstart, wmax, wstep):
            param_df.loc[i, 'wmax'] = wmax
            param_df.loc[i, 'wmin'] = wmin
            for d in data_dict: # finds parameters between wmin and wmax,
                param = find_parameter(data_dict[d], measure='V',
                                       wmin=wmin, wmax=wmax)
                param_df.loc[i, 'param_'+d] = param # appends to df
            print_progress_bar(i, t, '')
            i+=1 # Go through all possible values of wmin for wmax

    if to_csv: # saves results to csv if wanted.
        if csv_path is None:
            print('No path specified, can\'t save csv')
        else: 
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)
            param_df.to_csv(f"{csv_path}param_df.csv")
    print("...done") 
    return param_df


def make_report(project, sorptives, wstart, wstop, wstep, parameter):
    """
    Generates a report file for the current analysis.

    Parameters
    ----------

    Returns
    -------
    """
    if parameter == 'S':
        parameter_name = 'surface area' 
    elif parameter == 'V':
        parameter_name = 'pore volume'

    path = make_path('source', project, sorptives, 'psd')
    angstrom = u'\u212B'
    header = f"""
                Parameter DataFrame generated at {now_1.strftime('%H:%M')} on {now_1.strftime('%y-%m-%d')} 
                ------------------------------------------------
                """
    body = f"""
                Project name = {project}, Sorptives = {sorptives},
                Number of PSDs = {len(os.listdir(path))}, calculated for {parameter_name}.
                Using pore widths between {wstart} and {wstop} {angstrom} with a minimum increment
                of {wstep} {angstrom}
                """
    report = f"{header}{body}"
    return report

def process_psd(project, sorptives, parameter, now,
                wstart=3, wstop=20, wstep=1):
    path = make_path('source', project, sorptives, 'psd')
    data_dict = data_collect(path)
    param_df = parameter_df(data_dict,
                            wstart=wstart,
                            wstop=wstop, wstep=wstep)
    results_path = f"{make_path('result', project, sorptives, 'psd')}/{now}/"
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    param_df.to_csv(f"{results_path}param_df.csv")

    report = make_report(project,
                         sorptives,
                         wstart, wstop,
                         wstep,
                         parameter) 
    report_txt = open(f"{results_path}psd_report.txt", 'w')
    report_txt.write(report)
    report_txt.close()
    print(f"Parameter dataframe and report saved in {results_path}")
    return param_df, data_dict

def main(project, sorptives, wstart=3, wstop=20, wstep=1):
    path = make_path('source', project, sorptives, 'psd')
    data_dict = data_collect(path)

    param_df = parameter_df(data_dict,
                            wstart=wstart, wstop=wstop, wstep=wstep)

    results_path = make_path('result', project, sorptives, 'psd')
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    param_df.to_csv(f"{results_path}param_df.csv")

    Report = report(project, sorptives, wstart, wstop, wstep, 'V')
    report_txt = open(f"{results_path}psd_report.txt", 'w')
    report_txt.write(Report)
    report_txt.close()
    print(f"Parameter dataframe and report saved in {esults_path}")
    return param_df, data_dict

if __name__ == '__main__':
    # for testing
    project = '0010_dualiso_co2'
    sorptives = 'n2h2'
    param_df, data_dict = main(project, sorptives)

