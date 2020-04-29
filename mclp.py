# INPUT:
# * Instance >> coord
# * Number of sites to select >> S
# * Service radius of each site >> radius
# * Desired population to cover >> M
#
# OUTPUT:
# * Objective function of Constructive Heuristic -> Total of the population covered
# * Execution time of the Constructive Heuristic -> cpu_sec_ch
# * Objective function of Local Search Heuristic -> Total of the population covered IMPROVED
# * Execution time of the Local Search Heuristic -> cpu_sec_ls

# TODO: Generate objective functions matrix
# TODO: Constructive Heuristic:
#           * Create empty solution -> sites = [] 
#           * Generate all candidate sites under specified radius
#           * Evaluate objective function of these sites -> sites_OF = [of-1, of-2,...,of-n]
#           * for site in range(sites):
#               if M covered is greater than 0:
#                   Pick the site with the MAX objective function, and add to solution -> sites.append(max_of(site))
#               else:
#                   end for loop
#           * Return sites

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
        instances_directory_list = sorted_ls(instances_directory)

        # Read each instance file
        for instance in instances_directory_list:
            print(f"[*] Working with instance {instance}...")
            file = f'{instances_directory}/{instance}'
            coordinates_list = read_data(file)
            print(coordinates_list)

    except NotADirectoryError as e:
        instance = options.directory
        print(f"[*] Working with instance {instance}...")
        coordinates_list = read_data(instance)
        print(coordinates_list)
    
    except FileNotFoundError:
        print("[-] Error: File not found.")


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

    print(coordinates_list)

    return coordinates_list


def generate_sites(coordinates, S):
    # coordinates => List of coordinates to work on
    # S => Number of sites to generate

    return

def mclp(coord, S, radius, M):
    # coord => Coordinates
    # S => Number of sites to select
    # radius => Service radius of each site
    # M => Desired population to cover
    
    return


if __name__ == '__main__':
    main()