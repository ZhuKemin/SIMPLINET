import numpy as np
import pickle
from scipy.signal import correlate


class SimilarityCalculator:
    def __init__(self, rt_input_path, output_path):
        self.rt_input_path = rt_input_path
        self.output_path = output_path
        self.Rt = self.load_Rt()
        self.num_regions = self.Rt.shape[1]

    def load_Rt(self):
        with open(self.rt_input_path, 'rb') as f:
            data = pickle.load(f)
        return data['Rt']

    def calculate_ccf(self, series1, series2):
        ccf = correlate(series1 - np.mean(series1), series2 - np.mean(series2))
        zero_lag_index = len(ccf) // 2
        ccf_zero_lag = ccf[zero_lag_index] / (np.std(series1) * np.std(series2) * len(series1))
        return ccf_zero_lag  # 使用零滞后的CCF值
    
    def construct_similarity_matrix(self):
        similarity_matrix = np.zeros((self.num_regions, self.num_regions))
        
        for i in range(self.num_regions):
            for j in range(i, self.num_regions):
                ccf = self.calculate_ccf(self.Rt[:, i], self.Rt[:, j])
                similarity_matrix[i, j] = ccf
                similarity_matrix[j, i] = ccf  # 由于 CCF 是对称的
        similarity_matrix = (similarity_matrix-np.min(similarity_matrix))/(np.max(similarity_matrix)-np.min(similarity_matrix))
        return similarity_matrix
    
    def save_similarity_matrix(self, similarity_matrix):
        np.save(self.output_path, similarity_matrix)


if __name__ == '__main__':
    rt_input_path = r'./rt_values.pkl'
    output_path = r'./similarity_matrix.npy'
    
    # Initialize the SimilarityCalculator class
    similarity_calculator = SimilarityCalculator(rt_input_path, output_path)
    
    # Construct the similarity matrix
    similarity_matrix = similarity_calculator.construct_similarity_matrix()
    
    # Save the similarity matrix
    # similarity_calculator.save_similarity_matrix(similarity_matrix)
    
    # Print the similarity matrix
    print(similarity_matrix)
