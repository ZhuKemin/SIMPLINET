import numpy as np
import matplotlib.pyplot as plt

class MaxClusterSizeVisualizer:
    def __init__(self, clustering_results_path):
        # 加载聚类结果
        data = np.load(clustering_results_path)
        self.labels_per_step = data['cluster_labels']
        
        # 获取初始节点数和简化步骤数
        self.n_nodes = self.labels_per_step.shape[1]
        self.n_steps = self.labels_per_step.shape[0]

        self.simplification_rates = np.array([1-len(np.unique(labels))/self.n_nodes for labels in self.labels_per_step])

    def compute_max_cluster_size(self):
        max_cluster_sizes = []

        for step in range(self.n_steps):
            labels = self.labels_per_step[step]
            cluster_sizes = np.bincount(labels)
            max_size = np.max(cluster_sizes)
            max_cluster_sizes.append(max_size)

        return max_cluster_sizes

    def compute_singleton_clusters(self):
        singleton_clusters = []
        singleton_proportions = []

        for step in range(self.n_steps):
            labels = self.labels_per_step[step]
            cluster_sizes = np.bincount(labels)
            singletons = np.sum(cluster_sizes == 1)
            singletons_norm = singletons / len(cluster_sizes)
            singleton_clusters.append(singletons)
            singleton_proportions.append(singletons_norm)

        return singleton_clusters, singleton_proportions

    def plot_max_cluster_size(self, output_path='./Output/Figure/max_cluster_size.png'):
        max_cluster_sizes = self.compute_max_cluster_size()
        simplification_rates = self.simplification_rates

        plt.figure(figsize=(10, 6))
        plt.plot(simplification_rates, max_cluster_sizes, marker='o', label='Max Cluster Size')
        plt.xlabel('Simplification Rate')
        plt.ylabel('Max Cluster Size')
        plt.title('Max Cluster Size vs Simplification Rate')
        plt.grid(ls='-.', lw=0.5, color='gray')
        plt.tight_layout()
        plt.show()
        plt.close()

    def plot_singleton_clusters(self, output_path='./Output/Figure/singleton_clusters.png'):
        singleton_clusters, singleton_proportions = self.compute_singleton_clusters()
        simplification_rates = self.simplification_rates

        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = 'tab:orange'
        ax1.set_xlabel('Simplification Rate')
        ax1.set_ylabel('Number of Singleton Clusters', color=color)
        ax1.plot(simplification_rates, singleton_clusters, marker='o', label='Singleton Clusters', color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Proportion of Singleton Clusters', color=color)
        ax2.plot(simplification_rates, singleton_proportions, marker='o', linestyle='--', label='Singleton Proportion', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        fig.tight_layout()
        plt.title('Singleton Clusters vs Simplification Rate')
        plt.grid(ls='-.', lw=0.5, color='gray')
        plt.show()
        plt.close()

    def print_indicators_at_rates(self, target_rates=[0.2, 0.9]):
        max_cluster_sizes = self.compute_max_cluster_size()
        singleton_clusters, singleton_proportions = self.compute_singleton_clusters()

        for target_rate in target_rates:
            closest_step = np.argmin(np.abs(self.simplification_rates - target_rate))
            closest_rate = self.simplification_rates[closest_step]
            max_size = max_cluster_sizes[closest_step]
            singletons = singleton_clusters[closest_step]
            singleton_prop = singleton_proportions[closest_step]
            print(f"Simplification rate closest to {target_rate}: {closest_rate}")
            print(f"  Max Cluster Size: {max_size}")
            print(f"  Number of Singleton Clusters: {singletons}")
            print(f"  Proportion of Singleton Clusters: {singleton_prop:.4f}")

if __name__ == '__main__':
    clustering_results_path = "./Output/constrained_clustering_results.npz"

    visualizer = MaxClusterSizeVisualizer(clustering_results_path)
    visualizer.plot_max_cluster_size()
    visualizer.plot_singleton_clusters()
    visualizer.print_indicators_at_rates([0.2, 0.9])
