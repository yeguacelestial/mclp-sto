"""
MAXIMUM COVERING LOCATION PROBLEM - Constructive Heuristic and Local Search Heuristic
PROGRAM INPUT:
* Instance >> coord
* Number of sites to select >> S
* Service radius of each site >> radius
* Desired population to cover >> M
*********************************************
Greddy Adding Algorithm
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
Constructive Heuristic
        INPUT:
            * population_points
            * candidate_sites_points
            * number_sites_to_select
            * radius
            * instance_name
        OUTPUT:
            * Selected sites
            * Objective function (Population covered)

        ALGORITHM:
            1. Start with an empty solution
                selected_sites <== []

            2. Restrictions for adding a site to selected_sites:
                r1 <== site has nodes under radius == (1,0)
                r2 <== len(selected_sites) < number_sites_to_select == (1, 0)
                r3 <== current_covered_nodes < population_points == (1,0)

            3. Iterate candidate sites and compute covered nodes of each one
            
            4. Repeat step 3 while r2 or r3 are not true

            5. Return: selected_sites

            6. objF <== Compute objective function of selected_sites

            7. Return: objF
        
        PSEUDOCODE:
            selected_sites = []
            population_size = len(population_points)

            For site in candidate_sites:
                current_covered_nodes <== compute_covered_nodes(selected_sites)
                number_of_covered_nodes = len(current_covered_nodes)

                r1 = covered_nodes(boolean_matrix(site)) > 0
                r2 = len(selected_sites) < number_sites_to_select
                r3 = number_of_covered_nodes < population_size

                if r1 and r2 and r3 == True:
                    selected_sites.append(site)

                elif r1 == False:
                    pass

                else:
                    break
                
*********************************************
Local Search Heuristic
        INPUT:
            * CONSTRUCTIVE HEURISTIC Solution
                -> objF_value = Objective function value
                -> objF_sites = Objective function sites
            * free_sites = List of current free sites
            * sites_with_objF = Dict of sites with their objective function

        OUTPUT:
            * LOCAL SEARCH Solution
                -> Objective function
                -> Objective function nodes
            * Computation time

        ALGORITHM:
            objF_copy = int(objF_value) <== int
            objF_sites_copy = objF_sites.copy() <== list 
            free_sites_copy = free_sites.copy() <== list
            sites_with_objF_copy = sites_with_objF.copy() <== dict

            for i, site in enumerate(objF_sites_copy):
                site_objF = sites_with_objF_copy[site]

                for free_site in free_sites_copy:
                    free_site_objF = sites_with_objF_copy[free_site]
                    
                    if free_site_objF > site_objF:
                        objF_sites_copy[i] = free_site

                    else:
                        pass
            
            new_sites_set => objF_sites_copy.copy()
            new_objF_value => compute population covered by new_sites_set

            if new_objF_value > objF_copy:
                return new_objF_value, new_sites_set
            else:
                print "Solution couldn't be improved"

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
*********************************************
"""

# TODO: Fix Local Search algorithm

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
        raise

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
    print(f"\n[*] Computing instance {instance_file}...")

    # Read input data
    data = read_data(instance_file)
    population_coordinates = data[0]
    candidate_sites_coordinates = data[1]


    # Start CH timer
    ch_time_start = time.clock()

    # Solve MCLP by CH (Constructive Heuristic)
    ch_data = mclp_ch(population_coordinates, candidate_sites_coordinates, number_of_sites, radius, instance_file)

    # End CH timer
    ch_time_elapsed = time.clock() - ch_time_start
    print(f"[+] Constructive Heuristic execution time: {ch_time_elapsed}s")


    # Start LS timer
    ls_time_start = time.clock()

    # Solve MCLP by LS (Local Search)

    # Get input from CH
    objF_value = ch_data[0]
    objF_sites = ch_data[1]
    free_sites = ch_data[2]
    sites_with_objF = ch_data[3]

    ls_data = mclp_ls(objF_value, objF_sites, free_sites, sites_with_objF)

    # End LS timer
    ls_time_elapsed = time.clock() - ls_time_start
    print(f"[+] Local Search Heuristic execution time: {ls_time_elapsed}s")


    # Start GA timer
    ga_time_start = time.clock()

    # Solve MCLP by GA (Greedy Adding)
    #ga_data = mclp_ga(population_coordinates, candidate_sites_coordinates, number_of_sites, radius, instance_file)
    
    # End GA timer
    ga_time_elapsed = time.clock() - ga_time_start
    #print(f"[+] Greedy Adding algorithm execution time: {ga_time_elapsed}s")


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


def mclp_ga(population_points, candidate_sites_points, number_sites_to_select, radius, instance_name):
    print("\n[***] GREEDY ADDING ALGORITHM [***]")
    """
        INPUT
    """
    print("\n[+++] INPUT [+++]")

    # Assocciate index to each population coordinate
    print(f"[*] POPULATION POINTS => {len(population_points)}")
    print(f"[*] CANDIDATE SITES => {len(candidate_sites_points)}")
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
    # 1. Start with an empty solution
    selected_sites = []

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
        nodes_covered_by_site = len(sites_with_covered_nodes[site])

        if nodes_covered_by_site > 0:
            print(f"SITE {site+1} => {nodes_covered_by_site} nodes covered")
    
    # 5. Pick the site that covers most of the total population
    # Create dictionary with the sum of covered nodes
    sites_with_objective_function = {}
    for site in sites_with_covered_nodes:
        sites_with_objective_function[site] = len(sites_with_covered_nodes[site])
    sites_with_objective_function_copy = sites_with_objective_function.copy()

    """
    7. Repeat step 5, stop until
    (len(solution) == number_sites_to_select)
                   or
    (len(current_covered_nodes) == len(population_points))
    """
    print(f"[*] COVERED NODES BY ALL CANDIDATE SITES => {len(current_covered_nodes)}")

    loop_boolean_value = True
    while loop_boolean_value == True:
        # 5. Pick the site that covers most of the total population
        # Site whose objective function is the largest
        site_with_max_population = max(sites_with_objective_function, key = lambda k: sites_with_objective_function[k])

        # 6. Add_site_with_max_population to solution, and remove it from sites_with_objective_function
        selected_sites.append(site_with_max_population)
        sites_with_objective_function.pop(site_with_max_population)

        # Constraint
        if (len(selected_sites) == number_sites_to_select) or (len(current_covered_nodes) == len(population_points)):
            loop_boolean_value = False

    # Compute objective function (covered population)
    objective_function = 0
    for site in selected_sites:
        objective_function += sites_with_objective_function_copy[site]

    # Filter free sites (With Excel index)
    free_sites = []
    for site in sites_with_objective_function:
        free_sites.append(site+1)

    """
        OUTPUT
    """
    print("\n[+++] OUTPUT [+++]")

    # Solution - Selected sites (Display Excel instances nodes)
    selected_sites_excel_instance = [site+1 for site in selected_sites]
    print(f"[+] SOLUTION - SELECTED SITES => {selected_sites_excel_instance}")

    # Free sites
    print(f"[+] FREE SITES => {free_sites}")

    # Solution - Covered population
    print(f"[+] SOLUTION - OBJECTIVE FUNCTION (COVERED POPULATION) => {objective_function}")

    return


def mclp_ch(population_points, candidate_sites_points, number_sites_to_select, radius, instance_name):
    print("\n[***] CONSTRUCTIVE HEURISTIC ALGORITHM [***]")
    """
        INPUT
    """
    print("\n[+++] INPUT [+++]")

    # Assocciate index to each population coordinate
    print(f"[*] POPULATION POINTS => {len(population_points)}")
    print(f"[*] CANDIDATE SITES => {len(candidate_sites_points)}")
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
    # Compute distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(population_points, candidate_sites_points, 'euclidean').astype(int)
    
    # Compute boolean matrix
    boolean_matrix = dist_matrix.copy()
    constraint1 = dist_matrix <= radius # Validates if demand point 'i' is under radius of site 'j'
    boolean_matrix[constraint1] = 1 # Stores boolean 'True' if demand point 'i' is under radius of site 'j'
    boolean_matrix[~constraint1] = 0 # Stores boolean 'False' if demand point 'i' is NOT under radius of site 'j'
    
    # Compute INDIVIDUAL covered nodes by each site in boolean matrix
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
        nodes_covered_by_site = len(sites_with_covered_nodes[site])
        
        if nodes_covered_by_site > 0:
            print(f"SITE {site+1} => {nodes_covered_by_site} nodes covered")

    # Start with an empty solution
    selected_sites = []
    population_size = len(population_points)
    free_sites = sites_with_covered_nodes.copy()

    # Iterate until a feasible solution is found
    for site in sites_with_covered_nodes:
        current_covered_nodes = []
        total_covered_nodes = sum(current_covered_nodes)

        # Constraints
        c1 = len(sites_with_covered_nodes[site]) > 0
        c2 = len(selected_sites) < number_sites_to_select
        c3 = total_covered_nodes < population_size

        if (c1 and c2 and c3) == True:
            current_covered_nodes.append(sites_with_covered_nodes[site])
            selected_sites.append(site)
            free_sites.pop(site)
        elif c1 == False:
            pass
        else:
            break

    # Create dictionary with the sum of covered nodes
    sites_with_objective_function = {}
    for site in sites_with_covered_nodes:
        sites_with_objective_function[site] = len(sites_with_covered_nodes[site])

    # Compute objective function
    objective_function = 0
    for site in selected_sites:
        objective_function += sites_with_objective_function[site]

    # Create selected sites Excel copy
    selected_sites_excel_copy = [site+1 for site in selected_sites]
    
    # Create free sites indexes copy
    free_sites_copy = []
    for site in free_sites:
        free_sites_copy.append(site)

    # Create free sites Excel copy
    free_sites_excel_copy = []
    for site in free_sites:
        free_sites_excel_copy.append(site+1)

    """
        OUTPUT
    """
    print("\n[+++] OUTPUT [+++]")
    print(f"[+] SELECTED SITES => {selected_sites_excel_copy}")
    print(f"[+] FREE SITES => {free_sites_excel_copy}")
    print(f"[+] OBJECTIVE FUNCTION (Covered population/points) => {objective_function}")

    return objective_function, selected_sites, free_sites_copy, sites_with_objective_function


def mclp_ls(objF_value, objF_sites, free_sites, sites_with_objF):
    print("\n[*] *** LOCAL SEARCH HEURISTIC ***")
    print(f"[*] Current objective function = {objF_value}")
    """
        INPUT
    """
    objF_copy = int(objF_value)
    objF_sites_copy = objF_sites.copy()
    free_sites_copy = free_sites.copy()
    sites_with_objF_copy = sites_with_objF.copy()

    """
        ALGORITHM
    """
    

    """
        OUTPUT
    """
    return


if __name__ == '__main__':
    main()