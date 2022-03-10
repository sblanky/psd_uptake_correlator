import core.plots as plots
import core.utils as utils
import pandas as pd

root = utils.get_project_root()
project = '0061_all'
source_path = f"{root}/results/{project}/"

df_V = pd.read_csv(f"{source_path}2202101349/twap/0.csv")
df_S = pd.read_csv(f"{source_path}S/twap/0.csv")

data_dict = {}
def smaller_df(df,
               pressures=['0.10', '1.0', '10', '40']):
    for index, row in df.iterrows():
        df.loc[index, 'p'] = utils.format_num(df.loc[index, 'p'])

    df = df[df['p'].isin(pressures)]
    df = df.reset_index(drop=True)
    return df

data_dict['V'] = smaller_df(df_V)
data_dict['S'] = smaller_df(df_S)

results_path = f"{utils.make_path('result', '0061_all')}plots/"
name = "correlations_VS"
plots.correlations_VS(data_dict,
                      results_path, name,
                      convert_string=True)

