# INPUT:
# * Size of each instance -> size
# * Number of instances to generate -> instances
# OUTPUT:
# * Fixed sets generated in an Excel file

# points -> ([x1,y1], [x2,y2], [x3,y3]...[xn,yn])

from optparse import OptionParser

def main():
    get_input = getInput()

    options = get_input[0]
    arguments = get_input[1]
    
    try:
        size = int(options.size)
        instances = int(options.instances)

        print(f"Specified size: {size}")
        print(f"Number of instances to generate: {instances}")
    
    except:
        print("Use 'instance_generator -h' to get information of use.")


def output():
    pass


def getInput():
    parser = OptionParser()
    parser.add_option("-s", "--size",
                      dest="size",
                      help="INT value - Size of population to generate on each instance.")
    parser.add_option("-i", "--instances",
                      dest="instances",
                      help="INT value - Number of instances to generate.")
    (options, args) = parser.parse_args()

    return options, args


if __name__ == '__main__':
    main()