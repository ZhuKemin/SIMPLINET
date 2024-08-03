import numpy as np
import matplotlib.pyplot as plt

# 配置图形属性
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 16,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class ScatterPlot:
    def __init__(self):
        self.datasets = []
        self.special_point = None
    
    def add_dataset(self, x_path, y_path, label, color, marker, size):
        """加载数据集并添加到图形中"""
        x_data = np.load(x_path)
        y_data = np.load(y_path)
        self.datasets.append({
            'x': x_data,
            'y': y_data,
            'label': label,
            'color': color,
            'marker': marker,
            'size': size
        })
    
    def set_special_point(self, x, y, label, color, marker, size):
        """设置图中的特殊点"""
        self.special_point = {
            'x': x,
            'y': y,
            'label': label,
            'color': color,
            'marker': marker,
            'size': size
        }
    
    def plot(self):
        """绘制散点图"""
        fig, ax = plt.subplots()
        
        # 绘制数据集
        for data in self.datasets:
            ax.scatter(data['x'], data['y'], label=data['label'], 
                       color=data['color'], marker=data['marker'], s=data['size'])
        
        # 绘制特殊点
        if self.special_point:
            ax.scatter(self.special_point['x'], self.special_point['y'], 
                       color=self.special_point['color'], 
                       marker=self.special_point['marker'], s=self.special_point['size'], alpha=0.7)
        
        ax.set_xlabel('Simplification rate $ρ$')
        ax.set_ylabel(r'Simulation Error $\Delta \epsilon$')
        ax.set_xlim(0, 1)
        ax.set_ylim(bottom=1e-6)
        ax.grid(ls="-.", lw=0.3, color='lightgray')
        ax.set_axisbelow(True)

        # 增大图例中散点的大小，并单独设置特殊点的图例大小
        handles, labels = ax.get_legend_handles_labels()
        special_handle = plt.Line2D([0], [0], color=self.special_point['color'], marker=self.special_point['marker'], 
                                    markersize=6, linestyle='None', label=self.special_point['label'])
        handles.append(special_handle)
        labels.append(self.special_point['label'])
        ax.legend(handles=handles, scatterpoints=1, markerscale=1.2, prop={'size': 12}, loc='lower right')
        
        plt.yscale('log')
        plt.tight_layout()
        # plt.show()
        plt.savefig('fig-scatter-new.png', dpi=600)

# 创建 ScatterPlot 实例
scatter_plot = ScatterPlot()

# 添加数据集
scatter_plot.add_dataset('./scCluster_simplify_ratio.npy', './scCluster_delta_auc.npy', 'Simplinet', '#5C8DC7', 'o', 8)
scatter_plot.add_dataset('./scLeiden_simplify_ratio.npy' , './scLeiden_delta_auc.npy' , 'Leiden'   , '#198E5C', 'x', 12)
scatter_plot.add_dataset('./scLouvian_simplify_ratio.npy', './scLouvian_delta_auc.npy', 'Louvian'  , '#EF7F29', 's', 4)

# 设置特殊点
special_x = 1 - (74 / 1818)
special_y = 0.00815056881216123
scatter_plot.set_special_point(special_x, special_y, 'Administrative', '#EC050E', '*', 80)

# 绘制散点图
scatter_plot.plot()
