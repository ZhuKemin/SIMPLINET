import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.wkt import loads as load_wkt
from shapely.geometry import LineString

# 1. 读取 CSV 并过滤掉 comm_ID 等于 -1 的记录
df = pd.read_csv('./shenzhen_1km_sort.csv')
df = df[df['comm_ID'] != -1]

# 2. 读取 OD.npy 文件
od_matrix = np.load('./OD.npy')
print (od_matrix)

# 3. 将 geometry 列转换为 Shapely 对象
df['geometry'] = df['geometry'].apply(load_wkt)

# 4. 创建网格的 GeoDataFrame 并转换坐标系到 EPSG:3857
gdf_grid = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
gdf_grid = gdf_grid.to_crs(epsg=3857)
gdf_grid.to_file('./shenzhen_1km_grid.shp', driver='ESRI Shapefile')

# 5. 创建流动线的 GeoDataFrame
lines = []
flows = []
comm_id_to_geom = {row['comm_ID']: row['geometry'].centroid for _, row in gdf_grid.iterrows()}

# 将矩阵展平成稀疏表示
rows, cols = od_matrix.nonzero()
for r, c in zip(rows, cols):
    if r != c and od_matrix[r, c] > 0:
        start_centroid = comm_id_to_geom[r]
        end_centroid = comm_id_to_geom[c]
        lines.append(LineString([start_centroid, end_centroid]))
        flows.append(od_matrix[r, c])


print (flows)
print (min(flows))
print (max(flows))
exit()

gdf_lines = gpd.GeoDataFrame({'geometry': lines, 'flow': flows}, crs='EPSG:3857')
# gdf_lines.to_file('./shenzhen_OD_lines.shp', driver='ESRI Shapefile')
