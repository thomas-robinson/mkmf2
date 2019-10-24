#!/bin/python
import re

verbose = True
vv = False
"""open the file and read contens"""
fname = "diag_manager.F90"
if verbose or vv:
	print('open ',fname,' and read contens')
f = open(fname, 'r')
fcontents = f.read()
if vv:
	print(fname, ":\n ",fcontens)
f.close()

""" Set up the regex to find use statements ^\s*use """
module_dependencies = []
findUse = re.compile('^\s*use', re.IGNORECASE)
findOnly = re.compile('only\s*:', re.IGNORECASE)
""" Parse each line of the file for the regex ^\s*use """
if verbose or vv:
	print('Parse each line of the file for the regex ^\s*use ')
for line in fcontents.splitlines():
	if findUse.match(line):
		if verbose or vv:
			print(line)
""" Split the line on a , because of multiple module possibility on a line """
		splitModLineCom = line.split(",")
		for mods in splitModLineCom:
""" If the current string has USE in it, split on white space.  The second member of this list is a module """
			if findUse.match(mods):
				mod1 = mods.split()
				alreadyExist = False
""" Get rid of dupicate mentions of a module """
				for md in module_dependencies:
					if md == mod1[1]:
						alreadyExist = True
						if vv:
							print(fname,": the module ",md," is listd more than once.  only keeping one")
						break
				if not alreadyExist:
					module_dependencies.append(mod1[1])

if verbose or vv:
	print("The dependencies for ",fname," are ",module_dependencies)

