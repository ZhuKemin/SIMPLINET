import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import LogNorm
import os

class DAUCVisualizer:
    def __init__(self, shapefile_path, boundary_path):
        # 读取GIS数据
        self.gdf_raw = gpd.read_file(shapefile_path)
        self.gdf_boundary = gpd.read_file(boundary_path)
        self.gdf = self.gdf_raw.copy()

    def plot_dauc_distribution(self, dauc_data, rho, output_dir='./Output/Figure', use_log_scale=True):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fig, ax = plt.subplots(figsize=(10, 6))

        print (dauc_data)
        print (len(dauc_data))
        exit()

        # 将DAUC数据添加到GeoDataFrame
        self.gdf['dauc'] = dauc_data

        # 绘制底图各要素
        self.gdf_boundary.plot(ax=ax, facecolor='white', edgecolor='black', lw=1.5, zorder=11)
        gdf_unpopulated = self.gdf.loc[self.gdf['dauc'] == 0]
        gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.2, zorder=12)

        # DAUC数据绘图
        if use_log_scale:
            vmin, vmax = (np.log1p(0), np.log1p(0.04))
            self.gdf['dauc_log'] = np.log1p(self.gdf['dauc'])
            self.gdf.plot(ax=ax, column='dauc_log', vmin=vmin, vmax=vmax, cmap='RdYlBu_r', edgecolor="black", lw=0.2, legend=False, zorder=15)
        else:
            vmin, vmax = (0, 0.05)
            self.gdf.plot(ax=ax, column='dauc', vmin=vmin, vmax=vmax, cmap='RdYlBu_r', edgecolor="black", lw=0.2, legend=False, zorder=15)

        ax.grid(ls='-.', lw=0.5, color='gray', zorder=10)
        ax.set_aspect('equal')
        ax.set_title(f"DAUC Distribution (ρ = {rho})", fontsize=26)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'dauc_distribution_{rho}.png'), dpi=300)
        plt.close(fig)

    def plot_colorbar(self, output_dir='./Output/Figure', use_log_scale=True):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fig, ax = plt.subplots(figsize=(0.5, 8))

        if use_log_scale:
            vmin, vmax = (1, 2)
            log_norm = LogNorm(vmin=vmin, vmax=vmax)
            cmap = plt.cm.ScalarMappable(norm=log_norm, cmap='RdYlBu_r')
            cbar = fig.colorbar(cmap, cax=ax, orientation='vertical', extend='max')
            cbar.minorticks_off()
            cbar.set_ticks([vmin, vmax])
            cbar.ax.set_yticklabels(['0', '≥0.04'], fontsize=24)
        else:
            vmin, vmax = (0, 0.05)
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            cmap = plt.cm.ScalarMappable(norm=norm, cmap='RdYlBu_r')
            cbar = fig.colorbar(cmap, cax=ax, orientation='vertical')
            cbar.ax.tick_params(labelsize=24)

        plt.savefig(os.path.join(output_dir, 'dauc_cbar.png'), dpi=300, bbox_inches='tight')
        plt.close(fig)

if __name__ == '__main__':
    shapefile_path = "./GISData/Grid-Pop-1km-WGS84.shp"
    boundary_path = "./GISData/Boundary.shp"
    data_path = "./Data/Results/Plot data/fig1"

    visualizer = DAUCVisualizer(shapefile_path, boundary_path)

    simplification_rates = [0.2, 0.4, 0.6, 0.8, 0.9]
    for rate in simplification_rates:
        rho = rate
        subpath_abs = os.path.join(data_path, f'simplify_rate={rho:.2f}')
        dauc_data_path = os.path.join(subpath_abs, 'comm_delta_auc.npy')
        dauc_data = np.load(dauc_data_path)
        visualizer.plot_dauc_distribution(dauc_data, rho)
        visualizer.plot_colorbar()
