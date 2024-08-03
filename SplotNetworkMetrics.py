import numpy as np
import matplotlib.pyplot as plt

class NetworkMetricsVisualizer:
    def __init__(self, flow_history_path):
        # 从文件中加载每一步的流量矩阵
        self.flow_history = np.load(flow_history_path, allow_pickle=True)
        self.n_steps = len(self.flow_history)-1

    def compute_clustering_coefficient(self, flow_matrix):
        # 将对角线元素设置为零
        np.fill_diagonal(flow_matrix, 0)
        # 计算流量矩阵中非零元素的比例（即有边的比例）
        n_elements = flow_matrix.size-len(flow_matrix)
        n_non_zero = np.count_nonzero(flow_matrix > 100000)
        clustering_coefficient = n_non_zero / n_elements
        return clustering_coefficient

    def plot_clustering_coefficient(self, output_path='./Output/Figure/clustering_coefficient.png'):
        clustering_coefficients = []

        for step in range(self.n_steps):
            print (step)
            flow_matrix = self.flow_history[step].copy()  # 创建流量矩阵的副本以避免修改原始数据
            # print (np.sum(flow_matrix>=0)/flow_matrix.size)
            # exit()


            coeff = self.compute_clustering_coefficient(flow_matrix)
            clustering_coefficients.append(coeff)

        simplification_rates = np.linspace(0, 1, self.n_steps)
        plt.figure(figsize=(5, 3))
        plt.plot(simplification_rates, clustering_coefficients, marker='o')
        plt.xlabel('Simplification Rate')
        plt.ylabel('Clustering Coefficient')
        plt.title('Clustering Coefficient vs Simplification Rate')
        plt.grid(ls='-.', lw=0.5, color='gray')
        plt.tight_layout()
        # plt.savefig(output_path, dpi=300)
        plt.show()
        plt.close()
        print(f"Clustering coefficient plot saved to {output_path}")

if __name__ == '__main__':
    flow_history_path = "./Output/flow_history.npy"

    visualizer = NetworkMetricsVisualizer(flow_history_path)
    visualizer.plot_clustering_coefficient()
