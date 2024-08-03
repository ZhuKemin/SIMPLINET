import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import random
import os
from datetime import datetime
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.patches as patches
from shapely.geometry import box


# 设置字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 16,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class FullNetworkFlowVisualizer:
    def __init__(self, shapefile_path, boundary_path, flow_matrix_path, population_path):
        # 读取GIS数据
        self.gdf_raw = gpd.read_file(shapefile_path)
        self.gdf = self.gdf_raw.loc[self.gdf_raw.population > 0]
        self.gdf_boundary = gpd.read_file(boundary_path)
        self.gdf = self.gdf.set_index('TID')

        # 加载人口流动数据
        self.flow_matrix = np.load(flow_matrix_path)
        self.population = np.load(population_path)

        # 检查GIS数据和人口流动数据的一致性
        assert self.flow_matrix.shape[0] == self.flow_matrix.shape[1] == len(self.population) == len(self.gdf), \
            "The number of grid cells and flow matrix must match."

        self.flow_matrix = (self.flow_matrix.T*self.population).T.astype(int)


    def plot_full_network_flow(self, min_flow_plot=1, max_flow_plot=4000, n_lines=2000000, cmap='RdYlBu_r', output_dir='./Output/Figure/FullNetworkFlow'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)

        # 获取社区的中心点
        self.gdf['lon'] = self.gdf.geometry.centroid.x
        self.gdf['lat'] = self.gdf.geometry.centroid.y

        # 以较浅的颜色绘制社区背景
        self.gdf_boundary.plot(ax=ax, facecolor='white', edgecolor='black', lw=1.5, zorder=11)
        gdf_unpopulated = self.gdf_raw.loc[self.gdf_raw.population == 0].dissolve()
        gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.1, zorder=12)
        self.gdf.plot(ax=ax, color='none', edgecolor='lightgray', alpha=0.1, zorder=13)

        # 绘制跨区域的人口流动
        rows, cols = np.indices(self.flow_matrix.shape)
        flattened_matrix = np.column_stack((rows.ravel(), cols.ravel(), self.flow_matrix.ravel()))

        random_indices  = np.random.choice(flattened_matrix.shape[0], n_lines, replace=False)
        flattened_matrix = flattened_matrix[random_indices ]

        sorted_matrix = flattened_matrix[flattened_matrix[:, 2].argsort()[::-1]]  # 按降序排序
        sorted_matrix = sorted_matrix[sorted_matrix[:, 0] != sorted_matrix[:, 1]]
        sorted_matrix = sorted_matrix[sorted_matrix[:, 2] > min_flow_plot]

        if len(sorted_matrix) > n_lines:
            sorted_matrix = sorted_matrix[:n_lines]

        cmap = plt.cm.get_cmap(cmap)
        norm = mcolors.LogNorm(vmin=min_flow_plot, vmax=max_flow_plot)

        for orig, dest, flow in sorted_matrix[::-1]:  # 逆序绘制
            orig_x, orig_y = self.gdf.loc[orig, 'lon'], self.gdf.loc[orig, 'lat']
            dest_x, dest_y = self.gdf.loc[dest, 'lon'], self.gdf.loc[dest, 'lat']
            linewidth = min(0.02 + flow / max_flow_plot * 2.0, 2.0)
            color = cmap(norm(flow))
            ax.plot([orig_x, dest_x], [orig_y, dest_y], color=color, lw=linewidth, alpha=0.5, zorder=15)

        # 添加色彩条标签
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        cax = inset_axes(ax, width="20%", height="2%", loc='upper right',
                         bbox_to_anchor=(-0.05, -0.15, 1, 1), bbox_transform=ax.transAxes, borderpad=0)

        # 添加 colorbar
        cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')

        # cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.02, pad=0.04)
        cbar.set_label('Flow Volume', fontsize=16)
        # cbar.set_ticks([1,10,100,1000,10000])
        # cbar.set_ticklabels([r'$10^0$', r'$10^1$', r'$10^2$', r'$10^3$', r'$10^4$'], fontsize=14)
        cbar.set_ticks([1,10,100,1000])
        cbar.set_ticklabels([r'$10^0$', r'$10^1$', r'$10^2$', r'$10^3$'], fontsize=14)
        cbar.ax.tick_params(labeltop=True, labelbottom=False, top=True, bottom=False, pad=0)

        # 获取图的范围
        x_min, x_max, y_min, y_max = ax.axis()

        # 设置比例尺参数
        x_offset = 0.40  # 距离左侧的相对距离
        y_offset = 0.10  # 距离底部的相对距离
        scale_len_label = 20  # 比例尺的标签长度（以地图单位为准）
        rect_height_label = 2  # 比例尺的高度

        scale_len = scale_len_label/103
        rect_height = rect_height_label/111


        # 计算比例尺的位置
        scale_x_min = x_min + (x_max - x_min) * x_offset
        scale_x_max = scale_x_min + scale_len
        scale_y_min = y_min + (y_max - y_min) * y_offset
        scale_y_max = scale_y_min + rect_height

        # 绘制比例尺
        ax.add_patch(patches.Rectangle((scale_x_min, scale_y_min), scale_len, rect_height, fill=True, color='black', alpha=1.0, lw=0))
        ax.add_patch(patches.Rectangle((scale_x_min + scale_len/2, scale_y_min), scale_len/2, rect_height, fill=True, color='white', alpha=1.0, lw=0))
        ax.add_patch(patches.Rectangle((scale_x_min, scale_y_min), scale_len, rect_height, fill=False, color='black', alpha=1.0, lw=1.5))

        # 添加比例尺文本
        ax.text(scale_x_min               , scale_y_max + rect_height/4 , '0'                         , ha='center', va='bottom', fontsize=14)
        ax.text(scale_x_min + scale_len/2 , scale_y_max + rect_height/4 , f'{int(scale_len_label/2)}' , ha='center', va='bottom', fontsize=14)
        ax.text(scale_x_max               , scale_y_max + rect_height/4 , f'{int(scale_len_label)}'   , ha='center', va='bottom', fontsize=14)
        ax.text(scale_x_max + scale_len/7 , scale_y_max + rect_height/4, 'km'                         , ha='center', va='bottom', fontsize=14, fontstyle='italic')

        # 添加网格线
        ax.grid(ls='-.', lw=0.5, color='gray', zorder=10)
        ax.set_aspect('equal')
        ax.set_axisbelow(True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"full_network_flow_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        # 保存图像
        plt.savefig(filepath, dpi=600)
        plt.close(fig)
        print(f"Saved figure to {filepath}")

if __name__ == '__main__':
    shapefile_path = "./GISData/Grid-Pop-1km-WGS84.shp"
    boundary_path = "./GISData/Boundary.shp"
    flow_matrix_path = "./Data/flow.npy"
    population_path = "./Data/population.npy"

    visualizer = FullNetworkFlowVisualizer(shapefile_path, boundary_path, flow_matrix_path, population_path)
    visualizer.plot_full_network_flow()
