import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import rankdata

# 设置字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class MatrixAnalyzer:
    def __init__(self, adjacency_path, distance_path, population_diff_path, similarity_path, flow_path):
        self.adjacency_matrix = self.load_numpy(adjacency_path)
        self.distance_matrix = self.load_numpy(distance_path)
        self.population_diff_matrix = self.load_numpy(population_diff_path)
        self.similarity_matrix = self.load_numpy(similarity_path)
        self.flow_matrix = self.load_numpy(flow_path)
        self.data = self.create_dataframe()

    def load_pickle(self, file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def load_numpy(self, file_path):
        return np.load(file_path)

    def create_dataframe(self):
        adjacency_flat = self.adjacency_matrix.flatten()
        distance_flat = self.distance_matrix.flatten()
        population_diff_flat = self.population_diff_matrix.flatten()
        similarity_flat = self.similarity_matrix.flatten()
        flow_flat = self.flow_matrix.flatten()

        data = pd.DataFrame({
            'Adjacency': adjacency_flat,
            'Distance': distance_flat,
            'Population Difference': population_diff_flat,
            'Similarity': similarity_flat,
            'Flow': flow_flat
        })

        data = data.loc[data.Flow > 0]
        data = data.sample(n=10000, random_state=42)
        return data

    def plot_kde_with_regression(self, xlabel, ylabel, bw_adjust=1, save_path=None):
        x = rankdata(self.data[xlabel]) / len(self.data)
        y = rankdata(self.data[ylabel]) / len(self.data)

        plt.figure(figsize=(6, 6))
        ax = sns.kdeplot(x=x, y=y, cmap="viridis", shade=True, thresh=0.05, bw_adjust=bw_adjust)
        # ax = sns.kdeplot(x=x, y=y, cmap="bwr", shade=True, thresh=0.05, bw_adjust=bw_adjust)
        
        # 绘制回归线和置信区间
        sns.regplot(x=x, y=y, scatter=False, ci=99, ax=ax, line_kws={'color': 'tab:red'})
        plt.scatter(x, y, facecolor='k', edgecolor=None, s=0.01, alpha=0.3)
        
        # 设置网格
        plt.grid(True, linestyle='-.', linewidth=0.5, color='gray')
        ax.set_axisbelow(True)  # 确保网格线在底层
        
        plt.xlabel(f"Scaled Rank of {xlabel}", fontsize=20)
        plt.ylabel(f"Scaled Rank of {ylabel}", fontsize=20)
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        
        # 设置刻度标签的字体大小
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)

        if save_path:
            plt.savefig(save_path, dpi=600)
        # plt.show()

    def analyze(self):
        # 创建保存图像的文件夹
        os.makedirs('./Output/Figure/Regression', exist_ok=True)
        
        self.plot_kde_with_regression('Flow',                  'Similarity', bw_adjust=1.0, save_path='./Output/Figure/Regression/flow_similarity.png')
        self.plot_kde_with_regression('Distance',              'Similarity', bw_adjust=1.0, save_path='./Output/Figure/Regression/distance_similarity.png')
        self.plot_kde_with_regression('Population Difference', 'Similarity', bw_adjust=1.0, save_path='./Output/Figure/Regression/pop_similarity.png')

if __name__ == '__main__':
    adjacency_path = './Output/matrix_adjacency.npy'
    distance_path = './Output/matrix_distance.npy'
    pop_diff_path = './Output/matrix_pop_diff.npy'
    similarity_path = './Output/matrix_similarity.npy'
    flow_path = './Data/flow.npy'

    analyzer = MatrixAnalyzer(adjacency_path, distance_path, pop_diff_path, similarity_path, flow_path)
    analyzer.analyze()
