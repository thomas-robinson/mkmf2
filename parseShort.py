#!/bin/python
import re;
import os;

fName = "diag_manager.F90"


##Parses Fortran file and returns module dependencies
#
#This function takes in a file to parse through. 
#Using regex pattern matching a module list is populated, cleaned up, and returned without duplicates.  
def getModules(fileName):
	MODS = [] 
	
	fileContents = open(fileName).read()
	
	##Regex pattern to find matches in the file
	#Checks for USE and possible & on the same or next line, until module name is found signified by the '?'
	#Ignores cases and tries to match on all lines
	patternMatch = re.compile('^ *USE[ &\n]+.*?[ &\n]*,', re.IGNORECASE | re.M) 
	
	##Finds all possible matches in the file
	#Puts all possible matches in a list
	matches = re.findall(patternMatch, fileContents)
	
	##Grooms and populates return list of modules
	#Removes spaces, characters from pattern matching, and checks for duplicates
	for match in matches:
		match = match.lower().strip()
		badChars = ["use", "&", '\n', ' ', ',']
		#clean up the matches
		for char in badChars:
			match = match.replace(char, '')
		if not match in MODS:
			MODS.append(match)
			
	
	return MODS

##Creates a Makefile.am
#Creates a Makefile.am in the path provided, resolving all the dependencies
def writeModules(modules, path):
	
	makefile = open('Makefile.am', 'w')
	
	fileList = os.listdir(path)
	
	fortranMatch = re.compile('[.F90&]')
	
	makefile.write("noinst_LTLIBRARIES = " + path + ".la\n")
	
	for file in fileList:
		if fotranMatch.match(file):
			makefile.write(file + "\\n")
		
	for mod in modules:
		makefile.write(mod + ".$(FC_MODEXT) : " + mod + ".$(OBJEXT)\n")
	

if __name__ == '__main__':
	#testing diag_manager.F90
	print(getModules(fName))
	
