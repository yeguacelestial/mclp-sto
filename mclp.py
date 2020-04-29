# *** INPUT:
# * Instance >> coord
# * Number of sites to select >> S
# * Service radius of each site >> radius
# * Desired population to cover >> M
# *********************************************
# *** Constructive Heuristic:
#           * Create empty solution -> sites = [] 
#           * Generate all candidate sites under specified radius
#           * Evaluate objective function of these sites -> sites_OF = [of-1, of-2,...,of-n]
#           * for site in range(sites):
#               if M covered is greater than 0:
#                   Pick the site with the MAX objective function, and add to solution -> sites.append(max_of(site))
#               else:
#                   end for loop
#           * Return sites
# *********************************************
# *** OUTPUT:
# * Objective function of Constructive Heuristic -> Total of the population covered
# * Execution time of the Constructive Heuristic -> cpu_sec_ch
# * Objective function of Local Search Heuristic -> Total of the population covered IMPROVED
# * Execution time of the Local Search Heuristic -> cpu_sec_ls

# TODO: Generate objective functions matrix

import numpy as np
import os
from os import listdir
from optparse import OptionParser
import time
import openpyxl
from openpyxl import load_workbook


def main():
    time_start = time.clock()
    # START OF THE CODE

    # Get input
    get_input = getInput()
    options = get_input[0]
    arguments = get_input[1]

    # Instances directory
    try:
        instances_directory = options.directory
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
        radius = float(options.radius)
        instance = options.directory

        print(f"[*] Working with instance {instance}...")
        coordinates_list = read_data(instance)
        generate_candidate_sites(coordinates_list, radius)
    
    except FileNotFoundError:
        print("[-] Error: File not found.")
    
    except Exception as e:
        raise
        #print("[-] Error: something went wrong.")


    # END OF THE CODE
    time_elapsed = time.clock() - time_start
    print(f"[*] Elapsed time: {time_elapsed}s")


def getInput():
    parser = OptionParser()
    parser.add_option("-k", "--sites",
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
    # Generate candidate sites inside a convex hull of given coordinates
    # INPUT:
    #   coordinates => List of coordinates to work on
    #   S => Number of sites to generate
    # RETURN:
    #   candidate_sites list

    # Create a copy of coordinates without index
    coordinates_xy = [] 
    for coordinate in coordinates:
        coordinates_xy.append(coordinate[1:])

    coordinates = coordinates_xy[:]

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

    # Constructive heuristic
    sites = []
    while len(sites) < S:
        random_point = Point([random.uniform(min_x, max_x),
                              random.uniform(min_y,max_y)])
        if (random_point.within(poly)):
            sites.append(random_point)

    sites_coordinates = np.array([(site.x,site.y) for site in sites])
    print(sites_coordinates)
    return sites_coordinates

def mclp(coord, S, radius, M):
    # coord => Coordinates
    # S => Number of sites to select
    # radius => Service radius of each site
    # M => Desired population to cover
    
    return


if __name__ == '__main__':
    main()