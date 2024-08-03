import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely import wkt
from matplotlib.colors import LogNorm

pop = np.load('./population.npy')
flow = np.load('./flow.npy')
od = np.load('./OD.npy')

df = pd.read_csv('./shenzhen_1km_sort.csv')
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')
gdf.set_crs(epsg=4326, inplace=True)

gdf['population'] = 0
condition = gdf['comm_ID'] != -1
gdf.loc[condition, 'population'] = pop



# 假设你的GeoDataFrame命名为gdf

# 先单独绘制population为0的部分，使用灰色
ax = gdf[gdf['population'] == 0].plot(color='grey', edgecolor='black', figsize=(10, 10))

# 再绘制其余的部分，使用colormap
gdf[gdf['population'] != 0].plot(ax=ax, vmin=1, vmax=50000,  column='population', cmap='summer', legend=True, edgecolor='black', figsize=(10, 10))


gdf = gdf.rename(columns={'tile_ID': 'TID_Raw', 'comm_ID': 'TID'})


# # 重新排列列顺序
# gdf = gdf[['TID', 'TID_Raw', 'population', 'lon', 'lat', 'geometry']]


# valid_gdf = gdf[gdf['population'] != 0]

# # 使用spatial join找到相交的区域
# joined = gpd.sjoin(valid_gdf, valid_gdf, how='inner', op='intersects')

# # 排除自己相交的情况
# joined = joined[joined.index != joined['index_right']]

# # 初始化邻接矩阵
# n = len(valid_gdf)
# adj_matrix = np.zeros((n, n), dtype=int)

# # 将相交的区域标记为1
# adj_matrix[joined.index, joined['index_right']] = 1

# exit()






# # 添加标题和其他注释
# plt.title('Map by Population')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')

# # 显示地图
# plt.show()

gdf.to_file('./Grid-Pop-1km-WGS84.shp')


print (gdf.head(30))

print (pop.shape)
print (flow.shape)

