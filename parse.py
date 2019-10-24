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
justUse = re.compile('^\s*use', re.IGNORECASE)
if verbose or vv:
	print('regex is ^\s*use')
for line in fcontents.splitlines():
	if findUse.match(line):
		if verbose or vv:
			print(line)
		splitModLineCom = line.split(",")
		for mods in splitModLineCom:
			if findUse.match(mods):
				mod1 = mods.split()
				alreadyExist = False
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

