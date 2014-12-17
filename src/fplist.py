import sys

def main():
    filename = sys.argv[1]
    fplist = create_fplist(filename)
    print fplist

def create_fplist(filename):
    fplist = []
    with open(filename, 'r') as fhandle:
    	for line in fhandle:
	    l = line.split()
	    del l[-1]
	    a = sorted(l)
	    fplist.append(tuple(a))
    return fplist

if __name__ == '__main__':
    main()

