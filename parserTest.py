#!/bin/python
from parseShort import getModules;
import sys;

if __name__ == "__main__":
	verbose = False
	for i in sys.argv:
		if i == "--verbose" or i == "-v":
			verbose = True
	
	print("------------------------------")
	for i in getModules(sys.argv[1], verbose):
		print(i)
	print("------------------------------")
	
	
