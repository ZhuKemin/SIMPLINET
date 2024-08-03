from shapely import wkt
import geopandas as gpd
import numpy as np
import pickle

class MatrixCalculatorAdjacency:
    def __init__(self, grid_path, output_path, buffer_distance=0.0):
        self.grid_path = grid_path
        self.output_path = output_path
        self.buffer_distance = buffer_distance
        self.grid = self.load_shapefile()

    def load_shapefile(self):
        grid = gpd.read_file(self.grid_path)
        return grid

    def calculate_adjacency_matrix_8neigbor(self):
        self.grid['TID'] = self.grid['TID'].astype(int)
        grid_valid = self.grid[self.grid['population'] > 0]

        # 应用缓冲区以增加容差
        grid_valid['geometry'] = grid_valid['geometry'].buffer(self.buffer_distance)

        # 找到相交的区域/排除自身
        joined = gpd.sjoin(grid_valid, grid_valid, how='inner', op='intersects')
        joined = joined[joined.TID_left != joined.TID_right]

        # 初始化邻接矩阵
        n = len(grid_valid)
        adjacency_matrix = np.zeros((n, n), dtype=int)

        # 相交的区域标记为1
        adjacency_matrix[joined.TID_left, joined.TID_right] = 1
        return adjacency_matrix

    def calculate_adjacency_matrix(self):
        self.grid['TID'] = self.grid['TID'].astype(int)
        grid_valid = self.grid[self.grid['population'] > 0]

        # 获取每个单元的边界线
        grid_valid['boundary'] = grid_valid['geometry'].boundary

        # 找到相交的区域，排除自身
        joined = gpd.sjoin(grid_valid, grid_valid, how='inner', op='intersects', lsuffix='left', rsuffix='right')
        joined = joined[joined['TID_left'] != joined['TID_right']]

        # 初始化邻接矩阵
        n = len(grid_valid)
        adjacency_matrix = np.zeros((n, n), dtype=int)

        # 记录四领域的相邻关系
        for idx, row in joined.iterrows():
            left_geom = grid_valid.loc[grid_valid['TID'] == row['TID_left'], 'boundary'].values[0]
            right_geom = grid_valid.loc[grid_valid['TID'] == row['TID_right'], 'boundary'].values[0]
            
            # 计算边界线的相交长度
            if left_geom.intersects(right_geom):
                intersection_length = left_geom.intersection(right_geom).length
                if intersection_length > 0:
                    adjacency_matrix[row['TID_left'], row['TID_right']] = 1
                    adjacency_matrix[row['TID_right'], row['TID_left']] = 1  # 对称性

        return adjacency_matrix

    def save_adjacency_matrix(self, adjacency_matrix):
        np.save(self.output_path, adjacency_matrix)

if __name__ == '__main__':
    grid_path = "../GISData/Grid-Pop-1km-WGS84.shp"
    output_path = '../Output/matrix_adjacency.npy'
    buffer_distance = 0.001  # 可以调整的缓冲区距离

    calculator = MatrixCalculatorAdjacency(grid_path, output_path, buffer_distance)
    adjacency_matrix = calculator.calculate_adjacency_matrix()
    calculator.save_adjacency_matrix(adjacency_matrix)

    print(f'Adjacency matrix saved to {output_path}')
