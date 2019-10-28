#!/bin/python
import re;
import os;

fName = "diag_manager.F90"

def getModules(fileName):
	MODS = [] 
	
	fileContents = open(fileName).read()
	
	#The regex creates a pattern to find matches in the file
	#Checks for USE and possible & on the same or next line, until module name is found signified by the '?'
	#Ignores cases and tries to match on all lines
	patternMatch = re.compile('^ *USE[ &\n]+.*?[ &\n]*,', re.IGNORECASE | re.M)  #regex to match 
	
	matches = re.findall(patternMatch, fileContents) #list of all matches
	
	for match in matches:
		match = match.lower().strip()
		badChars = ["use", "&", '\n', ' ', ',']
		#clean up the matches
		for char in badChars:
			match = match.replace(char, '')
		if not match in MODS:
			MODS.append(match)
			
	
	return MODS


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
	
