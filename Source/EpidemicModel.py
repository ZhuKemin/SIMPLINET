import numpy as np
import pandas as pd
import time

class EpidemicModel:
    def __init__(self, epidemic_params, mobility, population, initial_infected, sim_settings):
        self.epidemic_params = epidemic_params
        self.beta = epidemic_params.get('beta')
        self.sigma = epidemic_params.get('sigma')
        self.gamma = epidemic_params.get('gamma')
        
        self.mobility = mobility
        self.population = population
        self.initial_infected = initial_infected
        self.Pm = epidemic_params.get('Pm', 0.4)
        
        self.sim_days = sim_settings.get('sim_days')
        self.reset()

    def reset(self):
        self.simState = np.zeros((len(self.population), 4))
        self.simState[:, 0] = self.population - self.initial_infected
        self.simState[:, 2] = self.initial_infected
        self.simRes = []
        self.actions = []
        self.incidence = []
        self.day = 0

    def step(self, action = []):
        if len(action) == 0:
            action = np.zeros(len(self.mobility))

        self.day += 1
        self.actions.append(action)

        contagious_infects = self.simState[:, 1] + self.Pm * self.simState[:, 2]

        contagious_toJ = np.sum(self.mobility.T * contagious_infects, axis=1)
        contagious_toJ[contagious_toJ < 0.0] = 0.0

        all_toJ = np.sum(self.population * self.mobility.T, axis=1)

        with np.errstate(divide='ignore', invalid='ignore'):
            contagious_ratio_toJ = np.nan_to_num(contagious_toJ / all_toJ, nan=0.0, posinf=0.0, neginf=0.0)

        lam = np.sum(self.mobility * contagious_ratio_toJ * self.beta * (1 - 0.25 * action), axis=1)
        lam[lam < 0.0] = 0.0

        dS = -self.simState[:, 0] * lam
        dE = self.simState[:, 0] * lam - self.sigma * self.simState[:, 1]
        dI = self.sigma * self.simState[:, 1] - self.gamma * self.simState[:, 2]
        dR = self.gamma * self.simState[:, 2]

        # 记录每日新增感染人数
        daily_incidence = self.sigma * self.simState[:, 1]
        self.incidence.append(daily_incidence)

        dState = [dS, dE, dI, dR]
        self.simState = self.simState + np.array(dState).T
        self.simRes.append(self.simState)
       
        done = False
        if self.day >= self.sim_days:
            done = True

        return done

    def simulate(self):
        actions = np.ones((self.sim_days, len(self.population)))
        self.reset()
        current_day = 0
        
        while current_day < self.sim_days:
            done = self.step(action=actions[current_day])
            current_day += 1
            if done:
                break
        
        results = {
            'S': np.array(self.simRes)[:, :, 0],
            'E': np.array(self.simRes)[:, :, 1],
            'I': np.array(self.simRes)[:, :, 2],
            'R': np.array(self.simRes)[:, :, 3],
            'actions': np.array(self.actions),
            'Incidence': np.array(self.incidence)
        }

        return results

    def get_metadata(self):
        metadata = {
            'epidemic_params': self.epidemic_params,
            'mobility': self.mobility,
            'population': self.population,
            'initial_infected': self.initial_infected,
            'sim_days': self.sim_days
        }
        return metadata

    def save_results(self, results, filename):
        import pickle
        metadata = self.get_metadata()
        
        data = {
            'metadata': metadata,
            'results': results
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)


# if __name__ == '__main__':
#     epidemic_params = {
#         'beta' :   0.95,
#         'sigma':   0.33,
#         'gamma':   0.14,
#         'Pm':      0.40,
#         'si_mean': 4.00,
#         'si_std':  2.50
#     }

#     mobility = np.array([
#         [0, 0.1, 0.2],
#         [0.1, 0, 0.3],
#         [0.2, 0.3, 0]
#     ])

#     population = np.array([1000, 800, 600])
#     initial_infected = np.array([1, 0, 0])

#     sim_settings = {
#         'sim_days': 160
#     }

#     model = EpidemicModel(epidemic_params, mobility, population, initial_infected, sim_settings)
    
#     sim_results = model.simulate()
#     # model.save_results(sim_results, '../Output/epidemic_model_results.pkl')
