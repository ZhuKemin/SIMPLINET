import geopandas as gpd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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
        
    def load_results(self):
        with open(self.results_path, 'rb') as f:
            data = pickle.load(f)
        return data['results'], data['metadata']
    
    def load_shapefile(self):
        return gpd.read_file(self.shapefile_path)
    
    def load_boundary(self):
        return gpd.read_file(self.boundary_path)
    
    def calculate_prevalence(self, day):
        prevalence = self.results['I'][day] / self.metadata['population']
        return prevalence
    
    def plot_prevalence(self, days):
        for day in days:
            prevalence = self.calculate_prevalence(day)
            self.grid['prevalence'] = prevalence

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            self.grid.plot(column='prevalence', ax=ax, legend=True,
                           cmap='viridis', edgecolor='black', linewidth=0.5,
                           legend_kwds={'label': "Prevalence Rate",
                                        'orientation': "horizontal"},
                           zorder=10)

            # 绘制外轮廓
            self.boundary.plot(ax=ax, facecolor='none', edgecolor='black', lw=1.5, zorder=11)
            
            # 特殊处理无人区
            gdf_unpopulated = self.grid_raw.loc[self.grid_raw['population'] == 0].dissolve()
            gdf_unpopulated.plot(ax=ax, color='none', edgecolor='black', hatch='//', alpha=0.2, zorder=12)

            # 绘制人口最多的网格红框
            max_pop_area = self.grid.loc[self.max_population_idx]
            if max_pop_area.geometry.type == 'Polygon':
                x, y = max_pop_area.geometry.exterior.xy
                ax.plot(x, y, color='red', linewidth=2, zorder=13)
            else:
                for polygon in max_pop_area.geometry:
                    x, y = polygon.exterior.xy
                    ax.plot(x, y, color='red', linewidth=2, zorder=13)

            plt.title(f'Prevalence on Day {day}')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.grid(False)
            plt.show()

if __name__ == '__main__':
    results_path = './Output/epidemic_model_results.pkl'
    shapefile_path = './GISData/Grid-Pop-1km-WGS84.shp'
    boundary_path = './GISData/Boundary.shp'
    plotter = EpidemicPlotter(results_path, shapefile_path, boundary_path)
    plotter.plot_prevalence([20, 30, 40, 50])
