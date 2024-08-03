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

class CurveVisualizer:
    def __init__(self, data_path):
        with open(os.path.join(data_path, "draw_I.pkl"), 'rb') as fh:
            self.dict_curves = pickle.load(fh)
        for rho,prevalence in self.dict_curves.items():
            self.dict_curves[rho] = prevalence[:101]
        del self.dict_curves['0.99']

        self.arr_rho = np.load(os.path.join(data_path, "simplify_ratio.npy"))
        self.arr_auc = np.load(os.path.join(data_path, "delta_auc.npy"))

    def plot_curves(self):
        fig_height,fig_width = 10, 6
        fig,ax = plt.subplots(figsize=(fig_height,fig_width))
        cmap = plt.cm.get_cmap('GnBu')

        # 1. ----------------- 绘制主图完整曲线 -----------------
        # for rho,prevalence in np.array(list(self.dict_curves.items()))[::-1]:
        for rho,prevalence in self.dict_curves.items():
            prevalence = 100*prevalence/pop_size
            color = cmap(0.3+0.7*(1-float(rho)))
            ax.plot(prevalence, lw=1.5, color=color, label="ρ=%s"%(rho), alpha=0.5, zorder=10)

        peaks = [max(curve) for curve in self.dict_curves.values()]
        print ((max(peaks)-min(peaks))/pop_size)
        print (max(peaks)-min(peaks))

        sizes = [sum(curve) for curve in self.dict_curves.values()]
        print ((max(sizes)-min(sizes))/pop_size)
        print (max(sizes)-min(sizes))
        exit()


        ax.set_xlim(0,100)
        ax.set_ylim(0,50)
        ax.legend(ncols=2, loc='lower right', fontsize='small', borderpad=1, markerscale=0.8, labelspacing=0.1, handletextpad=0.5, handlelength=1, columnspacing=0.8)

        # 2. ----------------- 计算局部放大范围 -----------------
        peak_min = np.min([np.max(100*prevalence/pop_size) for prevalence in self.dict_curves.values()])
        peak_max = np.max([np.max(100*prevalence/pop_size) for prevalence in self.dict_curves.values()])
        y_margin = (peak_max-peak_min)*1.0
        ymin,ymax = peak_min-y_margin,peak_max+y_margin

        x_centre = np.median([np.argmax(100*prevalence/pop_size) for prevalence in self.dict_curves.values()])
        x_margin = (ymax-ymin)*fig_width/fig_height
        xmin,xmax = x_centre-x_margin,x_centre+x_margin

        ax.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin], "red")
        ax.set_xlabel("Simulation Day")
        ax.set_ylabel("Overall Prevalence (%)")
        ax.grid(ls='-.', lw=0.4, color='lightgray', zorder=10)

        # 3. ----------------- 绘制子图放大区域 -----------------
        ax_inset = inset_axes(ax, width="30%", height="30%", loc='upper right', 
                bbox_to_anchor=(0, -0.05, 1, 1), bbox_transform=ax.transAxes)

        for rho,prevalence in self.dict_curves.items():
            prevalence = 100*prevalence/pop_size
            color = cmap(0.3+0.7*(1-float(rho)))
            ax_inset.plot(prevalence, lw=2.5, alpha=0.8, color=color)

        formatter = ScalarFormatter(useOffset=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-2, 2))
        ax_inset.yaxis.set_major_formatter(formatter)

        ax_inset.set_xlim(xmin, xmax)
        ax_inset.set_ylim(ymin, ymax)
        ax_inset.set_xticklabels('')
        ax_inset.set_yticklabels('')

        ax_inset.tick_params(axis='x', labelsize='small')
        ax_inset.tick_params(axis='y', labelsize='small')
        ax_inset.xaxis.get_offset_text().set_fontsize('small')
        ax_inset.yaxis.get_offset_text().set_fontsize('small')

        # 4. ----------------- 绘制主图子图连接 -----------------
        xy1 = (xmax, ymin)
        xy2 = (0, 0)
        con = ConnectionPatch(xyA=xy2, xyB=xy1, coordsA="axes fraction", coordsB="data",
                              axesA=ax_inset, axesB=ax, lw=0.8, color="gray", ls='-.')
        ax_inset.add_artist(con)

        xy1 = (xmax, ymax)
        xy2 = (0, 1)
        con = ConnectionPatch(xyA=xy2, xyB=xy1, coordsA="axes fraction", coordsB="data",
                              axesA=ax_inset, axesB=ax, lw=0.8, color="gray", ls='-.')
        ax_inset.add_artist(con)

        ax_inset.grid(ls='-.', lw=0.3, color='lightgray', zorder=10)
        # plt.show()
        # exit()

        plt.savefig('./Output/Figure/OverallError/overall_prevalence.png', dpi=600)

    def plot_curves_cumu(self):
        fig_height,fig_width = 10, 6
        fig,ax = plt.subplots(figsize=(fig_height,fig_width))
        cmap = plt.cm.get_cmap('GnBu')

        adj = 7.5

        # 1. ----------------- 绘制主图完整曲线 -----------------
        for rho,prevalence in self.dict_curves.items():
            prevalence = (100*prevalence/pop_size).cumsum()/adj
            color = cmap(0.3+0.7*(1-float(rho)))
            ax.plot(prevalence, lw=1.5, color=color, label="ρ=%s"%(rho), alpha=0.5, zorder=10)

        ax.set_xlim(0,100)
        ax.set_ylim(0,100)
        ax.legend(ncols=2, loc='lower right', fontsize='small', borderpad=1, markerscale=0.8, labelspacing=0.1, handletextpad=0.5, handlelength=1, columnspacing=0.8)

        # 2. ----------------- 计算局部放大范围 -----------------
        peak_min = np.min([np.sum(100*prevalence/pop_size)/adj for prevalence in self.dict_curves.values()])
        peak_max = np.max([np.sum(100*prevalence/pop_size)/adj for prevalence in self.dict_curves.values()])

        y_margin = (peak_max-peak_min)*1.0
        ymin,ymax = peak_min-y_margin,peak_max+y_margin

        x_margin = (ymax-ymin)*fig_width/fig_height
        xmin,xmax = 100-x_margin,100

        ax.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin], "red")
        ax.set_xlabel("Simulation Day")
        ax.set_ylabel("Overall Cumulative Infection Rate (%)")
        ax.grid(ls='-.', lw=0.4, color='lightgray', zorder=10)

        # 3. ----------------- 绘制子图放大区域 -----------------
        ax_inset = inset_axes(ax, width="30%", height="30%", loc='center right',
                bbox_to_anchor=(0, +0.1, 1, 1), bbox_transform=ax.transAxes)

        for rho,prevalence in self.dict_curves.items():
            prevalence = (100*prevalence/pop_size).cumsum()/adj
            color = cmap(0.3+0.7*(1-float(rho)))
            ax_inset.plot(prevalence, lw=2.5, alpha=0.8, color=color)

        ax_inset.set_xlim(xmin, xmax)
        ax_inset.set_ylim(ymin, ymax)
        ax_inset.set_xticklabels('')
        ax_inset.set_yticklabels('')

        ax_inset.tick_params(axis='x', labelsize='small')
        ax_inset.tick_params(axis='y', labelsize='small')
        ax_inset.xaxis.get_offset_text().set_fontsize('small')
        ax_inset.yaxis.get_offset_text().set_fontsize('small')

        # 4. ----------------- 绘制主图子图连接 -----------------
        xy1 = (xmin, ymin)
        xy2 = (0, 1)
        con = ConnectionPatch(xyA=xy2, xyB=xy1, coordsA="axes fraction", coordsB="data",
                              axesA=ax_inset, axesB=ax, lw=0.8, color="gray", ls='-.')
        ax_inset.add_artist(con)

        xy1 = (xmax, ymin)
        xy2 = (1, 1)
        con = ConnectionPatch(xyA=xy2, xyB=xy1, coordsA="axes fraction", coordsB="data",
                              axesA=ax_inset, axesB=ax, lw=0.8, color="gray", ls='-.')
        ax_inset.add_artist(con)
        ax_inset.grid(ls='-.', lw=0.3, color='lightgray', zorder=10)

        plt.savefig('./Output/Figure/OverallError/overall_cumulative.png', dpi=600)


    def plot_dauc(self):
        fig_height,fig_width = 8, 6
        fig,ax = plt.subplots(figsize=(fig_height,fig_width))

        ax.scatter(self.arr_rho, self.arr_auc, color='tab:blue', marker='.', zorder=11)
        ax.set_yscale('log')

        ax.set_xlim(0, 1)

        ax.set_xlabel('Simplification Rate ρ')
        # ax.set_ylabel('Simulation Error $\\Delta \\epsilon$')
        ax.set_ylabel(r'Simulation Error $\Delta \epsilon$')
        ax.tick_params(axis='both', labelsize=14)

        ax.grid(ls='-.', lw=0.4, color='lightgray', zorder=10)
        plt.savefig('./Output/Figure/OverallError/overall_dauc.png', dpi=600)
        # plt.show()


    def run(self):
        self.plot_curves()
        self.plot_curves_cumu()
        self.plot_dauc()



if __name__ == '__main__':
    data_path = r"./Data/Results/Plot data/fig2"

    visualizer = CurveVisualizer(data_path)
    visualizer.run()



 


    exit()



