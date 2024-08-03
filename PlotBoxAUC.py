from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import ConnectionPatch
from matplotlib.ticker import ScalarFormatter

import matplotlib.pyplot as plt
import numpy as np

import pickle
import os


config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 18,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)


import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings('ignore', category=ShapelyDeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

pop_size = 16236023   # 深圳总人口

class ErrorVisualizer:
    def __init__(self, data_path):
        with open(os.path.join(data_path, "data.pkl"), 'rb') as fh:
            self.list_arr_auc = pickle.load(fh)
        # self.list_arr_auc = [np.array([auc for auc in arr_auc if auc<1]) for arr_auc in self.list_arr_auc]

        with open(os.path.join(data_path, "positions.pkl"), 'rb') as fh:
            self.list_rho = pickle.load(fh)

    def plot_error_box(self):
        fig,ax = plt.subplots(figsize=(20,5))

        widths=0.8/len(self.list_rho)
        flierprops = dict(marker='o', markersize=3)
        ax.boxplot(x=self.list_arr_auc, positions=self.list_rho, widths=widths, flierprops=flierprops, zorder=10)
        ax.set_yscale('log')

        ticks = np.arange(0, 1.01, 0.1)
        ax.set_xticks(ticks)
        ax.set_xticklabels(['%0.2f'%(x) for x in ticks])

        ax.set_xlim(-0.01, 1.000001)
        ax.set_ylim(10e-9, 10)
        ax.set_xlabel('Simplification Rate ρ')
        # ax.set_xlabel('ρ')
        ax.set_ylabel(r'Simulation Error $\Delta \epsilon$')
        ax.grid(ls='-.', lw=0.4, color='gray', zorder=10)

        plt.tight_layout()
        plt.savefig('./Output/Figure/SpatialError/boxplot_dauc.png', dpi=600)
        # plt.show()


    def run(self):
        self.plot_error_box()



if __name__ == '__main__':
    data_path = r"./Data/Results/Plot data/fig4"

    visualizer = ErrorVisualizer(data_path)
    visualizer.run()



 


    exit()



