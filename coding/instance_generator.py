# INPUT:
# * Size of each instance -> size
# * Number of instances to generate -> instances
# OUTPUT:
# * Fixed sets generated in an Excel file

# points -> ([x1,y1], [x2,y2], [x3,y3]...[xn,yn])

from optparse import OptionParser

def main():
    pass

def output():
    pass

def getInput():
    parser = OptionParser()
    parser.add_option("-s", "--size",
                      dest="size",
                      help="Size of the set of each instance to generate.")
    parser.add_option("-i", "--instances",
                      dest="instances",
                      help="Number of instances to generate.")
    (options, args) = parser.parse_args()

    return options, args


if __name__ == '__main__':
    main()