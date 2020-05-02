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
#from sklearn.datasets import make_moons

# TODO: Change data type of input generated to int

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

        print(f"[*] Specified size: {size}")
        print(f"[*] Number of instances to generate: {instances}")
        print(f"[*] Format of the filenames: {filenames}[size]_[instance].xlsx")

        print("\n[+] Generating instances...")
        generate(size, instances, filenames, min_value, max_value)
        print("\n[+] Done.")

    except ValueError:
        print ("[-] Error: something is wrong with the range. Perhaps low>=high ?")
        print("[*] REMINDER: '-m' stands for minimum value and '-M' stands for maximum value.")

    except:
        print("[*] Use 'instance_generator -h' to get information of use.")


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


def generate(size, instances, filenames, min_value, max_value):
    try:
        folder = f'{filenames}_instances'
        os.mkdir(folder)

    except FileExistsError as e:
        pass

    finally:
        for i in range(1, instances+1):
            # Generate float64 data
            # data = np.random.rand(size,2)

            # Generate int data
            data = np.random.randint(low=min_value, high=max_value, size=(size, 2))

            # Create excel file 
            filename = f'{filenames}{size}_{i}.xlsx'
            print(f"[+] Creating {filename}...")
            create_excel(folder, filename)
            
            # Write data on excel file
            print(f"[+] Writing data on {filename}...")
            write_excel(folder, filename, data)


def create_excel(folder, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = f"MCLP Instance data"
    wb.save(filename=f'{folder}/{filename}')


def write_excel(folder, filename, data):
    # Load excel file
    workbook = load_workbook(f'{folder}/{filename}')
    sheet = workbook.get_sheet_by_name("MCLP Instance data")
    sheet['A1'] = 'i'
    sheet['B1'] = 'x'
    sheet['C1'] = 'y'

    # Cast ndarray to list
    data = list(data)

    # Write data
    for row in range(sheet.max_row-1, len(data)):
        for column in range(4):
            # i:
            sheet.cell(row=row+2, column=1).value = row+1

            # x:
            sheet.cell(row=row+2, column=2).value = data[row][0]

            # y:
            sheet.cell(row=row+2, column=3).value = data[row][1]

    workbook.save(f'{folder}/{filename}')


if __name__ == '__main__':
    main()