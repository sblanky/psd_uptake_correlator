"""
For generating some strings for other modules. Currently only makes
paths to source data. Will add more functionality later.
"""

import os
from pathlib import Path
import pandas as pd

def make_path(source_result, project, sorptives=None, application=None):
    """
    Finds the path to your source data, or makes path to in which to save
    results. Used in psd_processing and uptake_processing. Will implement in
    best_width_at_pressure at a later stage.
    Source data should be located in ./source_data/project/application/sorptive(s)
    Will throw ValueError if project or sorptives not found, or if application
    is not either uptake or psd.

    Parameters
    ----------
    source_result : string
        Whether taking source data or generating results. Must be 'source' or
        'result' otherwise ValueError thrown.
    project : string
        Name of your project, usually in the form ####_*, i.e. four numbers and then some alphanumeric description.
    sorptives : string
        The name of the sorptive(s) you want to use the data from. 
    application : string
        Either uptake or psd (if source_result=source), or don't use (=None).
        Default is None.
                d = pd.DataFrame(d)
    Returns
    -------
    path : string
        path to your source data.
	"""
    if source_result not in ['source', 'result']: 
        raise ValueError("Variable source_result must be either source or result")

    elif source_result == 'result':
        if project is None:
            raise ValueError("Must have project name to generate results directory")
        else:
            return f"../../results/{project}/"
    
    elif source_result == 'source':
        if application not in ['uptake', 'psd']:
            raise ValueError(f"Application variable must be either \'uptake\' or \'psd\'. You have input {application}.")

        if project not in os.listdir("./source_data/"):
            raise ValueError(f"{project} is an invalid project, please check project file exists in source_data")

        if sorptives not in os.listdir(f"./source_data/{project}/{application}/"):
            raise ValueError(f"{sorptives} could not be found. Check that the directory {sorptives} exists in the {application} folder in {project}.")
        
        return f"../../source_data/{project}/{application}/{sorptives}/"

def read_data(path):
    file_path = Path(f"{path}")
    file_extension = file_path.suffix.lower()[1:]
    if file_extension == 'xlsx':
        return pd.read_excel(file_path, engine='openpyxl')
    elif file_extension == 'xls':
        return pd.read_excel(file_path)
    elif file_extension == 'csv':
        return pd.read_csv(file_path)
    else:
        raise Exception("File not supported")

