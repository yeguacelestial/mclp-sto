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
# TODO: Constructive Heuristic

import time

def main():
    time_start = time.clock()
    # START OF THE CODE
    time.sleep(2)
    # END OF THE CODE
    time_elapsed = float(time.clock() - time_start)
    print(f"Execution time: {time_elapsed}s")


if __name__ == '__main__':
    main()