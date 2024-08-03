import numpy as np
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import os
from datetime import datetime

# 设置字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 20,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

def load_merge_info(filepath):
    """加载 merge_info 数据"""
    return np.load(filepath)

def create_linkage_matrix(merge_info):
    """生成链接矩阵 Z"""
    Z = np.array(merge_info)
    return Z

def plot_horizontal_dendrogram(Z, max_distance=0.025, linewidth=0.02, save_path='./Output/Figure/Dendrogram'):
    """绘制横向树状图，使用Set2配色，并保存图片"""

    # 设置Set2调色板，转换为十六进制字符串
    # palette = [to_hex(plt.get_cmap('tab10')(i)) for i in range(10)]
    # palette = [to_hex(plt.get_cmap('Paired')(i)) for i in range(8)]
    # palette = [to_hex(plt.get_cmap('Set3')(i)) for i in range(10)]
    palette = [to_hex(plt.get_cmap('Set2')(i)) for i in range(10)]

    # 可选：随机打乱颜色顺序
    np.random.shuffle(palette)
    sch.set_link_color_palette(palette)

    dendro = sch.dendrogram(Z, orientation='right', color_threshold=max_distance, above_threshold_color='None')
    plt.figure(figsize=(16, 4))

    # 手动设置线条宽度
    icoord = np.array(dendro['icoord'])
    dcoord = np.array(dendro['dcoord'])
    color_list = np.array(dendro['color_list'])
    ax = plt.gca()
    for xs, ys, color in zip(icoord, dcoord, color_list):
        ax.plot(ys, xs, color=color, linewidth=linewidth, alpha=1.0)

    # 设置x轴和y轴标签
    # plt.xlabel('Simplification Rate ρ')
    plt.ylabel('Clusters')

    # 隐藏x轴和y轴的刻度和刻度标签
    plt.xticks([])
    plt.yticks([])

    # 获取当前的ylim并进行调整
    ymin, ymax = plt.ylim()
    plt.ylim(ymin - 300, ymax + 300)  # 扩大上下边界

    plt.xlim(0, max_distance * 0.9)

    # 创建保存目录
    os.makedirs(save_path, exist_ok=True)
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'Dendrogram_{timestamp}.png'
    file_path = os.path.join(save_path, filename)
    plt.savefig(file_path, dpi=600, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    # 加载 merge_info 数据
    merge_info = load_merge_info("./Output/merge_info.npy")
    print (merge_info.shape)
    print (merge_info[0])
    exit()

    # 创建链接矩阵 Z
    Z = create_linkage_matrix(merge_info)
    idx_increasing = np.where(Z[:-1,2]>Z[1:,2])[0][0]
    max_distance = Z[idx_increasing+1, 2]

    # 执行10次制图程序
    for _ in range(10):
        plot_horizontal_dendrogram(Z, max_distance=0.025, linewidth=0.8)
