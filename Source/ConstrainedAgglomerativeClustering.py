import numpy as np

class ConstrainedClustering:
    def __init__(self, distance_matrix, adjacency_matrix, flow_matrix, population):
        self.distance_matrix = distance_matrix
        self.adjacency_matrix = adjacency_matrix
        self.flow_matrix = (flow_matrix.T * population).T.astype(int)
        self.n = distance_matrix.shape[0]
        self.cluster_labels = np.arange(self.n)
        self.cluster_distances = np.copy(distance_matrix)
        self.cluster_adjacency = np.copy(adjacency_matrix)
        self.labels_history = []  # 用于存储每次迭代后的簇标签
        self.flow_history = []  # 用于存储每次迭代后的流量矩阵
        self.current_max_label = self.n  # 新的簇编号从n开始
        self.index_to_label = np.arange(self.n)  # 查找数组，记录下标对应的簇号
        self.merge_info = []  # 用于记录合并信息以生成Z矩阵

    def find_closest_clusters(self, ignore_adjacency=False):
        # 找到邻接的簇对或忽略邻接关系
        if ignore_adjacency:
            mask = np.triu(np.ones_like(self.cluster_distances), 1)
        else:
            mask = np.triu(self.cluster_adjacency, 1)
        
        if not np.any(mask):
            return None, None
        # 获取最小距离的簇对
        adjacent_distances = np.where(mask, self.cluster_distances, np.inf)
        min_distance_index = np.argmin(adjacent_distances)
        closest_pair = np.unravel_index(min_distance_index, self.cluster_distances.shape)
        # 根据查找数组找到具体的簇编号
        c1 = self.index_to_label[closest_pair[0]]
        c2 = self.index_to_label[closest_pair[1]]
        return c1, c2

    def merge_clusters(self, c1, c2):
        # 分配新的簇编号
        new_cluster_label = self.current_max_label
        self.current_max_label += 1

        # 记录合并信息
        c1_index = np.where(self.index_to_label == c1)[0][0]
        c2_index = np.where(self.index_to_label == c2)[0][0]
        merge_distance = self.cluster_distances[c1_index, c2_index]
        size_c1 = np.sum(self.cluster_labels == c1)
        size_c2 = np.sum(self.cluster_labels == c2)
        self.merge_info.append([c1, c2, merge_distance, size_c1 + size_c2])

        # 更新簇标签和查找数组
        self.cluster_labels[self.cluster_labels == c1] = new_cluster_label
        self.cluster_labels[self.cluster_labels == c2] = new_cluster_label
        self.index_to_label = np.append(self.index_to_label, new_cluster_label)

        # 更新簇间距离和邻接矩阵
        new_distances = np.maximum(self.cluster_distances[c1_index, :], self.cluster_distances[c2_index, :])
        new_adjacency = np.logical_or(self.cluster_adjacency[c1_index, :], self.cluster_adjacency[c2_index, :])

        # 更新簇间流量矩阵
        new_flow = self.flow_matrix[c1_index, :] + self.flow_matrix[c2_index, :]

        # 添加新的簇数据
        self.cluster_distances = np.vstack([self.cluster_distances, new_distances])
        new_distances = np.append(new_distances, 0)  # 添加自身距离0
        self.cluster_distances = np.column_stack([self.cluster_distances, new_distances])
        self.cluster_adjacency = np.vstack([self.cluster_adjacency, new_adjacency])
        new_adjacency = np.append(new_adjacency, 0)  # 添加自身不邻接
        self.cluster_adjacency = np.column_stack([self.cluster_adjacency, new_adjacency])
        self.flow_matrix = np.vstack([self.flow_matrix, new_flow])
        new_flow = np.append(new_flow, 0)  # 添加自身流量0
        self.flow_matrix = np.column_stack([self.flow_matrix, new_flow])

        # 移除旧的簇
        self.cluster_distances = np.delete(self.cluster_distances, [c1_index, c2_index], axis=0)
        self.cluster_distances = np.delete(self.cluster_distances, [c1_index, c2_index], axis=1)
        self.cluster_adjacency = np.delete(self.cluster_adjacency, [c1_index, c2_index], axis=0)
        self.cluster_adjacency = np.delete(self.cluster_adjacency, [c1_index, c2_index], axis=1)
        self.flow_matrix = np.delete(self.flow_matrix, [c1_index, c2_index], axis=0)
        self.flow_matrix = np.delete(self.flow_matrix, [c1_index, c2_index], axis=1)

        # 更新查找数组，移除旧的簇
        self.index_to_label = np.delete(self.index_to_label, [c1_index, c2_index])

        # 记录当前簇标签和流量矩阵
        self.labels_history.append(np.copy(self.cluster_labels))
        self.flow_history.append(np.copy(self.flow_matrix).astype(int))

    def fit(self):
        while True:
            print(len(np.unique(self.cluster_labels)))
            c1, c2 = self.find_closest_clusters()
            if c1 is None or c2 is None:
                # 如果找不到邻接簇对，则忽略邻接关系继续寻找
                c1, c2 = self.find_closest_clusters(ignore_adjacency=True)
                if c1 is None or c2 is None:
                    # 如果依然找不到簇对，则终止
                    break
            self.merge_clusters(c1, c2)
            
            # 如果所有簇都合并成一个簇，终止
            if np.all(self.cluster_labels == self.cluster_labels[0]):
                break

        # 记录最终的簇分配
        return self.cluster_labels

    def save_results(self, clustering_results_path="../Output/constrained_clustering_results.npz", flow_matrix_path="../Output/flow_history.npy"):
        np.savez(clustering_results_path, cluster_labels=self.labels_history)
        np.save(flow_matrix_path, self.flow_history)

# 主程序
similarity_matrix = np.load("../Output/matrix_similarity.npy")
adjacency_matrix = np.load("../Output/matrix_adjacency.npy")
flow_matrix = np.load("../Data/flow.npy")
population = np.load("../Data/population.npy")
distance_matrix = 1 - similarity_matrix

clustering = ConstrainedClustering(distance_matrix, adjacency_matrix, flow_matrix, population)
clustering.fit()
clustering.save_results()
