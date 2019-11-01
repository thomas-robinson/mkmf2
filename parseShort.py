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
from conda_env.env import Dependencies
from boto.mws.response import GetSubscriptionResult
from conda.exports import subdir

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
		matches = ' '
		return matches
	else:
		return matches[0].split(' ')[1]


def getPathModuleNameList(path):
	"""Outputs a list of modules in given path.
	
	Requires a path to be parsed.
	"""
	
	moduleList = []
	
	fileList = os.listdir(path)
	
	for file in fileList:
		if os.path.isfile(path + "/" + file) and file != "Makefile.am":
			moduleList.append(getFileModuleName(path + "/" + file))
	
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
	
	subDirModules = []
	
	DONE = False
	
	AMCPPFLAGS_str = ''
	SUBDIRS_str = ''
	SOURCES_str = ''
	MODULESINIT_str = ''
	DEPENDENCIES_str = ''
	BUILTSOURCES_str = ''
	
	if verbose:
		print("Setting work directory to " + path + "\n")
		print("Files to parse:\n")
		for f in fileList:
			print(f)
	
	
	for file in fileList:
		
		"""List all possible sub directories"""
		if not os.path.isfile(file) and not fortranMatch.match(file):
			SUBDIRS_str += ("\t" + file + " \\\n")
			print(path + "/" + file)
			subDirModules.append(getPathModuleNameList(path + "/" + file))
		
		
		"""List Fortran file sources"""
		if fortranMatch.match(file):
			SOURCES_str += ("\t" + file + "\\\n")
			MODULESINIT_str += (getFileModuleName(file) + ".$(FC_MODEXT) : " + file.split('.')[0] + ".$(OBJEXT)\n")
			
			"""List dependencies of each file"""
			check = any(item in getModules(file, verbose) for item in getPathModuleNameList(path))
			print(check)
			if check:
				DEPENDENCIES_str += (file.split('.')[0] + ".$(OBJEXT) : \\\n")
			for mod in getModules(file, verbose):
				if mod in getPathModuleNameList(path) or subDirModules:
					DONE = True
					DEPENDENCIES_str += ("\t" + mod + ".$(FC_MODEXT) \\\n")
			if DONE:
				DEPENDENCIES_str = DEPENDENCIES_str[0:len(DEPENDENCIES_str)-3] + "\n"
				DONE = False		
			
			"""List all modules files in built_sources"""
			BUILTSOURCES_str += ("\t" + getFileModuleName(file) + ".$(FC_MODEXT) \\\n")
	
	
	"""Write populated strings to the file"""
	if verbose:
		print("\nWriting sub directories... \n")
	if SUBDIRS_str != '':
		makefile.write("SUBDIRS = \\\n" + SUBDIRS_str[0:len(SUBDIRS_str)-3] + '\n')
	
	makefile.write("\n\n")
	
	if verbose:
		print("\nWriting Fortran sources... \n")
	if SOURCES_str != '':
		makefile.write("noinst_LTLIBRARIES = lib" + folder + ".la\n" +
					  "lib" + folder +"_la_SOURCES = \\\n" + 
					  SOURCES_str[0:len(SOURCES_str)-2] + '\n')
		makefile.write("\n\n")
		if verbose:
			print("\nWriting module initializations... \n")
		makefile.write(MODULESINIT_str)
		makefile.write("\n\n")
		if verbose:
			print("\nWriting module dependencies... \n")
		makefile.write(DEPENDENCIES_str)
		makefile.write("\n\n")
		makefile.write("MODFILES = \\\n" + BUILTSOURCES_str[0:len(BUILTSOURCES_str)-3] + '\n' + 
					"BUILT_SOURCES = $(MODFILES)\n" + 
					"include_HEADERS = $(MODFILES)\n")
		makefile.write("\n\n")
	
	
	makefile.write("CLEANFILES = *.$(FC_MODEXT)")
	
	print(subDirModules)
	
if __name__ == '__main__':
	writeModules('/home/Diyor.Zakirov/atmos_param/clubb')

	
                                     