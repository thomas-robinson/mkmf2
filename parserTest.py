#!/bin/python
from parseShort import getModules;
import sys;

if __name__ == "__main__":
	print("------------------------------")
	print("The module dependencies are:")
	for i in getModules(sys.argv[1]):
		print(i)
	print("------------------------------")
	
	
