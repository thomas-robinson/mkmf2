"""Fortran file parser.
Resolves dependencies between Fortran modules.
""" 

import re;
import os;

def getModules(fileName, verbose = False):
	"""Parses Fortran file and returns module dependencies.

	This function takes in a file to parse through. 
	Using regex to pattern match, populates a module list, cleans up, and returns without duplicates.
	Requires a name of the file to be parsed.  
	"""
	MODS = [] 
	
	fileContents = open(fileName).read()

	if verbose:
		print("Open " + fileName + " and read contents")
	
	"""Regex pattern to find matches in the file
	Checks for USE and possible & on the same or next line, until module name is found signified by the '?'
	Ignores cases and tries to match on all lines
	"""
	patternMatch = re.compile('^ *USE[ &\n]+.*?[ &\n]*,', re.IGNORECASE | re.M) 
	
	if verbose:
		print("Parsing the file, finding all possible matches using regex")
		
	"""Finds all possible matches in the file.
	Puts all possible matches in a list.
	"""
	matches = re.findall(patternMatch, fileContents)
	
	"""Grooms and populates return list of modules.
	Removes spaces, characters from pattern matching, and checks for duplicates.
	"""
	for match in matches:
		if verbose:
			print("Match found: " + match)
		match = match.lower().strip()
		badChars = ["use", "&", '\n', ' ', ',']
		for char in badChars:
			match = match.replace(char, '')
		if verbose:
			print("Cleaning up the match: " + match +"\n")
		if not match in MODS:
			MODS.append(match)
	
	if verbose:		
		print("The module dependencies are:")
		for m  in MODS:
			print(m)
		print("\n")
		
	return MODS


def getFileModuleName(fileName):
	"""Outputs the module name of a file.
	
	Requires name of file to be parsed.
	"""
	fileContents = open(fileName).read()
	
	moduleNameMatch = re.compile('MODULE+.*', re.IGNORECASE)
	
	matches = re.findall(moduleNameMatch, fileContents)
	
	return matches[0].split(' ')[1]


def getPathModuleNameList(path):
	"""Outputs a list of modules in given path.
	
	Requires a path to be parsed.
	"""
	moduleList = []
	
	for file in os.listdir(path):
		if os.path.isfile(file):
			moduleList.append(getFileModuleName(file))
		
	return moduleList
	


def writeModules(path, verbose = True):
	"""Creates a Makefile.am
	
	Creates a Makefile.am in the path provided, resolving all possible dependencies.
	Requires a path to a folder with Fortran modules. 
	"""
	
	os.chdir(path)
	
	folder = path.split('/')[len(path.split('/'))-1]
	
	makefile = open('Makefile.am', 'w')
	
	fileList = os.listdir(path)
	
	fortranMatch = re.compile('.*F90', re.IGNORECASE)
	
	if verbose:
		print("Setting work directory to " + path + "\n")
		print("Files to parse:\n")
		for f in fileList:
			print(f + "\n")
	
	"""List all possible sub directories"""
	makefile.write("SUBDIRS = \ \n")
	if verbose:
		print("Writing sub directories... \n")
	for file in fileList:
		if not fortranMatch.match(file) and not os.path.isfile(file):
			if verbose:
				print(file + "\n")
			makefile.write("\t" + file + " \ \n")
	
	makefile.write("\n\n")
	makefile.write("noinst_LTLIBRARIES = lib" + folder + ".la\n")
	makefile.write("lib" + folder +"_la_SOURCES = \ \n")
	
	if verbose:
		print("Writing Fortran sources... \n")
	"""List Fortran file sources"""
	for file in fileList:
		if fortranMatch.match(file):
			if verbose:
				print(file + "\n")
			makefile.write("\t" + file + " \ \n")
	
	makefile.write("\n\n")
	
	if verbose:
		print("Writing module initialization... ")
	"""Initialize the modules"""	
	for file in fileList:
		if fortranMatch.match(file):
			makefile.write(getFileModuleName(file) + ".$(FC_MODEXT) : " + file.split('.')[0] + ".$(OBJEXT)\n")
		
	makefile.write("\n\n")
	
	if verbose:
		print("Writing module dependencies... ")
	"""List dependencies of each file"""
	for file in fileList:
		if fortranMatch.match(file):
			makefile.write(file.split('.')[0] + ".$(OBJEXT) : \ \n")
			for mod in getModules(file, verbose):
				makefile.write("\t" + mod + ".$(FC_MODEXT) \ \n")
				
	makefile.write("\n\n")
	makefile.write("MODFILES = \ \n")
	
	"""List all modules files in built_sources"""
	for file in fileList:
		if fortranMatch.match(file):
				makefile.write("\t" + getFileModuleName(file) + ".$(FC_MODEXT) \ \n")
	
	makefile.write("BUILT_SOURCES = $(MODFILES)\n")
	makefile.write("include_HEADERS = $(MODFILES)\n")
	makefile.write("\n\n")
	
	makefile.write("CLEANFILES = *.$(FC_MODEXT)")

if __name__ == '__main__':
	writeModules('/home/Diyor.Zakirov/atmos_param/diag_cloud_rad')
