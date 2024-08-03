import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap
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


class ClusteringVisualizer:
    def __init__(self, shapefile_path, boundary_path, clustering_results_path):
        # 读取GIS数据
        self.gdf_raw = gpd.read_file(shapefile_path)
        self.gdf = self.gdf_raw.loc[self.gdf_raw.population > 0]
        self.gdf_boundary = gpd.read_file(boundary_path)

        # 加载保存的聚类结果
        data = np.load(clustering_results_path)
        self.labels_per_step = data['cluster_labels']

        # 检查GIS数据和聚类数据的一致性
        assert len(self.gdf) == self.labels_per_step.shape[1], "The number of grid cells and clustering labels must match."

    def plot_clustering(self, simplification_rates, cmap='tab20', output_dir='./Output/Figure/Cluster'):
        colors = plt.cm.get_cmap(cmap)
        num_steps = self.labels_per_step.shape[0]
        selected_steps = [int(rate * num_steps) for rate in simplification_rates]
        # selected_steps = [int(num_steps*(rate+(num_steps/len(self.gdf_raw))-1)) for rate in simplification_rates]

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for step_idx, step in enumerate(selected_steps):
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)
            

            # 获取当前步骤的聚类标签
            labels = self.labels_per_step[step]

            # 创建一个新的 GeoDataFrame 来存储绘图所需的数据
            self.gdf['community_label'] = labels

            # 绘制外边框，不要颜色和底纹
            self.gdf_boundary.plot(ax=ax, facecolor='white', edgecolor='black', lw=1.5, zorder=11)

            # 绘制无人区域，先dissolve然后绘制
            gdf_unpopulated = self.gdf_raw.loc[self.gdf_raw.population == 0].dissolve()
            gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.2, zorder=12)

            # Dissolve 根据 community_label 聚合
            gdf_community = self.gdf.dissolve(by='community_label')
            gdf_community.reset_index(inplace=True)

            # 为每个簇分配颜色
            num_colors = len(gdf_community['community_label'].unique())
            community_colors = [colors(i % 20) for i in range(num_colors)]
            random.shuffle(community_colors)
            cmap = ListedColormap(community_colors)

            # 绘制社区区域
            gdf_community.plot(ax=ax, column='community_label', cmap=cmap, edgecolor='gray', alpha=0.3, zorder=13)

            # 找出仅包含一个网格的社区，并绘制
            gdf_community['grid_count'] = self.gdf.groupby('community_label').size().reindex(gdf_community['community_label']).values
            gdf_community_single = gdf_community.loc[gdf_community.grid_count == 1]
            gdf_community_single.plot(ax=ax, facecolor='dimgray', edgecolor='none', alpha=1.0, zorder=14)

            # 添加网格线
            ax.grid(ls='-.', lw=0.5, color='gray', zorder=10)
            ax.set_aspect('equal')

            # 设置标题
            reduction_percentage = int(round(simplification_rates[step_idx]*100))
            # ax.set_title(f"ρ={reduction_percentage}% (Clustering at Step {step + 1})")
            # ax.set_title(f"n={len(np.unique(labels))/1818}")

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"clustering_{reduction_percentage}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)

            # 保存图像
            # plt.tight_layout()

            # plt.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)
            plt.savefig(filepath, dpi=600)
            plt.close(fig)
            print(f"Saved figure to {filepath}")

if __name__ == '__main__':
    shapefile_path = "./GISData/Grid-Pop-1km-WGS84.shp"
    boundary_path = "./GISData/Boundary.shp"
    clustering_results_path = "./Output/constrained_clustering_results.npz"

    visualizer = ClusteringVisualizer(shapefile_path, boundary_path, clustering_results_path)
    visualizer.plot_clustering(simplification_rates=[0.2, 0.4, 0.6, 0.8, 0.9])
