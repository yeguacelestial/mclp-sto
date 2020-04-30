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

# TODO: Generate objective functions matrix

import numpy as np
import os
from os import listdir
from optparse import OptionParser
import time
import openpyxl
from openpyxl import load_workbook
from gurobipy import *

def main():
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
            print(f"[*] Working with instance {instance}...")
            file = f'{instances_directory}/{instance}'
            coordinates_list = read_data(file)
            print(coordinates_list)

    except NotADirectoryError as e:
        number_of_sites = int(options.sites)
        candidate_sites = int(options.candidate_sites)
        radius = float(options.radius)
        instance = options.directory

        print(f"[*] Working with instance {instance}...")
        coordinates_list = read_data(instance)

        # Create a copy of coordinates without index
        coordinates_xy = [] 
        for coordinate in coordinates_list:
            coordinates_xy.append(coordinate[1:])

        coordinates_list = coordinates_xy[:]

        # Solve MCLP
        mclp(coordinates_list, number_of_sites, radius, candidate_sites)

    except FileNotFoundError:
        print("[-] Error: File not found.")
    
    except TypeError:
        print("[-] Error: input couldn't be read.")

    except Exception as e:
        raise
        #print("[-] Error: something went wrong.")


def getInput():
    parser = OptionParser()
    parser.add_option("-c", "--sites",
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

    return sites_coordinates


def mclp(coordinates, S, radius, M):
    """
    SOLVE MCLP
    *Input:
        coord => Coordinates
        S => Number of sites to select
        radius => Service radius of each site
        M => Number of candidate sites (randomly generated inside the ConvexHull polygon)

    *Return:
        optimal_sites => Locations of K optimal sites, numpy array
        f => Value of objective function
    """
    # Start timer
    time_start = time.clock()

    # START OF CONSTRUCTIVE HEURISTIC

    # Generated candidate sites
    sites = generate_candidate_sites(coordinates, M)
    from numpy import array
    coordinates = array(coordinates)
    print(f"Dimension of coordinates: {coordinates.shape}")
    print(f"Dimension of sites: {sites.shape}")

    # Create I and J sets
    I_set = coordinates.shape[0]
    J_set = sites.shape[0]

    print(f'I set - Size of the instance: {I_set}')
    print(f'J set - Number of sites to be selected: {J_set}')

    # Create distance matrix
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(coordinates, sites, 'euclidean')

    # Generate boolean matrix for each candidate under radius
    mask1 = dist_matrix <= radius
    dist_matrix[mask1] = 1
    dist_matrix[~mask1] = 0

    # Build Model
    m = Model()

    # Add variables
    x = {}
    y = {}

    for i in range(I_set):
        y[i] = m.addVar(vtype=GRB.BINARY, name="y%d" % i)
    
    for j in range(J_set):
        x[j] = m.addVar(vtype=GRB.BINARY, name="x%d" % j)
    
    # Update model
    m.update()

    # Add constraints to the model
    m.addConstr(quicksum(x[j] for j in range(J_set)) == S)

    # END OF CONSTRUCTIVE HEURISTIC
    # End timer
    time_elapsed = time.clock() - time_start
    print(f"[*] Elapsed time: {time_elapsed}s")
    return


if __name__ == '__main__':
    main()