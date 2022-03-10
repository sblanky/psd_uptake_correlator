import core.utils as utils
import core.plots as plots
import pandas as pd

bwap_dict = {}
source_dir = utils.make_path('result', '0061_all')
bwap_S = pd.read_csv(f"{source_dir}S/twap/0.csv")
bwap_V = pd.read_csv(f"{source_dir}2202101349/twap/0.csv")

bwap_dict['bwap_V'] = bwap_V
bwap_dict['bwap_S'] = bwap_S

results_path = f"{source_dir}bwap_grid_test/"
plots.bwap_grid(bwap_dict, results_path,
                ylim=[[3.6, 30],
                      [3.6, 100]],
                name="bwap_grid_test")
