"""
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
"""

# TODO: Code Local Search Heuristic

import colorama
from colorama import Fore, Back, Style
import numpy as np
import os
from os import listdir
from optparse import OptionParser
import time
import openpyxl
from openpyxl import load_workbook
from gurobipy import *

def main():
    colorama.init()

    # Get input
    get_input = getInput()
    options = get_input[0]
    arguments = get_input[1]

    # Instances directory
    try:
        instances_directory = options.directory
        candidate_sites = int(options.candidate_sites)
        number_of_sites = int(options.sites)
        radius = float(options.radius)

        # Sort excel files by modified date
        instances_directory_list = sorted_ls(instances_directory)

        # Read each instance file
        for instance in instances_directory_list:
            # print(f"\n[*] Computing instance {instance}...\n")
            # print("")
            file = f'{instances_directory}/{instance}'
            coordinates_list = read_data(file)
            
            # Create a copy of coordinates without index
            coordinates_xy = [] 
            for coordinate in coordinates_list:
                coordinates_xy.append(coordinate[1:])

            coordinates_list = coordinates_xy[:]

            # Solve MCLP
            mclp(coordinates_list, number_of_sites, radius, candidate_sites, instance)
            
    # Single file
    except NotADirectoryError as e:
        number_of_sites = int(options.sites)
        candidate_sites = int(options.candidate_sites)
        radius = float(options.radius)
        instance = options.directory

        coordinates_list = read_data(instance)

        # Create a copy of coordinates without index
        coordinates_xy = [] 
        for coordinate in coordinates_list:
            coordinates_xy.append(coordinate[1:])

        coordinates_list = coordinates_xy[:]

        # Solve MCLP
        mclp(coordinates_list, number_of_sites, radius, candidate_sites, instance)

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
    parser.add_option("-c", "--candidate-sites",
                      dest="candidate_sites",
                      help="INT value - Number of candidate sites to generate.")
    parser.add_option("-s", "--select-sites",
                      dest="sites",
                      help="INT value - Number of sites to select.")
    parser.add_option("-r", "--radius",
                      dest="radius",
                      help="FLOAT value - Service radius of each size")
    parser.add_option("-d", "--directory",
                      dest="directory",
                      help="STRING value - Folder or file name of the instances to compute")
    (options, args) = parser.parse_args()

    return options, args


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


def read_data(file):
    workbook = load_workbook(f'{file}')
    sheet = workbook.active
    
    i_column = sheet['A']
    x_column = sheet['B']
    y_column = sheet['C']

    # Get i, x and y from each row
    coordinates_list = []

    for row in sheet.iter_rows(min_row=sheet.min_row+1, max_row=sheet.max_row):
        coordinates_list.append((row[0].value,row[1].value,row[2].value))
    
    return coordinates_list


def generate_candidate_sites(coordinates, S):
    """
    Generate candidate sites inside a convex hull of given coordinates
    INPUT:
      coordinates => List of coordinates to work on
      S => Number of sites to generate
    RETURN:
      candidate_sites list
    """

    # From array to numpy array
    coordinates = np.array(coordinates)

    # Create convex hull
    from scipy.spatial import ConvexHull
    hull = ConvexHull(coordinates)

    # Create polygon points
    polygon_points = coordinates[hull.vertices]
    from shapely.geometry import Polygon
    poly = Polygon(polygon_points)

    # Min and max coordinates bounds
    min_x, min_y, max_x, max_y = poly.bounds

    # Generate candidate sites
    from shapely.geometry import Point
    from numpy import random

    sites = []
    while len(sites) < S:
        random_point = Point([random.uniform(min_x, max_x),
                              random.uniform(min_y,max_y)])
        if (random_point.within(poly)):
            sites.append(random_point)

    sites_coordinates = np.array([(site.x,site.y) for site in sites])
    sites_coordinates = sites_coordinates.astype(int)

    return sites_coordinates


def mclp(coordinates, S, radius, M, instance_name):
    """
    SOLVE MCLP
    *Input:
        coord => Coordinates
        S => Number of sites to select
        radius => Service radius of each site
        M => Number of candidate sites (randomly generated inside the ConvexHull polygon)

    *Return:
        opt_sites => Locations of K optimal sites, numpy array
        objective => Value of objective function
    """
    # Start timer
    time_start = time.clock()

    # START OF CONSTRUCTIVE HEURISTIC
    # Build Model
    m = Model()

    # Delete lines generated by Gurobipy
    for line in range(2):
        delete_last_line()

    # Generated candidate sites
    sites = generate_candidate_sites(coordinates, M)
    from numpy import array
    coordinates = array(coordinates)

    # Create I and J sets
    I_set = coordinates.shape[0]
    J_set = sites.shape[0]

    print(f"\n[*] Computing instance {instance_name}...")
    print(f'I set - Size of the instance: {I_set}')
    print(f'J set - Number of sites to be selected: {J_set}')

    # Create distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(coordinates, sites, 'euclidean').astype(int)
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
        opt_sites = sites[solution]

        return opt_sites, objective

    except:
        print("[-] Error: this problem is infeasible.\n\n")


def delete_last_line():
    import sys
    "Delete last line in STDOUT"

    # CURSOR UP ONE LINE
    sys.stdout.write('\x1b[1A')

    # DELETE LAST LINE
    sys.stdout.write('\x1b[2K')


if __name__ == '__main__':
    main()