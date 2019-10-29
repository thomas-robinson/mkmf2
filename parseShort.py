import re;
import os;
##!@package Parser
#Resolves dependencies 
fName = "diag_manager.F90"
##\brief Parses Fortran file and returns module dependencies
#
#This function takes in a file to parse through. 
#Using regex pattern matching a module list is populated, cleaned up, and returned without duplicates.  
def getModules(fileName, verbose = False):
	MODS = [] 
	
	fileContents = open(fileName).read()

	if verbose:
		print("Open" + fileName + " and read contents")
	
	##Regex pattern to find matches in the file
	#Checks for USE and possible & on the same or next line, until module name is found signified by the '?'
	#Ignores cases and tries to match on all lines
	patternMatch = re.compile('^ *USE[ &\n]+.*?[ &\n]*,', re.IGNORECASE | re.M) 
	
	if verbose:
		print("Parsing the file, finding all possible matches using regex")
	##Finds all possible matches in the file
	#Puts all possible matches in a list
	matches = re.findall(patternMatch, fileContents)
	
	##Grooms and populates return list of modules
	#Removes spaces, characters from pattern matching, and checks for duplicates
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
			
	print("The module dependencies are:")
	return MODS

##\brief Creates a Makefile.am
#Creates a Makefile.am in the path provided, resolving all the dependencies
def writeModules(modules, path):
	
	folder = path.split('/')[len(path.split('/'))-1]
	
	makefile = open('Makefile.am', 'w')
	
	fileList = os.listdir(path)
	
	fortranMatch = re.compile('[F90$]', re.IGNORECASE)
	
	makefile.write("SUBDIRS = \ \n")
	for file in fileList:
		if not fortranMatch.match(file):
			makefile.write("\t" + file + " \ \n")
	
	makefile.write("\n\n")
	makefile.write("noinst_LTLIBRARIES = lib" + folder + ".la\n")
	makefile.write("lib" + folder +"_la_SOURCES = \ \n")
	
	for file in fileList:
		if fortranMatch.match(file):
			makefile.write("\t" + file + " \ \n")
	
	makefile.write("\n\n")
		
	for file in fileList:
		makefile.write(file.split('.')[0] + ".$(FC_MODEXT) : " + file.split('.')[0] + ".$(OBJEXT)\n")
		
	makefile.write("\n\n")
	
	makefile.write("CLEANFILES = *.$(FC_MODEXT)")

if __name__ == '__main__':
	writeModules(getModules(fName), '/home/Diyor.Zakirov/atmos_param/clubb/CLUBB_core')
	print(getModules(fName))
	
