import os

def make_path(project, sorptives, application):
    """
    Finds the path to your source data. Used in psd_processing and uptake_processing.
    Source data should be located in ./source_data/project/application/sorptive(s)
    Will throw ValueError if project or sorptives not found, or if application
    is not either uptake or psd.

    Parameters
    ----------
    project : string
        Name of your project, usually in the form ####_*, i.e. four numbers and then some alphanumeric description.
    sorptives : string
        The name of the sorptive(s) you want to use the data from. 
    application : string
        Either uptake or psd.
    Returns
    -------
    path : string
        path to your source data.
	"""
    applications = ['uptake', 'psd']
    if application not in applications:
        raise ValueError(f"Application variable must be either \'uptake\' or \'psd\'. You have input {application}.")

    if project not in os.listdir("./source_data/"):
        raise ValueError(f"{project} is an invalid project, please check project file exists in source_data")
        

    if sorptives not in os.listdir(f"./source_data/{project}/{application}/"):
        raise ValueError(f"{sorptives} could not be found. Check that the directory {sorptives} exists in the {application} folder in {project}.")
    
    return f"source_data/{project}/{application}/{sorptives}/"
