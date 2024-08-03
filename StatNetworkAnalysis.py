import numpy as np

class NetworkAnalysis:
    def __init__(self, clustering_results_path, flow_matrix_path, population_path):
        # 加载聚类结果和流量数据
        data = np.load(clustering_results_path)
        self.labels_per_step = data['cluster_labels']
        self.flow_matrix = np.load(flow_matrix_path)
        self.population = np.load(population_path)
        self.flow_matrix = (self.flow_matrix.T*self.population).T.astype(int)
        
        # 获取节点总数
        self.n = self.labels_per_step.shape[1]

    def compute_simplification_rate(self, labels):
        # 计算简化率 ρ
        unique_clusters = np.unique(labels)
        simplification_rate = 1 - len(unique_clusters) / self.n
        return simplification_rate

    def compute_cluster_sizes(self, labels):
        # 计算每个簇的大小
        unique_labels, counts = np.unique(labels, return_counts=True)
        return counts

    def analyze_clusters(self):
        cluster_stats = {}
        for labels in self.labels_per_step:
            cluster_sizes = self.compute_cluster_sizes(labels)
            mean_size = np.mean(cluster_sizes)
            median_size = np.median(cluster_sizes)
            coeff_var = np.std(cluster_sizes)/mean_size
            max_size = np.max(cluster_sizes)
            num_singletons = np.sum(cluster_sizes == 1)
            simplification_rate = self.compute_simplification_rate(labels)

            rho = int(round(simplification_rate*100))
            
            cluster_stats[rho] = {
                'mean_size': mean_size,
                'median_size': median_size,
                'coeff_var': coeff_var,
                'max_size': max_size,
                'num_singletons': num_singletons
            }
        return cluster_stats

    def compute_cluster_flows(self, labels):
        # 获取每个节点的簇索引
        unique_labels, inverse_indices = np.unique(labels, return_inverse=True)
        num_clusters = len(unique_labels)

        # 构建簇间流动矩阵
        cluster_flow_matrix = np.zeros((num_clusters, num_clusters))
        
        # 使用numpy的高级索引和聚合操作计算簇间流动量
        np.add.at(cluster_flow_matrix, 
                  (inverse_indices[:, None], inverse_indices[None, :]), 
                  self.flow_matrix)

        # 去除对角线上的自流动
        # np.fill_diagonal(cluster_flow_matrix, 0)
        
        return cluster_flow_matrix

    def analyze_flows(self, list_rho):
        list_nc = [int(round(self.n*(100-rho)/100)) for rho in list_rho]
        print (list_nc)

        flow_stats = {}
        for i,labels in enumerate(self.labels_per_step):
            rho = 100-int(round(100*len(set(labels))/self.n))

            if len(set(labels)) not in list_nc:
                continue

            cluster_flow_matrix = self.compute_cluster_flows(labels)
            total_flow = np.sum(cluster_flow_matrix)
            flow_concentration = np.sum(np.max(cluster_flow_matrix, axis=1)) / total_flow
            clustering_coefficient = np.sum(cluster_flow_matrix>0) / cluster_flow_matrix.size
            # clustering_coefficient = np.trace(cluster_flow_matrix) / total_flow
            print(cluster_flow_matrix.shape)
            
            flow_stats[rho] = {
                'total_flow': total_flow,
                'flow_concentration': flow_concentration,
                'clustering_coefficient': clustering_coefficient
            }
        return flow_stats

if __name__ == '__main__':
    clustering_results_path = "./Output/constrained_clustering_results.npz"
    population_path = "./Data/population.npy"
    flow_matrix_path = "./Data/flow.npy"

    list_rho = [0,20,40,60,80,90,95]

    analyzer = NetworkAnalysis(clustering_results_path, flow_matrix_path, population_path)
    # cluster_stats = analyzer.analyze_clusters()

    # for rho in list_rho:
    #     print(f"Cluster Stats - rho={rho}:  {cluster_stats[rho]}")
    # exit()
    
    flow_stats = analyzer.analyze_flows(list_rho)
    # print("Flow Stats:", flow_stats)
    for rho in list_rho:
        try:
            print(f"Flow Stats - rho={rho}:  {flow_stats[rho]}")
        except:
            pass
    exit()