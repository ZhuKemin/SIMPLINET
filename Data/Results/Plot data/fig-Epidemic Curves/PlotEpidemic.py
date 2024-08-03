import numpy as np
import matplotlib.pyplot as plt

config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 24,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",}
plt.rcParams.update(config)


# Load the SEIR data and population data
fn = './simRes_3d.npy'
data = np.load(fn)
population = np.load('population.npy')

# Normalize SEIR data by population
population = population.reshape(1, -1, 1)  # Reshape population for broadcasting
data_normalized = 100 * data / population

# Calculate the total population
total_population = np.sum(population)

# Calculate the overall SEIR proportions by summing across all spatial units and dividing by total population
overall_seir = 100 * np.sum(data, axis=1) / total_population

# Extract the shape of the data
days, units, compartments = data_normalized.shape

# SEIR colors and labels
colors = ['gray', 'yellow', 'red', 'green']
labels = ['S', 'E', 'I', 'R']

# Plotting overall SEIR proportions
plt.figure(figsize=(15, 10))

for j in range(compartments):
    plt.plot(range(days), overall_seir[:, j], color=colors[j], label=f'Overall {labels[j]}')

    # Plotting the fill_between for each spatial unit
    plt.fill_between(range(days), 
                     np.min(data_normalized[:, :, j], axis=1), 
                     np.max(data_normalized[:, :, j], axis=1), 
                     color=colors[j], alpha=0.3)

# Adding labels and title
plt.xlabel('Simulation Days')
plt.ylabel('Proportion of Population (%)')

# Adding legend
handles = [plt.Line2D([0], [0], color=colors[j], lw=4) for j in range(compartments)]
handles += [plt.Line2D([0], [0], color=colors[j], lw=4, alpha=0.3) for j in range(compartments)]
labels = [f'City-level Overall {label}' for label in labels] + [f'Grid-level {label} range' for label in labels]
plt.legend(handles, labels, loc='center right')
plt.xlim(0, 100)
plt.ylim(0, 100)


# Show the plot
plt.grid(ls="-.", lw=0.6, color='gray')

# plt.savefig('SEIR_Proportions_and_Range_All_Spatial_Units.png')
plt.show()
