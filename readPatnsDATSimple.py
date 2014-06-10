#check the data for every patent that shows up in the log
#	maybe the patent after them too
#	or buffer the patn search
#BUGBUG look into pickling again (highest protocol slowest? cause it's slow as **fuck**)
#fewer lines in poolsize
#nPatnsEachIPC-A needs labels -- cumhits!
#make a bunch of the perQuarter graphs peryear
#	esp. nisdPerQuarter
#make dictQ FIFO to make auditting easier
#	-> figure out why totals aren't right!
#ExpIPC w/uspc
#remake act figs with coloring reflecting degree of separation


# Notes:
# to double-check counts in xml files do something like:
# grep -c '^<us-patent-grant .* file="US0[0-9]*-' *.xml
# leaving off the us-patent-grant bit finds image tags as well

# nPatns found in files 1976.dat through ipgb20101228.xml
# grep '^WKU \+[0-9]' *.dat | wc -l
# 2892360
# grep '^<us-patent-grant.*file="US0' *.xml | wc -l
# 1020707
# = 3913067

# open `svn st | gawk '{printf("%s ",$2)}'`

# todo:
# fix live re-running, can't be copying patns to each new process
# look into using split and re.split for the file parsing
# look at using SAX for the XML
# look at controlling swapping out
# talk with Noah re: old stuff

import os, time, logging, datetime, inspect
import multiprocessing, Queue
import DATSimple, Patent

fnLog = 'patents.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"


if not 'patns' in dir():	# assume this is first time running
	# don't overwrite patns!
	patns = dict()
	# no need to re-run logging config
	logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)
	datfilelist = [DATParser.fr + x for x in os.listdir(DATParser.fr) if x[-4:] == '.dat']
else:
	logging.info('Found existing patns dict, continuing')
datfilelist = datfilelist[1]		# just get 1st file for now...
def loadPatnFiles(patns, fl):
	logging.info("Started read at %s", time.strftime("%X %x"))

	for fp in datfilelist:
		parser = DATSimple.DATParser()
		logging.info("Parsing %s", os.path.basename(fp))
		try:
			dpatns,badpatns = parser.parseFile(fp)
			logging.info("%d (%d bad) found in %s", len(dpatns), len(badpatns), os.path.basename(fp))
			dQ.put(dpatns)
			parser.patns = dict()	# toss old patns
						# BUGBUG tossing bad patns instead of dealing with them
			parser.badpatns = dict()
		except:
			logging.error("Error parsing %s", os.path.basename(fp), exc_info=True)
			eQ.put(fp)
			fQ.task_done()
			#dictQ.close()
		logging.info("Worker finished.")
		
	# all workers are done, join up extraneous queues and such
	for p in workerProcesses:
		p.join()
	fileQ.join()	# should be instant as workers are already done
	dictQ.join()
	#if not dictQ.empty():	logging.error("dictQ not empty before close!")
	#dictQ.close()
	#dictQ.join_thread()
	logging.info("done reading files after %.2f minutes.", (time.time()-tStart)/60)

def sanityCheck(patns):
	# misc cleanup
	def handFix(patns):
		# bad, but fixable, apds
		patns[3943504].apd = datetime.date(1975, 2, 25) # not 2975
		patns[3964954].apd = datetime.date(1973, 5, 31) # not 9173
		patns[3969699].apd = datetime.date(1975, 4, 11) # not 9175
		patns[4010353].apd = datetime.date(1974, 9, 11) # not 9174
		patns[4020425].apd = datetime.date(1976, 3, 26) # not 2976
		patns[4032532].apd = datetime.date(1973, 3, 1) # not 9173
		patns[4041523].apd = datetime.date(1976, 6, 1) # not 9176
		patns[4135654].apd = datetime.date(1977, 4, 11) # not 9177
		patns[4198308].apd = datetime.date(1978, 7, 21) # not 7978
		patns[4255928].apd = datetime.date(1978, 12, 11) # not 9178
		patns[4474874].apd = datetime.date(1983, 3, 11) # not 9183
		patns[4542062].apd = datetime.date(1982, 1, 20) # not 2982
		patns[4596904].apd = datetime.date(1984, 5, 25) # not 2984
		patns[4709214].apd = datetime.date(1986, 4, 28) # not 2986
		patns[4725260].apd = datetime.date(1987, 3, 24) # not 2987
		patns[4732727].apd = datetime.date(1986, 4, 3) # not 9186
		patns[4739365].apd = datetime.date(1987, 5, 28) # not 2987
		for pno in [3943504, 3964954, 3969699, 4010353, 4020425, 4032532, 4041523, 4135654, 4198308,\
			4255928, 4474874, 4542062, 4596904, 4709214, 4725260, 4732727, 4739365]:
			patns[pno].apq = Patent.d2q(patns[pno].apd)
			
		# datetime.date(8198, 4, 5) ???? even on patn image!
		if hasattr(patns[4469216], 'apd'):
			del(patns[4469216].apd, patns[4469216].apq)
			
		# the only bad (missing) TTL
		# b/c missing title, not included by current scripts
		# patns[5001050].title = 'PH.phi.29 DNA polymerase'
		
	execfile('checkCoverage.py')	# import checkCoverage
	missing = checkCoverage(patns)
	handFix(patns)
	#for patn in patns.itervalues():
	#	if 
	# ipcs
	# <main-group/> : 89 from 2005 - 20101228
	
def populateCites(patns):
	logging.info("Started reverse at %s", time.strftime("%X %x"))
	tStart = time.time()
	for citingPatn in patns.itervalues():
		if citingPatn.pno % 100000 == 0:
			print '\r', citingPatn.pno,
		isq = citingPatn.isq
		citedPnos = citingPatn.rawcites
		
		for citedPno in citedPnos:
			if not patns.has_key(citedPno):
				# only include patents in our dataset
				continue
			citedPatn = patns[citedPno]
			# the ifs allow for rerunning without causing problems
			if citedPno not in citingPatn.cites:
				citingPatn.cites.append(citedPno)
			if citingPatn.pno not in citedPatn.citedby:
				citedPatn.citedby.append(citingPatn.pno)
	print
	logging.info("done after %.2f minutes.", (time.time()-tStart)/60)


logging.info("-------------------------------------")
logging.info("$Id: readPatnsFromFiles.py 293 2011-04-04 20:45:34Z andy $")

#xmlfilelist = [frXML + 'ipgb20081104.xml', frXML + 'ipgb20091215.xml']
#datfilelist = [datfilelist[-1]]
#xmlfilelist = ['test.xml']
#datfilelist = ['test.dat']
loadPatnFiles(patns, xmlfilelist + datfilelist)
#sanityCheck(patns)
#populateCites(patns)
