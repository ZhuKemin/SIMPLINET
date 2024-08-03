import numpy as np
import matplotlib.pyplot as plt

class ClusterSizeVisualizer:
    def __init__(self, clustering_results_path):
        # 加载聚类结果
        data = np.load(clustering_results_path)
        self.labels_per_step = data['cluster_labels']
        
        # 获取初始节点数和简化步骤数
        self.n_nodes = self.labels_per_step.shape[1]
        self.n_steps = self.labels_per_step.shape[0]

    def plot_cluster_size_distribution(self, output_path='./Output/Figure/cluster_size_distribution.png'):
        x = []
        y = []

        for step in range(self.n_steps):
            labels = self.labels_per_step[step]
            cluster_sizes = np.bincount(labels)
            simplification_rate = step / self.n_nodes

            for size in cluster_sizes:
                x.append(simplification_rate)
                y.append(size)

        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, alpha=0.5)
        plt.xlabel('Simplification Rate')
        plt.ylabel('Cluster Size')
        plt.title('Cluster Size Distribution vs Simplification Rate')
        plt.yscale('log')  # 如果簇大小分布跨度较大，使用对数尺度
        plt.grid(ls='-.', lw=0.5, color='gray')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Cluster size distribution plot saved to {output_path}")

    def plot_coefficient_of_variation(self, output_path='./Output/Figure/coefficient_of_variation.png'):
        x = []
        y = []

        for step in range(self.n_steps):
            labels = self.labels_per_step[step]
            cluster_sizes = np.bincount(labels)
            simplification_rate = step / self.n_nodes

            if len(cluster_sizes) > 1:  # 确保有多个簇才能计算变异系数
                mean_size = np.mean(cluster_sizes)
                std_size = np.std(cluster_sizes)
                coefficient_of_variation = std_size / mean_size
                x.append(simplification_rate)
                y.append(coefficient_of_variation)

        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, alpha=0.5)
        plt.xlabel('Simplification Rate')
        plt.ylabel('Coefficient of Variation')
        plt.title('Coefficient of Variation vs Simplification Rate')
        plt.grid(ls='-.', lw=0.5, color='gray')
        plt.tight_layout()
        # plt.savefig(output_path, dpi=300)
        plt.show()
        exit()
        plt.close()
        print(f"Coefficient of variation plot saved to {output_path}")

if __name__ == '__main__':
    clustering_results_path = "./Output/constrained_clustering_results.npz"

    visualizer = ClusterSizeVisualizer(clustering_results_path)
    # visualizer.plot_cluster_size_distribution()
    visualizer.plot_coefficient_of_variation()
