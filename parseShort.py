''' 
!***********************************************************************
!*                   GNU Lesser General Public License
!*
!* This file is part of the GFDL Flexible Modeling System (FMS).
!*
!* mkmf2 is free software: you can redistribute it and/or modify it under
!* the terms of the GNU Lesser General Public License as published by
!* the Free Software Foundation, either version 3 of the License, or (at
!* your option) any later version.
!*
!* mkmf2 is distributed in the hope that it will be useful, but WITHOUT
!* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
!* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
!* for more details.
!*
!* You should have received a copy of the GNU Lesser General Public
!* License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
!*
!* Author: Diyor Zakirov
!***********************************************************************
'''

"""Fortran file parser.
Resolves dependencies between Fortran modules.
""" 

import re;
import os;
from docutils.parsers.rst.directives import encoding

def getModules(fileName, verbose = False):
	"""Parses Fortran file and returns module dependencies.

	This function takes in a file to parse through. 
	Using regex to pattern match, populates a module list, cleans up, and returns without duplicates.
	Requires a name of the file to be parsed.  
	"""
	MODS = [] 
	
	fileContents = open(fileName, encoding = 'latin-1').read()

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
	fileContents = open(fileName, encoding = 'latin-1').read()
	
	moduleNameMatch = re.compile('MODULE+.*', re.IGNORECASE)
	
	matches = re.findall(moduleNameMatch, fileContents)
	
	if not matches:
		matches = [' ']
		return matches
	else:
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
	


def writeModules(path, verbose = False):
	"""Creates a Makefile.am
	
	Creates a Makefile.am in the path provided, resolving all possible dependencies.
	Requires a path to a folder with Fortran modules. 
	"""
	
	os.chdir(path)
	
	folder = path.split('/')[len(path.split('/'))-1]
	
	makefile = open('Makefile.am', 'w',)
	
	fileList = os.listdir(path)
	
	fortranMatch = re.compile('.*F90', re.IGNORECASE)
	
	
	SUBDIRS = False
	SOURCES = False
	DEPENDENCIES = False
	
	if verbose:
		print("Setting work directory to " + path + "\n")
		print("Files to parse:\n")
		for f in fileList:
			print(f)
	
	"""List all possible sub directories"""
	for file in fileList:
		if not fortranMatch.match(file) and not os.path.isfile(file):
			SUBDIRS = True;
	if verbose:
		print("\nWriting sub directories... \n")
	if SUBDIRS:
		makefile.write("\nSUBDIRS = \\\n")
		for file in fileList:
			if (file == fileList[-1] and fortranMatch.match(file)) or (file == fileList[-2] and fortranMatch.match(file)):
				makefile.write("\t" + file)
			if not fortranMatch.match(file) and not os.path.isfile(file):
				if verbose:
					print(file)
				makefile.write("\t" + file + " \\\n")
	
	makefile.write("\n\n")
	
	"""List Fortran file sources"""
	for file in fileList:
		if fortranMatch.match(file):
			SOURCES = True;
	if verbose:
		print("\nWriting Fortran sources... \n")
	if SOURCES:
		makefile.write("noinst_LTLIBRARIES = lib" + folder + ".la\n")
		makefile.write("lib" + folder +"_la_SOURCES = \\\n")
		for file in fileList:
			if fortranMatch.match(file):
				if verbose:
					print(file)
				makefile.write("\t" + file + " \\\n")
	
	makefile.write("\n\n")
	
	if verbose:
		print("\nWriting module initialization... ")
	"""Initialize the modules"""	
	if SOURCES:
		for file in fileList:
			if fortranMatch.match(file):
				makefile.write(getFileModuleName(file) + ".$(FC_MODEXT) : " + file.split('.')[0] + ".$(OBJEXT)\n")
		
	makefile.write("\n\n")
	
	if verbose:
		print("\nWriting module dependencies... \n")
	"""List dependencies of each file"""
	for file in fileList:
		if fortranMatch.match(file):
			check = any(item in getModules(file, verbose) for item in getPathModuleNameList(path))
			if check:
				makefile.write(file.split('.')[0] + ".$(OBJEXT) : \\\n")
			for mod in getModules(file, verbose):
				if mod in getPathModuleNameList(path):
					makefile.write("\t" + mod + ".$(FC_MODEXT) \\\n")
				
	makefile.write("\n\n")

	"""List all modules files in built_sources"""
	if SOURCES:
		makefile.write("MODFILES = \\\n")
		for file in fileList:
			if fortranMatch.match(file):
					makefile.write("\t" + getFileModuleName(file) + ".$(FC_MODEXT) \\\n")
	
		makefile.write("BUILT_SOURCES = $(MODFILES)\n")
		makefile.write("include_HEADERS = $(MODFILES)\n")
	
	makefile.write("\n\n")
	
	makefile.write("CLEANFILES = *.$(FC_MODEXT)")

if __name__ == '__main__':
	writeModules('/home/Diyor.Zakirov/atmos_param')
