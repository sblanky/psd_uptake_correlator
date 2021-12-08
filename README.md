A package to determine the optimum pore size for gas uptake at different 
pressures in carbons. Heavily relies on [pyGAPS](https://github.com/pauliacomi/pyGAPS).

Steps to use:
 1. install new conda environment;
    `conda create -n <env> python=3.8 numpy nomkl scipy pandas xlwt xlrd requests matplotlib`
 2. Activate environment
 3. Use pip to install the dev build of pyGAPS. `pip install git+https://github.com/pauliacomi/pyGAPS@develop`

This is to avoid the problem found [here](https://stackoverflow.com/questions/70248438/module-breaks-when-loaded-into-multiple-scripts).
Thanks to @pauliacomi for help with the above.
