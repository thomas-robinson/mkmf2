# mkmf2
mkmf2 is a tool to create Makefile.am files based on fortran module depenencies.  
1. mkmf2 is a Python script
2. mkmf2 does not rely on any external programs that are not "commonly" available on target operating systems.
3. mkmf2 searches only the directory given for dependencies, ignoring subdirectories unless a -R --recursive option is given.
4. mkmf2 has an option (-l, --lib-name) to name the final library 
5. mkmf2 ignores all CPP macros when building the dependency tree
6. mkmfs ignores all #include/include statements that include a file not in the given directory/search path(s)
7. mkmf2 has a -v,--verbose option that clearly prints what the program is doing.  There is also a -vv/--very-verbose option
8. Source is (hopefully) clearly documented, including in-code comments, user documentation, etc., especially when the code may be unclear to another developer (e.g. when using complicated regular expressions).
9. mkmf2 has a -h/--help option to give a brief overview of options available.
10. mkmf2 works on *nix operating systems (including Mac OS X).

