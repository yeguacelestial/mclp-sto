# INPUT:
# * Size of each instance -> size
# * Number of instances to generate -> instances
# OUTPUT:
# * Fixed sets generated in an Excel file

# points -> ([x1,y1], [x2,y2], [x3,y3]...[xn,yn])

import os
from openpyxl import Workbook
from openpyxl import load_workbook
import numpy as np
from optparse import OptionParser

import pandas as pd

# TODO: Migrate from openpyxl to Pandas
# TODO: New input - Set of candidate sites

def main():
    get_input = getInput()

    options = get_input[0]
    arguments = get_input[1]
    
    try:
        size = int(options.size)
        instances = int(options.instances)
        filenames = options.filenames
        min_value = int(options.min_value)
        max_value = int(options.max_value)
        number_candidate_sites = options.candidate_sites

        print(f"[*] Specified size: {size}")
        print(f"[*] Number of instances to generate: {instances}")
        print(f"[*] Format of the filenames: {filenames}[size]_[instance].xlsx")

        print("\n[+] Generating instances...")
        generate(size, instances, filenames, min_value, max_value, number_candidate_sites)
        print("\n[+] Done.")

    except ValueError:
        print ("[-] Error: something is wrong with the range. Perhaps low>=high ?")
        print("[*] REMINDER: '-m' stands for minimum value and '-M' stands for maximum value.")

    except:
        raise
        #print("[*] Use 'instance_generator -h' to get information of use.")


def getInput():
    parser = OptionParser()
    parser.add_option("-s", "--size",
                      dest="size",
                      help="INT value - Size of population to generate on instance/instances.",
                      type=int)
    parser.add_option("-m", "--min-value",
                      dest="min_value",
                      help="INT value - Minimum value to be generated on instance/instances.",
                      type=int)
    parser.add_option("-M", "--max-value",
                      dest="max_value",
                      help="INT value - Maximum value to be generated on instance/instances.",
                      type=int)
    parser.add_option("-c", "--candidate-sites",
                      dest="candidate_sites",
                      help="INT value - Number of candidate sites to generate.",
                      type=int)
    parser.add_option("-i", "--instances",
                      dest="instances",
                      help="INT value - Number of instances to generate.",
                      type=int)
    parser.add_option("-f", "--filenames",
                      dest="filenames",
                      help="String value - Name of the instances",
                      type=str)
    (options, args) = parser.parse_args()

    return options, args


def generate(size, instances, filenames, min_value, max_value, number_candidate_sites):
    try:
        folder = f'{filenames}_instances'
        os.mkdir(folder)

    except FileExistsError as e:
        pass

    finally:
        for i in range(1, instances+1):
            # Create excel file 
            filename = f'{filenames}{size}_{i}.xlsx'
            print(f"[+] Creating {filename}...")
            writer = pd.ExcelWriter(f'{folder}/{filename}', engine='xlsxwriter')
            
            # Generate and write population data on excel file
            print(f"[+] Generating and writing population data on {filename}...")
            data_population = np.random.randint(low=min_value, high=max_value, size=(size, 2))
            data_population_x = [coord[0] for coord in data_population]
            data_population_y = [coord[1] for coord in data_population]

            df = pd.DataFrame({'x': data_population_x, 'y': data_population_y})
            df.index += 1
            df.to_excel(writer, sheet_name='Population nodes')
            writer.save()

            # Generate and write candidate sites data on excel file
            print(f"[+] Writing candidate sites data on {filename}...")
            data_candidate_sites = generate_candidate_sites(data_population, number_candidate_sites)
            #write_excel(folder, filename, data_candidate_sites, col1, col2, col3, col1_name, col2_name, col3_name)


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


def write_excel(folder, filename, data, col1, col2, col3, col1_name, col2_name, col3_name):
    # Load excel file
    workbook = load_workbook(f'{folder}/{filename}')
    sheet = workbook.get_sheet_by_name("MCLP Instance data")
    sheet[f'{col1}1'] = col1_name
    sheet[f'{col2}1'] = col2_name
    sheet[f'{col3}1'] = col3_name

    # Cast ndarray to list
    data = list(data)

    # Write data
    for row in range(sheet.max_row-1, len(data)):
        for column in range(4):
            # First column enumerate:
            sheet.cell(row=row+2, column=1).value = row+1

            # x:
            sheet.cell(row=row+2, column=2).value = data[row][0]

            # y:
            sheet.cell(row=row+2, column=3).value = data[row][1]

    workbook.save(f'{folder}/{filename}')


if __name__ == '__main__':
    main()