SIMPLINET
This repository contains the code for simplifying population flow networks using geographic adjacency constraints and a dynamic transmission model. The method improves epidemic simulation accuracy while reducing computational complexity, tested on Shenzhen's 1km grid-level network.

Directory Structure
Data/: Stores the raw data files used for analysis and modeling, such as flow matrices and population data.
GISData/: Contains Geographic Information System (GIS) data files, such as geographic boundary files and raster data, used for spatial analysis. All shapefiles in this directory are in the WGS84 coordinate system.
Output/: Stores all output results from analysis and model runs, including clustering results, flow matrix history, and Rt calculation results.
Source/: Contains all the source code files used to perform epidemic modeling, simulation, data processing, and analysis. 

Source Directory Code Files

1. ConstrainedAgglomerativeClustering.py
   Implements a constrained agglomerative hierarchical clustering algorithm. The code merges clusters iteratively while updating the flow matrix, forming a hierarchical cluster tree and recording the merging process.
2. EpidemicModel.py
   Implements an epidemic model, used to simulate the spread of a disease across different regions or populations and evaluate the effectiveness of various control strategies.
3. MatrixCalculatorAdjacency.py
   Calculates the adjacency matrix, determining the connections between regions or nodes based on geographic location or other features.
4. MatrixCalculatorSimilarity.py
   Calculates the similarity matrix, measuring the similarity between different nodes or regions, typically used in clustering analysis.
5. RtCalculator.py
   Uses multithreading to calculate the real-time reproduction number (Rt) for each grid area and calls RtCalculator.R to perform the actual computation.
6. RtCalculator.R
   A script written in R, used to calculate the real-time reproduction number (Rt), which is a key indicator of the transmission potential of an infectious disease.
7. RunEpidemicSimulation.py
   The main script that integrates and calls other modules to run the full epidemic simulation process, generating simulation results.

Running Steps

1. Calculate Matrices:
   Run MatrixCalculatorAdjacency.py to generate the adjacency matrix.
   Run MatrixCalculatorSimilarity.py to generate the similarity matrix.
2. Run Epidemic Simulation:
   Run RunEpidemicSimulation.py to simulate the spread of the epidemic using the clustering results and Rt values, and generate final output files.
3. Calculate Rt Values:
   Run RtCalculator.py to compute the real-time reproduction number (Rt) for each grid. This script will invoke the RtCalculator.R script to perform the calculation.
4. Perform Clustering:
   Run ConstrainedAgglomerativeClustering.py to perform hierarchical clustering based on the calculated matrices. This will also update and save the flow matrix history.
