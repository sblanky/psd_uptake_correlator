A package to determine the optimum pore size for gas uptake at different 
pressures in carbons. Heavily relies on pyGAPS.

Best to run in a conda virtual environement. pyGAPS relies on Coolprop, but the wheels are not up to date with python 3.9. Thus, it's best to make the environment by;
`conda create -n <env> python=3.8 numpy nomkl scipy pandas xlwt xlrd requests matplotlib`
