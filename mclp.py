"""
MAXIMUM COVERING LOCATION PROBLEM - Constructive Heuristic and Local Search Heuristic
PROGRAM INPUT:
* Instance >> coord
* Number of sites to select >> S
* Service radius of each site >> radius
* Desired population to cover >> M
*********************************************
Constructive Heuristic:
    INPUT:
        * population_points
        * candidate_sites_points
        * number_sites_to_select
        * radius
        * instance_name

    ALGORITHM:
        1. Start with an empty solution
            solution <== []
            current_covered_nodes = []

        2. Compute distance matrix
            dist_matrix <== [Site 'j':[Distance from node 'i' in population_points to site 'j' in candidate_sites_points],...]
        
        3. Compute boolean matrix
            boolean_matrix <== [Site 'j':['i' nodes covered by site 'j'],...]
        
        4. Compute INDIVIDUAL covered nodes by each site in boolean matrix
            sites_with_covered_nodes = {}

            for site in boolean_matrix:
                site_covered_nodes = []

                for node in site:
                    if node not in current_covered_nodes:
                        site_covered_nodes.append(node)
                        current_covered_nodes.append(node)
                    else:
                        pass

                sites_with_covered_nodes[site] = site_covered_nodes

        5. Pick the site that covers most of the total population
            # Site whose objective function is the largest
            site_with_max_population = max(sites_with_covered_nodes, key = lambda k: sites_with_covered_nodes[k])
        
        6. Add site_with_max_population to solution, and remove it from sites_with_covered_nodes
            solution <== append(site_with_max_population)
            sites_with_covered_nodes <== remove(site_with_max_population)
        
        7. Repeat step 5, stop until 
            len(solution) === number_sites_to_select
                        or
            len(compute_covered_nodes(solution)[covered nodes]) === len(population_points)

*********************************************
Local Search Heuristic
        INPUT:
            * CONSTRUCTIVE HEURISTIC Solution
                -> Objective function
                -> Objective function nodes
            * FREE Candidate sites
            * Distance matrix
        OUTPUT:
            * LOCAL SEARCH Solution
                -> Objective function
                -> Objective function nodes
            * Computation time
        ALGORITHM:
            

*********************************************
PROGRAM OUTPUT:
* Objective function of Constructive Heuristic -> Total of the population covered
* Execution time of the Constructive Heuristic -> cpu_sec_ch
* Objective function of Local Search Heuristic -> Total of the population covered IMPROVED
* Execution time of the Local Search Heuristic -> cpu_sec_ls
*********************************************
NOTE: Euclidean distance => AC = sqrt(AB² + BC²) = sqrt( (x2 - x1)² + (y2 - y1)² )
*********************************************
NOTE: About Local Search approach: Okay. You already have the candidate sites of an specific instance. The Greddy Adding
with Substitution Algorithm iterate each "free" site and compares the objective function (population covered by that site)
to a site inside the given solution. That could work. Remember. Local Search seeks to improve a given solution
by making small movements on it.  
"""

# TODO: Refactor Constructive Heuristic

import colorama
import numpy as np
import openpyxl
import os
import pandas as pd
import time

from colorama import Fore, Back, Style
from gurobipy import *
from numpy import array
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
        print("[*] Use 'mclp.py -h' to get information of use.")
        exit()
    
    instances_directory = options.directory
    number_of_sites = options.sites
    radius = options.radius

    # Process multiple instances
    try:
        # Sort excel files by modified date
        instances_directory_list = sorted_ls(instances_directory)

        # Read each instance file
        for instance in instances_directory_list:
            instance_file = f'{instances_directory}/{instance}'

            # Solve MCLP - Constructive Heuristic
            mclp(number_of_sites, radius, instance_file)
        
        print("\n[+] Done.")
            
    # Process single file instance
    except NotADirectoryError as e:
        instance_file = f'{instances_directory}'

        # Solve MCLP
        mclp(number_of_sites, radius, instance_file)

        print("\n[+] Done.")

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


def mclp(number_of_sites, radius, instance_file):
    # Solve MCLP by CH (Constructive Heuristic)
    data = read_data(instance_file)
    population_coordinates = data[0]
    candidate_sites_coordinates = data[1]

    print(f"\n[*] Computing instance {instance_file}...")
    ch_data = mclp_ch_refactor(population_coordinates, candidate_sites_coordinates, number_of_sites, radius, instance_file)

    # objective_function_value = ch_data[0]
    # objective_function_coordinates = ch_data[1]
    # dist_matrix_copy = ch_data[2] 
    # free_candidate_sites = ch_data[3]
    # dist_matrix_boolean = ch_data[4]

    # Solve MCLP by LS (Local Search Heuristic)
    #mclp_ls(objective_function_value, objective_function_coordinates, dist_matrix_copy, free_candidate_sites, dist_matrix_boolean)


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


def mclp_ch_refactor(population_points, candidate_sites_points, number_sites_to_select, radius, instance_name):
    print("[***] CONSTRUCTIVE HEURISTIC [***]")
    """
        INPUT
    """
    # Assocciate index to each population coordinate
    print(f"[*] POPULATION POINTS:\n{population_points}")
    print(f"[*] CANDIDATE SITES COORDINATES:\n{candidate_sites_points}")
    print(f"[*] NUMBER OF SITES TO SELECT => {number_sites_to_select}")
    print(f"[*] RADIUS => {radius}")
    print(f"[*] INSTANCE NAME => {instance_name}")

    # Associate index to population points, starting from 1
    population_points_with_index = []
    for point in population_points:
        population_points_with_index.append((population_points.index(point)+1, point))
    
    # Associate index to candidate sites, starting from 1
    candidate_sites_points_with_index = []
    for point in candidate_sites_points:
        candidate_sites_points_with_index.append((candidate_sites_points.index(point),point))

    # Cast to numpy arrays
    population_points = array(population_points)
    candidate_sites_points = array(candidate_sites_points)
    
    # Size of I and J
    I_size = population_points.shape[0]
    J_size = candidate_sites_points.shape[0]

    
    """
        ALGORITHM
    """
    # Start timer
    time_start = time.clock()

    # 1. Start with an empty solution
    solution = []

    # 2. Compute distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(population_points, candidate_sites_points, 'euclidean').astype(int)
    
    # 3. Compute boolean matrix
    boolean_matrix = dist_matrix.copy()
    constraint1 = dist_matrix <= radius # Validates if demand point 'i' is under radius of site 'j'
    boolean_matrix[constraint1] = 1 # Stores boolean 'True' if demand point 'i' is under radius of site 'j'
    boolean_matrix[~constraint1] = 0 # Stores boolean 'False' if demand point 'i' is NOT under radius of site 'j'
    
    # 4. Compute INDIVIDUAL covered nodes by each site in boolean matrix
    current_covered_nodes = []
    sites_with_covered_nodes = {}

    # for site in boolean_matrix...
    for i, site in candidate_sites_points_with_index:
        site_all_covered_nodes = np.where(boolean_matrix[:,i] == True)[0]
        site_individual_covered_nodes = []

        # for node in site:
        for node in site_all_covered_nodes:
            if node not in current_covered_nodes:
                site_individual_covered_nodes.append(node)
                current_covered_nodes.append(node)
            else:
                pass

        sites_with_covered_nodes[i] = site_individual_covered_nodes
    
    for site in sites_with_covered_nodes:
        print(f"SITE {site} => {sites_with_covered_nodes[site]} nodes")
    
    # 5. Pick the site that covers most of the total population
    # Create dictionary with the sum of covered nodes
    sites_with_objective_function = {}
    for site in sites_with_covered_nodes:
        sites_with_objective_function[site] = len(sites_with_covered_nodes[site])

    # Site whose objective function is the largest
    site_with_max_population = max(sites_with_objective_function, key = lambda k: sites_with_objective_function[k])
    print(f"SITE WITH MAX POPULATION => SITE {site_with_max_population}")

    # 6. Add_site_with_max_population to solution, and remove it from sites_with_objective_function
    solution.append(site_with_max_population)
    sites_with_objective_function.pop(site_with_max_population)
    print(f"NEW DICT => {sites_with_objective_function}")
    print(f"SOLUTION => {solution}")
    """
        OUTPUT
    """
    print("[+++] OUTPUT [+++]")

    # End timer
    time_elapsed = time.clock() - time_start
    print(f"Execution time: {time_elapsed}s")
    return


def mclp_ch(population_coordinates, candidate_sites_coordinates, S, radius, instance_name):
    """
    SOLVE MCLP (CONSTRUCTIVE HEURISTIC)
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
    print("[*] *** CONSTRUCTIVE HEURISTIC ***")
    # Build Model
    m = Model()

    # Delete lines generated by Gurobipy
    # for line in range(2):
    #     delete_last_line()

    # Cast population and candidates sites arrays to numpy arrays
    population_coordinates = array(population_coordinates)
    candidate_sites_coordinates = array(candidate_sites_coordinates)

    # Create I and J sets
    I_set = population_coordinates.shape[0]
    J_set = candidate_sites_coordinates.shape[0]

    print(f'\n[*] Size of the instance (Population): {I_set}')
    print(f'\n[*] Radius: {radius}')
    print(f'[*] Number of free sites: {J_set}')
    print(f'[*] Number of sites to be selected: {S}')

    # Create distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(population_coordinates, candidate_sites_coordinates, 'euclidean').astype(int)
    dist_matrix_copy = dist_matrix.copy() # Create a copy of distance matrix values

    # Generate boolean matrix for each candidate under radius
    mask1 = dist_matrix <= radius
    dist_matrix[mask1] = 1  # Stores '1' if dist_matrix value is less than radius
    dist_matrix[~mask1] = 0 # Stores '0' if dist_matrix value is greater than radius
    dist_matrix_boolean = dist_matrix.copy()

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

        objective_function_value = int(m.objVal)
        # If objective function is less or equal than 0:
        if objective_function_value <= 0: 
            objective_function_value = 0
            print("[-] Couldn't maximize this instance.")

        # Get solution data
        solution = []
        if m.status == GRB.Status.OPTIMAL:
            for v in m.getVars():
                if v.x==1 and v.varName[0]=="x":
                    solution.append(int(v.varName[1:]))
        opt_sites = candidate_sites_coordinates[solution]

        # Fixed solution with nodes for Excel files (starting from index 1 instead of 0)
        solution_excel = []
        for node in solution:
            node += 1
            solution_excel.append(node)
        
        # OUTPUT
        print(f"\n[+] Objective Function - Population covered: {objective_function_value}")
        print(f"[+] Objective Function - Selected sites: {solution_excel}")
        print(f"[+] CH Execution time: {time_elapsed}s\n")

        # Filter free candidate sites
        free_candidate_sites = []
        candidate_sites_coordinates = candidate_sites_coordinates.tolist()
        for site in candidate_sites_coordinates:
            if site not in opt_sites:
                site_index = candidate_sites_coordinates.index(site)
                free_candidate_sites.append((site_index, site))

        # Associate fixed node with each coordinate
        objective_function_coordinates = list(zip(solution_excel, opt_sites))

        return objective_function_value, objective_function_coordinates, dist_matrix_copy, free_candidate_sites, dist_matrix_boolean

    except AttributeError:
        raise
        print("[-] Error: Problem is unfeasible.")
        exit()


def mclp_ls(objective_function_value, objective_function_coordinates, dist_matrix, free_candidate_sites, dist_matrix_boolean):
    """
        Local Search Heuristic
        INPUT:
            * CONSTRUCTIVE HEURISTIC Solution
                * objective_function_value ==> Objective function
                * objective_function_coordinates ==> Objective function nodes
            * free_candidate_sites ==> FREE Candidate sites
            * dist_matrix ==> Distance matrix

        OUTPUT:
            * LOCAL SEARCH Solution
                -> Objective function
                -> Objective function nodes
            * Computation time
            
    """
    print("\n[*] *** LOCAL SEARCH HEURISTIC ***")
    print(f"[*] Current objective function = {objective_function_value}")
   
    # Create input copies
    current_objF_value = int(objective_function_value)
    current_objF_nodes = objective_function_coordinates.copy()
    current_free_sites = free_candidate_sites.copy()

    # Create list of indexes for distance matrix
    current_objF_sites_indexes = [node[0]-1 for node in current_objF_nodes]
    #print(f"[*] Current objective function indexes (for dist matrix): {current_objF_sites_indexes}")

    # DEBUGGING
    current_objF_sites_indexes_excel = [node[0] for node in current_objF_nodes]
    current_free_sites_indexes_excel = [site[0]+1 for site in current_free_sites]
    print(f"[*] Selected sites: {current_objF_sites_indexes_excel}")
    print(f"[*] Free sites: {current_free_sites_indexes_excel}")
    # END DEBUGGING

    # Create list of indexes of FREE candidate sites for distance matrix
    current_free_sites_indexes = [site[0] for site in current_free_sites]
    #print(f"[*] Current free sites indexes (for dist matrix): {current_free_sites_indexes}")

    # START TIMER
    time_start = time.clock()

    # Algorithm
    # Compute OBJECTIVE FUNCTION and COVERED NODES of a given solution
    def compute_covered_nodes(solution):
        # Get covered nodes by current objective function
        covered_nodes = []
        for site in solution:
            # Stores each node that is covered by site
            covered_node_index = np.where(dist_matrix_boolean[:, site] == True)[0]
            for node in covered_node_index:
                covered_nodes.append(node)

        # Remove duplicated nodes
        covered_nodes = list(dict.fromkeys(covered_nodes))

        return covered_nodes, len(covered_nodes)

    covered_population_data = compute_covered_nodes(current_objF_sites_indexes)
    covered_population_nodes = covered_population_data[0]
    covered_population_objF = covered_population_data[1]

    # 
    print(f"\n[*] CURRENT COVERED POPULATION => {covered_population_nodes}")
    #print(f"[*] SITES INITIAL SET => {current_objF_sites_indexes}")

    current_sites_data = []
    for site in current_objF_sites_indexes:
        covered_population_by_site_data = compute_covered_nodes([site])
        nodes_covered = covered_population_by_site_data[0]
        objective = covered_population_by_site_data[1]

        current_sites_data.append((site, objective, nodes_covered))
        print(f"POPULATION COVERED BY SITE {site+1} => {objective}")
        print(f"NODES COVERED => {nodes_covered}\n")
    
    free_sites_data = []
    print(f"\n[*] FREE SITES INITIAL SET => {current_free_sites_indexes}")
    for site in current_free_sites_indexes:
        covered_population_by_site_data = compute_covered_nodes([site])
        nodes_covered = covered_population_by_site_data[0]
        objective = covered_population_by_site_data[1]

        free_sites_data.append((site, objective, nodes_covered))
        print(f"POPULATION COVERED BY FREE SITE {site} => {objective}")

    #print(f"[*] CURRENT SITES: {current_sites_data}")
    for i, site in enumerate(current_sites_data):
        current_site = site[0]
        current_site_objF = site[1]
        current_site_population = site[2]
        
        for free_i, fr_site in enumerate(free_sites_data):
            free_site = fr_site[0]
            free_site_objF = fr_site[1]
            free_site_population = fr_site[2]
            #print(f"MOVE({current_site},{free_site})")
            
            if free_site_objF > current_site_objF:
                current_sites_data[i] = free_site
                free_sites_data.pop(free_i)

    #print(f"[*] NEW SITES: {current_sites_data}")
    print(f"\nPOPULATION COVERED BY SITE 0 => {compute_covered_nodes([0])[0]}")
    print(f"\nPOPULATION COVERED BY SITE 2 => {compute_covered_nodes([2])[0]}")
    print(f"\nPOPULATION COVERED BY SITE 5 => {compute_covered_nodes([5])[0]}")
    print(f"\nPOPULATION COVERED BY SITE 7 => {compute_covered_nodes([7])[0]}")
    print(f"\nPOPULATION COVERED BY SITE 13 => {compute_covered_nodes([13])[0]}")

    print(f"\nPOPULATION COVERED BY FREE SITE 17 => {compute_covered_nodes([17])[0]}")

    # END TIMER
    time_elapsed = time.clock() - time_start
    print(f"\n[+] LS Execution Time: {time_elapsed}s")


def delete_last_line():
    import sys
    "Delete last line in STDOUT"

    # CURSOR UP ONE LINE
    sys.stdout.write('\x1b[1A')

    # DELETE LAST LINE
    sys.stdout.write('\x1b[2K')


if __name__ == '__main__':
    main()