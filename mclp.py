"""
MAXIMUM COVERING LOCATION PROBLEM - Constructive Heuristic and Local Search Heuristic
*** INPUT:
* Instance >> coord
* Number of sites to select >> S
* Service radius of each site >> radius
* Desired population to cover >> M
*********************************************
*** Constructive Heuristic:
          * Create empty solution -> sites = [] 
          * Generate all candidate sites under specified radius
          * Evaluate objective function of these sites -> sites_OF = [of-1, of-2,...,of-n]
          * for site in range(sites):
              if M covered is greater than 0:
                  Pick the site with the MAX objective function, and add to solution -> sites.append(max_of(site))
              else:
                  end for loop
          * Return sites
*********************************************
*** OUTPUT:
* Objective function of Constructive Heuristic -> Total of the population covered
* Execution time of the Constructive Heuristic -> cpu_sec_ch
* Objective function of Local Search Heuristic -> Total of the population covered IMPROVED
* Execution time of the Local Search Heuristic -> cpu_sec_ls
*********************************************
NOTE: Euclidean distance => AC = sqrt(AB² + BC²) = sqrt( (x2 - x1)² + (y2 - y1)² )
*********************************************
NOTE: About Local Search approach: Okay. You already have the candidate sites of an specific instance. The Greddy Adding with Substitution Algorithm iterate each "free" site and compares the objective function (population covered by that site) it to a site inside the given solution. That could work. Remember. Local Search seeks to improve a given solution by making small movements on it.  
"""
# TODO: Code Local Search Heuristic

import colorama
import numpy as np
import openpyxl
import os
import pandas as pd
import time

from colorama import Fore, Back, Style
from gurobipy import *
from openpyxl import load_workbook
from os import listdir
from optparse import OptionParser


def main():
    colorama.init()

    # Get input
    get_input = getInput()
    options = get_input[0]
    arguments = get_input[1]

    options_dict = vars(options)
    options_values = options_dict.values()

    if None in options_values:
        print("[*] Use 'instance_generator -h' to get information of use.")
        exit()
    
    instances_directory = options.directory
    number_of_sites = options.sites
    radius = options.radius

    # Instances directory
    try:
        # Sort excel files by modified date
        instances_directory_list = sorted_ls(instances_directory)

        # Read each instance file
        for instance in instances_directory_list:
            instance_file = f'{instances_directory}/{instance}'
            data = read_data(instance_file)

            population_coordinates = data[0]
            candidate_sites_coordinates = data[1]

            # Solve MCLP
            mclp(population_coordinates, candidate_sites_coordinates, number_of_sites, radius, instance_file)
            
    # Single file
    except NotADirectoryError as e:
        instance_file = f'{instances_directory}'
        data = read_data(instance_file)

        population_coordinates = data[0]
        candidate_sites_coordinates = data[1]

        # Solve MCLP
        mclp(population_coordinates, candidate_sites_coordinates, number_of_sites, radius, instance_file)

    except FileNotFoundError:
        print("[-] Error: File not found.")
    
    except TypeError:
        print(Fore.RED + "[-] Error: input couldn't be read." + Style.RESET_ALL)
        print(Fore.YELLOW + "[*] Use 'mclp.py -h' for usage info." + Style.RESET_ALL)

    except Exception as e:
        raise
        #print("[-] Error: something went wrong.")


def getInput():
    parser = OptionParser()
    parser.add_option("-s", "--select-sites",
                      dest="sites",
                      help="INT value - Number of sites to select.",
                      type=int)
    parser.add_option("-r", "--radius",
                      dest="radius",
                      help="INT value - Service radius of each site.",
                      type=int)
    parser.add_option("-d", "--directory",
                      dest="directory",
                      help="STRING value - Folder or file name of the instances to compute.",
                      type=str)
    (options, args) = parser.parse_args()

    return options, args


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


def read_data(file):
    # Read population nodes
    population_df = pd.read_excel(f'{file}', sheet_name="Population")
    population_x = population_df['x'].tolist()
    population_y = population_df['y'].tolist()

    population_coordinates = list(zip(population_x, population_y))

    # Read candidate sites nodes
    candidate_sites_df = pd.read_excel(f'{file}', sheet_name="Candidate sites")
    candidate_sites_x = candidate_sites_df['x'].tolist()
    candidate_sites_y = candidate_sites_df['y'].tolist()
    
    candidate_sites_coordinates = list(zip(candidate_sites_x, candidate_sites_y))

    return population_coordinates, candidate_sites_coordinates


def mclp(population_coordinates, candidate_sites_coordinates, S, radius, instance_name):
    """
    SOLVE MCLP
    *Input:
        population_coordinates => Coordinates of population nodes
        candidate_sites_coordinates => Coordinates of free candidate sites
        S => Number of sites to be selected
        radius => Service radius of each site
        instance_name => Instance filename

    *Return:
        opt_sites => Locations of K optimal sites, numpy array
        objective => Value of objective function
    """

    # Start timer
    time_start = time.clock()

    # START OF CONSTRUCTIVE HEURISTIC
    print(f"\n[+] Computing instance {instance_name}...")

    # Build Model
    m = Model()

    # Delete lines generated by Gurobipy
    for line in range(2):
        delete_last_line()

    # Cast population and candidates sites arrays to numpy arrays
    from numpy import array
    population_coordinates = array(population_coordinates)
    candidate_sites_coordinates = array(candidate_sites_coordinates)

    # Create I and J sets
    I_set = population_coordinates.shape[0]
    J_set = candidate_sites_coordinates.shape[0]

    print(f'[*] Size of the instance (Population): {I_set}')
    print(f'[*] Number of free sites: {J_set}')
    print(f'[*] Number of sites to be selected: {S}')

    print(f"[*] Coordinates: \n{population_coordinates}")
    print(f"[*] Candidate sites:\n {candidate_sites_coordinates}")

    # Create distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(population_coordinates, candidate_sites_coordinates, 'euclidean').astype(int)
    print("[*] Distance matrix: ")
    print(dist_matrix)

    # Generate boolean matrix for each candidate under radius
    mask1 = dist_matrix <= radius
    dist_matrix[mask1] = 1  # Stores '1' if dist_matrix value is less than radius
    dist_matrix[~mask1] = 0 # Stores '0' if dist_matrix value is greater than radius
        
    # Add variables
    x = {}
    y = {}

    for i in range(I_set):
        y[i] = m.addVar(vtype=GRB.BINARY, name=f"y{i}")
    
    for j in range(J_set):
        x[j] = m.addVar(vtype=GRB.BINARY, name=f"x{j}")
    
    # Update model
    m.update()

    # Add constraints to the model
    m.addConstr(quicksum(x[j] for j in range(J_set)) == S)

    for i in range(I_set):
        m.addConstr(quicksum(x[j] for j in np.where(dist_matrix[i]==1)[0]) >= y[i])
    
    # Set objective function on the model
    m.setObjective(quicksum(y[i] for i in range(I_set)), GRB.MAXIMIZE)

    m.setParam('OutputFlag', 0)
    m.optimize()
    # END OF COMPUTATION OF CONSTRUCTIVE HEURISTIC

    try:
        # End timer
        time_elapsed = time.clock() - time_start
        objective = m.objVal

        # If objective function is less or equal than 0:
        if objective <= 0: 
            objective = 0
            print("[-] Couldn't maximize this instance.")

        # OUTPUT
        print(f"[+] Objective Function - Population covered: {objective}")
        print(f"[+] Execution time: {time_elapsed}s\n")

        # Get solution data
        solution = []
        if m.status == GRB.Status.OPTIMAL:
            for v in m.getVars():
                if v.x==1 and v.varName[0]=="x":
                    solution.append(int(v.varName[1:]))
        opt_sites = candidate_sites_coordinates[solution]

        print(f"[*] Chosen sites:\n {opt_sites}")
        print(f"[*] Solution set: {solution}")

        return opt_sites, objective

    except:
        raise
        #print("[-] Error: this problem is infeasible.\n\n")


def delete_last_line():
    import sys
    "Delete last line in STDOUT"

    # CURSOR UP ONE LINE
    sys.stdout.write('\x1b[1A')

    # DELETE LAST LINE
    sys.stdout.write('\x1b[2K')


if __name__ == '__main__':
    main()