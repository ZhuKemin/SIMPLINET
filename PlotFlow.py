import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import random
import os
from datetime import datetime

# 设置字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 26,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class FlowVisualizer:
    def __init__(self, shapefile_path, boundary_path, clustering_results_path, flow_matrix_path, population_path):
        # 读取GIS数据
        self.gdf_raw = gpd.read_file(shapefile_path)
        self.gdf = self.gdf_raw.loc[self.gdf_raw.population > 0]
        self.gdf_boundary = gpd.read_file(boundary_path)

        # 加载保存的聚类结果
        data = np.load(clustering_results_path)
        self.labels_per_step = data['cluster_labels']

        # 加载人口流动数据
        self.flow_matrix = np.load(flow_matrix_path)
        self.population = np.load(population_path)

        # 检查GIS数据和聚类数据的一致性
        assert len(self.gdf) == self.labels_per_step.shape[1], "The number of grid cells and clustering labels must match."
        assert self.flow_matrix.shape[0] == self.flow_matrix.shape[1] == len(self.population), "Flow matrix and population data must be consistent."

    def plot_flow(self, simplification_rates, cmap='tab20', output_dir='./Output/Figure/Flow'):
        colors = plt.cm.get_cmap(cmap)
        num_steps = self.labels_per_step.shape[0]
        selected_steps = [int(rate * num_steps) for rate in simplification_rates]

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for step_idx, step in enumerate(selected_steps):
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)

            # 获取当前步骤的聚类标签
            labels = self.labels_per_step[step]
            self.gdf['community_label'] = labels

            # 计算实际跨区域出行人数矩阵
            num_communities = len(np.unique(labels))
            flow_between_communities = np.zeros((num_communities, num_communities))

            for i in range(len(self.population)):
                for j in range(len(self.population)):
                    if i != j:
                        comm_i = labels[i]
                        comm_j = labels[j]
                        if comm_i != comm_j:
                            actual_flow = self.population[i] * self.flow_matrix[i, j]
                            flow_between_communities[comm_i, comm_j] += actual_flow

            # 获取社区的中心点
            self.gdf['lon'] = self.gdf.geometry.centroid.x
            self.gdf['lat'] = self.gdf.geometry.centroid.y
            gdf_community = self.gdf.dissolve(by='community_label', as_index=False)
            gdf_community['lon'] = gdf_community.geometry.centroid.x
            gdf_community['lat'] = gdf_community.geometry.centroid.y

            # 为每个簇分配颜色
            num_colors = len(gdf_community['community_label'].unique())
            community_colors = [colors(i % 20) for i in range(num_colors)]
            random.shuffle(community_colors)
            cmap = ListedColormap(community_colors)

            # 以较浅的颜色绘制社区背景
            self.gdf_boundary.plot(ax=ax, facecolor='white', edgecolor='black', lw=1.5, zorder=11)
            gdf_unpopulated = self.gdf_raw.loc[self.gdf_raw.population == 0].dissolve()
            gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.2, zorder=12)
            gdf_community.plot(ax=ax, column='community_label', cmap=cmap, edgecolor='gray', alpha=0.1, zorder=13)

            # 绘制跨社区的人口流动
            min_flow_plot, max_flow_plot = (100, 50000)  # 绘制控制范围
            rows, cols = np.indices(flow_between_communities.shape)
            flattened_matrix = np.column_stack((rows.ravel(), cols.ravel(), flow_between_communities.ravel()))
            sorted_matrix = flattened_matrix[flattened_matrix[:, 2].argsort()[::-1]]  # 按降序排序
            sorted_matrix = sorted_matrix[sorted_matrix[:, 0] != sorted_matrix[:, 1]]
            sorted_matrix = sorted_matrix[sorted_matrix[:, 2] > min_flow_plot]

            n_lines = 200000
            if len(sorted_matrix) > n_lines:
                sorted_matrix = sorted_matrix[:n_lines]

            cmap = plt.cm.get_cmap('RdYlBu_r')
            norm = mcolors.LogNorm(vmin=min_flow_plot, vmax=max_flow_plot)

            for orig, dest, flow in sorted_matrix[::-1]:  # 逆序绘制
                orig_x, orig_y = gdf_community.loc[orig, 'lon'], gdf_community.loc[orig, 'lat']
                dest_x, dest_y = gdf_community.loc[dest, 'lon'], gdf_community.loc[dest, 'lat']
                linewidth = min(0.15 + flow / max_flow_plot * 2.5, 2.5)
                color = cmap(norm(flow))
                ax.plot([orig_x, dest_x], [orig_y, dest_y], color=color, lw=linewidth, alpha=0.5, zorder=15)

            # 添加网格线
            ax.grid(ls='-.', lw=0.5, color='gray', zorder=10)
            ax.set_aspect('equal')

            # 设置标题
            reduction_percentage = int(round(simplification_rates[step_idx] * 100))
            # ax.set_title(f"ρ={reduction_percentage}% (Flow at Step {step + 1})")

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"flow_{reduction_percentage}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)

            # 保存图像
            # plt.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)
            # plt.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.05)
            # plt.tight_layout()
            plt.savefig(filepath, dpi=600)
            plt.close(fig)
            print(f"Saved figure to {filepath}")

if __name__ == '__main__':
    shapefile_path = "./GISData/Grid-Pop-1km-WGS84.shp"
    boundary_path = "./GISData/Boundary.shp"
    clustering_results_path = "./Output/constrained_clustering_results-test.npz"
    flow_matrix_path = "./Data/flow.npy"
    population_path = "./Data/population.npy"

    visualizer = FlowVisualizer(shapefile_path, boundary_path, clustering_results_path, flow_matrix_path, population_path)
    visualizer.plot_flow(simplification_rates=[0.2, 0.4, 0.6, 0.8, 0.9])
