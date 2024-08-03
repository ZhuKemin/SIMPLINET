import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap, LogNorm, Normalize
import os
from datetime import datetime
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pickle

# 设置全局字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 16,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class EpidemicPlotter:
    def __init__(self, results_path, shapefile_path, boundary_path):
        self.results_path = results_path
        self.shapefile_path = shapefile_path
        self.boundary_path = boundary_path
        self.results, self.metadata = self.load_results()
        self.grid_raw = self.load_shapefile()
        self.boundary = self.load_boundary()
        self.grid = self.grid_raw.loc[self.grid_raw['population'] > 0]  # 只保留有人的区域
        self.max_population_idx = self.grid['population'].idxmax()  # 找到人口最多的网格索引

        prevalence = self.results['I']/self.metadata['population']
        # plt.plot(prevalence)
        # plt.show()

        # print (prevalence.shape)

        # I_range = [max(row)-min(row) for row in prevalence]
        # print (np.max(I_range))
        # print (np.argmax(I_range))

        # print (min(prevalence[37]))
        # print (max(prevalence[37]))


        # peakdays = np.argmax(prevalence, axis=0)

        # print (max(peakdays))
        # print (min(peakdays))


        # exit()

        
    def load_results(self):
        with open(self.results_path, 'rb') as f:
            data = pickle.load(f)
        return data['results'], data['metadata']
    
    def load_shapefile(self):
        return gpd.read_file(self.shapefile_path)
    
    def load_boundary(self):
        return gpd.read_file(self.boundary_path)
    
    def calculate_normalized_rank(self, day):
        # 计算特定天数的流行率
        prevalence = self.results['I'][day] / self.metadata['population']
        
        # 计算排名（按降序）
        ranks = prevalence.argsort()[::-1].argsort()
        
        # 计算归一化排名值
        normalized_rank = 1 - (ranks + 1) / len(ranks)
        return normalized_rank
    
    def plot_normalized_rank(self, days, output_dir='./Output/Figure/NormalizedRank'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for day in days:
            normalized_rank = self.calculate_normalized_rank(day)
            self.grid['normalized_rank'] = normalized_rank

            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)
            plt.title(f'Simulation Day {day}', fontsize=22, pad=10)

            # 绘制社区背景和外轮廓
            self.boundary.plot(ax=ax, facecolor='white', edgecolor='black', lw=1.5, zorder=11)
            gdf_unpopulated = self.grid_raw.loc[self.grid_raw['population'] == 0].dissolve()
            gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.1, zorder=12)
            self.grid.plot(ax=ax, column='normalized_rank', cmap='RdYlBu_r', edgecolor='black', linewidth=0.5,
                           legend=False, alpha=0.6, zorder=13)

            # 绘制人口最多的网格红框
            max_pop_area = self.grid.loc[self.max_population_idx]
            if max_pop_area.geometry.type == 'Polygon':
                x, y = max_pop_area.geometry.exterior.xy
                ax.plot(x, y, color='tab:red', linewidth=1.5, zorder=14)
            else:
                for polygon in max_pop_area.geometry:
                    x, y = polygon.exterior.xy
                    ax.plot(x, y, color='tab:red', linewidth=1.5, zorder=14)

            """
            # 添加比例尺
            x_min, x_max, y_min, y_max = ax.axis()
            x_offset = 0.40
            y_offset = 0.10
            scale_len_label = 20
            rect_height_label = 2

            scale_len = scale_len_label / 103
            rect_height = rect_height_label / 111

            scale_x_min = x_min + (x_max - x_min) * x_offset
            scale_x_max = scale_x_min + scale_len
            scale_y_min = y_min + (y_max - y_min) * y_offset
            scale_y_max = scale_y_min + rect_height

            ax.add_patch(patches.Rectangle((scale_x_min, scale_y_min), scale_len, rect_height, fill=True, color='black', alpha=1.0, lw=0))
            ax.add_patch(patches.Rectangle((scale_x_min + scale_len / 2, scale_y_min), scale_len / 2, rect_height, fill=True, color='white', alpha=1.0, lw=0))
            ax.add_patch(patches.Rectangle((scale_x_min, scale_y_min), scale_len, rect_height, fill=False, color='black', alpha=1.0, lw=1.5))

            ax.text(scale_x_min, scale_y_max + rect_height / 4, '0', ha='center', va='bottom', fontsize=14)
            ax.text(scale_x_min + scale_len / 2, scale_y_max + rect_height / 4, f'{int(scale_len_label / 2)}', ha='center', va='bottom', fontsize=14)
            ax.text(scale_x_max, scale_y_max + rect_height / 4, f'{int(scale_len_label)}', ha='center', va='bottom', fontsize=14)
            ax.text(scale_x_max + scale_len / 7, scale_y_max + rect_height / 4, 'km', ha='center', va='bottom', fontsize=14, fontstyle='italic')
            """

            # 设置图的样式和网格线
            ax.grid(ls='-.', lw=0.5, color='gray', zorder=10)
            ax.set_aspect('equal')
            ax.set_axisbelow(True)

            """
            # 添加颜色条
            norm = Normalize(vmin=0, vmax=1)
            sm = plt.cm.ScalarMappable(cmap='RdYlBu_r', norm=norm)
            sm.set_array([])

            cax = inset_axes(ax, width="20%", height="2%", loc='upper right',
                             bbox_to_anchor=(-0.05, -0.15, 1, 1), bbox_transform=ax.transAxes, borderpad=0)

            cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')
            cbar.set_label('Normalized Rank', fontsize=16)
            cbar.set_ticks([0, 1])  # 设置刻度仅为0和1
            cbar.ax.tick_params(labeltop=True, labelbottom=False, top=True, bottom=False, pad=0)
            """

            # 保存图像
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"normalized_rank_day_{day}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=600)
            plt.close(fig)
            print(f"Saved figure to {filepath}")


if __name__ == '__main__':
    results_path = './Output/epidemic_model_results.pkl'
    shapefile_path = './GISData/Grid-Pop-1km-WGS84.shp'
    boundary_path = './GISData/Boundary.shp'
    plotter = EpidemicPlotter(results_path, shapefile_path, boundary_path)
    plotter.plot_normalized_rank([20, 30, 40, 50])
    # plotter.plot_normalized_rank([20, 25, 30, 35, 40, 45, 50])
    # plotter.plot_normalized_rank([35,36,37,38,39,40])
