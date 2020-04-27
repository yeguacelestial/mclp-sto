# INPUT:
# * Size of each instance -> size
# * Number of instances to generate -> instances
# OUTPUT:
# * Fixed sets generated in an Excel file

# points -> ([x1,y1], [x2,y2], [x3,y3]...[xn,yn])

#   TODO: Generate Excel files in generate() function

import os
from openpyxl import Workbook
import numpy as np
from optparse import OptionParser
from sklearn.datasets import make_moons

def main():
    get_input = getInput()

    options = get_input[0]
    arguments = get_input[1]
    
    try:
        size = int(options.size)
        instances = int(options.instances)
        filenames = options.filenames

        print(options)
        print(arguments)

        print(f"Specified size: {size}")
        print(f"Number of instances to generate: {instances}")
        print(f"Filenames: {filenames}")

        points = np.random.rand(size,2)
        generate(size, instances, filenames)

    except:
        raise
        #print("Use 'instance_generator -h' to get information of use.")


def getInput():
    parser = OptionParser()
    parser.add_option("-s", "--size",
                      dest="size",
                      help="INT value - Size of population to generate on each instance.")
    parser.add_option("-i", "--instances",
                      dest="instances",
                      help="INT value - Number of instances to generate.")
    parser.add_option("-f", "--filenames",
                      dest="filenames",
                      help="String value - Name of the instances")
    (options, args) = parser.parse_args()

    return options, args


def generate(size, instances, filenames):
    try:
        os.mkdir('instances')

    except FileExistsError as e:
        pass

    finally:
        create_excel(filenames)


def create_excel(name):
    wb = Workbook()
    ws = wb.active
    ws.title = "MCLP Instance data"
    wb.save(filename=f'instances\{name}.xlsx')
    wb.save(filename=f'instances\{name}2.xlsx')


if __name__ == '__main__':
    main()