import numpy as np
import pickle
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from matplotlib import pyplot as plt

class RtCalculator:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.results = self.load_results()
        
        self.metadata = self.results['metadata']
        self.si_mean = self.metadata['epidemic_params']['si_mean']
        self.si_std = self.metadata['epidemic_params']['si_std']
        self.I = self.results['results']['I']/self.metadata['population']*1e5  # 转换为10万人流行率

        overall_I = np.sum(self.results['results']['I'], axis=1)/sum(self.metadata['population'])
        self.sday = np.where(overall_I>1e-3)[0][0 ]
        self.eday = np.where(overall_I>1e-3)[0][-1]

    def load_results(self):
        with open(self.input_path, 'rb') as f:
            data = pickle.load(f)
        return data
    
    def calculate_Rt_for_region(self, infection_counts, region_index):
        infection_counts_str = '\n'.join(map(str, infection_counts))
        process = subprocess.Popen(['Rscript', 'RtCalculator.R', str(self.si_mean), str(self.si_std)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=infection_counts_str.encode())
        
        if process.returncode != 0:
            print(f"Error in R script for region {region_index}: {stderr.decode()}")
            raise RuntimeError("R script execution failed")
        
        rt_values = np.fromstring(stdout.decode(), sep='\n')
        return region_index, rt_values

    def calculate_Rt(self):
        Rt = [None] * self.I.shape[1]
        num_regions = self.I.shape[1]
        completed = 0

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.calculate_Rt_for_region, self.I[self.sday:self.eday, i].astype(int).tolist(), i): i for i in range(num_regions)}
            for future in as_completed(futures):
                region_index, rt_values = future.result()
                Rt[region_index] = rt_values
                completed += 1
                print(f"Progress: {completed}/{num_regions} regions completed.")
        Rt = np.c_[Rt].T
        return Rt

    def save_Rt(self, Rt):
        with open(self.output_path, 'wb') as f:
            pickle.dump({'Rt': Rt}, f)

if __name__ == '__main__':
    input_path = r'../Output/epidemic_model_results.pkl'
    output_path = r'./rt_values.pkl'
    
    # Initialize the RtCalculator class
    rt_calculator = RtCalculator(input_path, output_path)
    
    # Calculate Rt values
    Rt = rt_calculator.calculate_Rt()

    # Save Rt values
    # rt_calculator.save_Rt(Rt)
    