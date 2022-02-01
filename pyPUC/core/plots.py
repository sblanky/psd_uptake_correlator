import matplotlib.pyplot as plt
"""
Some default plotting tools.
"""
def bwap(bwap, results_path):
    f, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=96)
    ax.plot(bwap.p, bwap.wmin,
            color='b', label='min')
    ax.plot(bwap.p, bwap.wmax,
            color='b', label='max')  
    ax.set_xlabel('Pressure / bar')
    ax.set_ylabel('Pore width / $\AA$')
    f.savefig(f"{results_path}optimum_pore_size.png", dpi=200)
    plt.close(f)

def correlations(df, results_path):
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
        ax.annotate(f"$r^2$ = {format(df.loc[index, 'r_sq'], '.2f')}", 
                    xy=(0.05, 0.95), xycoords='axes fraction')
        path = f"{results_path}/plots/correlations/{df.loc[index, 'p']}/"
        if not os.path.exists(path):
            os.makedirs(path)
        name = f"{df.loc[index, 'wmin']}_{df.loc[index, 'wmax']}.png"
        f.savefig(f"{path}{name}")
        plt.close(f)
