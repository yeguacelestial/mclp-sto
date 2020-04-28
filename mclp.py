# INPUT:
# * Number of sites to select >> K
# * Service radius of each site >> radius
# * Candidate site size (Desired population to cover) >> M
#
# OUTPUT:
# * Objective function of Constructive Heuristic -> Total of the population covered
# * Execution time of the Constructive Heuristic -> cpu_sec_ch
# * Objective function of Local Search Heuristic -> Total of the population covered IMPROVED
# * Execution time of the Local Search Heuristic -> cpu_sec_ls

# TODO: Process each instance generated

import os
from os import listdir
from pathlib import Path
import time
from optparse import OptionParser


def main():
    time_start = time.clock()
    # START OF THE CODE

    # Get input
    get_input = getInput()
    options = get_input[0]
    arguments = get_input[1]

    # Instances directory
    instances_directory = options.directory
    instances_directory_list = sorted_ls(instances_directory)
    

    # END OF THE CODE
    time_elapsed = time.clock() - time_start
    print(f"Elapsed time: {time_elapsed}s")


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


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
                      help="STRING value - directory of the instances to compute")
    (options, args) = parser.parse_args()

    return options, args


if __name__ == '__main__':
    main()