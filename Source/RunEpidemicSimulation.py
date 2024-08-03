import numpy as np
import matplotlib.pyplot as plt
import pickle
from EpidemicModel import EpidemicModel
from RtCalculator import RtCalculator
from MatrixCalculatorSimilarity import SimilarityCalculator

class RunEpidemicSimulation:
    def __init__(self):
        self.epidemic_params = {
            'beta' :   0.80,
            'sigma':   0.33,
            'gamma':   0.14,
            'Pm':      0.40,
            'si_mean': 4.00,
            'si_std':  2.50
        }
        self.sim_settings = {
            'sim_days': 160
        }
        self.mobility_path = "../data/flow.npy"
        self.population_path = "../data/population.npy"
        self.sim_results_path = '../Output/epidemic_model_results.pkl'
        self.rt_output_path = '../Output/rt_values.pkl'
        self.similarity_output_path = '../Output/matrix_similarity.npy'

    def run_simulation(self):
        mobility = np.load(self.mobility_path)
        population = np.load(self.population_path)
        initial_infected = np.zeros_like(population)
        initial_infected[np.argmax(population)] = 100

        model = EpidemicModel(self.epidemic_params, mobility, population, initial_infected, self.sim_settings)
        sim_results = model.simulate()
        model.save_results(sim_results, self.sim_results_path)
        print(f'Simulation results saved to {self.sim_results_path}')

    def calculate_rt(self):
        rt_calculator = RtCalculator(self.sim_results_path, self.rt_output_path)
        Rt = rt_calculator.calculate_Rt()
        rt_calculator.save_Rt(Rt)
        print(f'Rt values saved to {self.rt_output_path}')

    def calculate_similarity(self):
        similarity_calculator = SimilarityCalculator(self.rt_output_path, self.similarity_output_path)
        # similarity_calculator = SimilarityCalculator(self.sim_results_path, self.similarity_output_path)
        similarity_matrix = similarity_calculator.construct_similarity_matrix()
        similarity_calculator.save_similarity_matrix(similarity_matrix)
        print(f'Similarity matrix saved to {self.similarity_output_path}')
        print(similarity_matrix)


if __name__ == '__main__':
    simulation_runner = RunEpidemicSimulation()
    # simulation_runner.run_simulation()
    # simulation_runner.calculate_rt()
    simulation_runner.calculate_similarity()
