Some quick info about what's what:
If you're just in it for the graphing, look at figgen.R

Patent and informational objects:
Patent.py - the basic patent object, number, app date, issue date, class, etc
	- includes generated properties as well: cited by, activity, etc
PerQuarter.py - quarterly information storage
CatInfo.py - IPC related information

The main event, these work to build (and cleanup) a big ol' dict with all the patents in it
readPatnsFromFiles.py - the main startup script for importing and cleaning the patent data
DATParser.py - parser for dat files, format from 1976-2004
XMLParser.py - parser for xml files, the format from 2005-present
checkCoverage.py - xml files don't always parse well, so this checks if any were missed
badIpcs.py - checks for missing/invalid ipc data
analyzePatns.py - more cleanup
mylib.py - convenience functions

Data analysis:
Shadow.py - a simple random attachment shadow model
TopActNormalized.py - a series of activity normalizations
saveData.py - writes out a number of data files for graphing
dedate.sh - removes the date from an R generated PDF so that changes to the file will be apparent to versioning systems
figgen.R - convert all the data files into pretty pictures

articles/
html/ - where data and some figures are stored
tfigs/ - where other figures are stored

Misc:
notes.txt - my scratchpad
classes.tmproj - convenience file for Textmate
scripts.tmproj
test.dat - testing data
test.xml
Not/ - old unused stuff
