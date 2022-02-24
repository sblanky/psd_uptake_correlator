pyPUC (Python Porosity Uptake Correlator) is an attempt to calculate the optimum pore size range of some type of material for gas uptake at pressures in a range. It is a work in progress but now has some limited CLI functionality. Any serious calculations will likely require use of an HPC. 
The code is... messy. But it works!

How it works
============
pyPUC requires a set of experimentally derived pore size distributions (PSDs), with experimental gravimetric uptake isotherms for some sporptive (e.g. CO<sub>2</sub>, CH<sub>4</sub>) from the same set of materials. This proceeds via a 'brute force' process, i.e.
  1. Model isotherms are generated from the uptake isotherms using [pyGAPS](https://github.com/pauliacomi/pyGAPS). Loadings for each sample are determined for a set of (user-defined) pressures to generate a loading dataframe (`loading_df`) for all samples.
  2. Porosity parameters are calculated from PSDs within a set of pore size regions defined by a minimum and maximum pore widths (`wmin` and `wmax`), as well as a minimum increment (`wstep`). For example, for `wmin=3`, `wmax=6`, and `wstep=1`, the pore size ranges calculated are 3-4, 3-5, 3-6, 4-5, 4-6. Calculations may be performed via surface area or pore volume PSDs. This forms a set of parameters at each pore range for all samples (`param_df`).
  3. Linear regressions are performed between each row of `param_df` and `loading_df`. 
  4. The highest pearson coefficient, r<sup>2</sup> is selected for each pressure, thus yielding the optimum pore size region for each pressure.

In addition there are a number of useful plotting tools in core.plots

Steps to use
============
 1. Clone this repo
 2. Install new conda environment;
    `conda create -n <env> python=3.8 numpy nomkl scipy pandas xlwt xlrd requests matplotlib`[^1]
 2. Activate environment inside your cloned repo.
 3. Use pip to install the dev build of pyGAPS. `pip install git+https://github.com/pauliacomi/pyGAPS@develop`[^2]
 4. If you want to use the CLI, simply type `./pyPUC-cli` and press enter. 
 5. Large calculations (any calculations worth doing!) will probably require an HPC, however calculation time can be significantly reduced by making arrays in logspace. Example sbatch script can be found in `./pyPUC/`. Modify to your requirements. Run from root with `sbatch ./pyPUC/sbatch.sh`. 

[^1]: python 3.8 is required due to compatibility issues with the coolprop backend in pyGAPS.
[^2]: This is to avoid the problem found [here](https://stackoverflow.com/questions/70248438/module-breaks-when-loaded-into-multiple-scripts). Thanks to [@pauliacomi](https://github.com/pauliacomi) for help with the above.
