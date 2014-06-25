# I'm modifying Andy's original code to save each patent as a dictionary, and
# the list of patents as an array of dicts.

#check the data for every patent that shows up in the log
#	maybe the patent after them too
#	or buffer the patn search
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
import DATParser, XMLParser, Patent

from pymongo import MongoClient

fnLog = 'patents.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"

# PyMongo docs say to share one Client across the multiprocessors
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
# at some future point dbname could be an input argument
db = client[dbname]
# db will be passed around to the various threads

# DB: this 'if' will always be 'true' nowadays
if not 'patns' in dir():	# assume this is first time running
	# don't overwrite patns!
	# patns = dict()
	patns = []
	# no need to re-run logging config
	logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)
	# purposely leave errorQ untouched on rerun, ditto filelists
	fileQ = multiprocessing.JoinableQueue()
	# dictQ = multiprocessing.JoinableQueue()
	errorQ = multiprocessing.JoinableQueue()
	xmlfilelist = [XMLParser.fr + x for x in os.listdir(XMLParser.fr) if x[-4:] == '.xml']
	datfilelist = [DATParser.fr + x for x in os.listdir(DATParser.fr) if x[-4:] == '.dat']
else:
	logging.info('Found existing patns dict, continuing')

# def loadPatnFiles(patns, fl):
def loadPatnFiles(dbase, fl):
	logging.info("Started read at %s", time.strftime("%X %x"))
	tStart = time.time()
	workerProcesses = []
	map(fileQ.put, fl)

	def work(fQ, eQ):
		xmlp = XMLParser.XMLParser()
		datp = DATParser.DATParser()

		while not fQ.empty():
			fp = fQ.get()
			if fp[-4:] == '.xml':
				parser = xmlp
			else:
				parser = datp
			logging.info('Parsing %s', os.path.basename(fp))
			print ('Parsing ' + os.path.basename(fp))
			try:
				dpatns,badpatns = parser.parseFile(fp)
				print(os.path.basename(fp) + " is parsed.")
				# The len fun below works for both dicts (badpatns) and arrays (dpatns)
				logging.info("%d (%d bad) found in %s", len(dpatns), len(badpatns), os.path.basename(fp))
				
				# DB: This next line, I think, is Andy loading the parsed good patents into the
				# multicore queue. I just have each thread insert the patents straight into the db.
				# dQ.put(dpatns)

				# DB: the below line inserts all of the good patents into
				# the database collection 'patns'. Assumes dpatns is of type array of dicts.
				dbase['patns'].insert(dpatns)
				print (os.path.basename(fp) + " is in the database.")
	
				# parser.patns = dict()	# toss old patns
				parser.patns = []
				# Could deal with bad patns instead of tossing them, but probably not worth it.
				# DB: put them into a mongo instance?
				parser.badpatns = {}
			except:
				logging.error("Error parsing %s", os.path.basename(fp), exc_info=True)
				eQ.put(fp)
			fQ.task_done()
		logging.info("Worker finished.")
		
	for i in range(0, multiprocessing.cpu_count()):
		# DB: The following line seems to be the main call of work. I hope
		# multiprocessing.Process still works if I change dictQ to a mongod
		# object or something?
		# p = multiprocessing.Process(target=work, args=(fileQ, dictQ, errorQ))
		p = multiprocessing.Process(target=work, args=(fileQ, errorQ))
		p.daemon = True
		p.start()
		workerProcesses.append(p)
		
	""" DB: this while block doesn't serve any purpose but logging, and since I'm no longer
		using dictQ it's broken. A later fix might be adding a log entry after dbase is
		updated in work
	while True in map(multiprocessing.Process.is_alive, workerProcesses) or not dictQ.empty():
		try:
			# DB: copies dictQ to dpatns unless that process takes longer than 1 sec
			dpatns = dictQ.get(timeout=1)
			
			patns.update(dpatns)
			# DB: on second thought, perhaps the above command should be just
			# where I load into Mongo.
			dictQ.task_done()
			logging.info("patns now %d", len(patns))
		except Queue.Empty:
			pass
	"""
	
	# all workers are done, join up extraneous queues and such
	for p in workerProcesses:
		p.join()
	fileQ.join()	# should be instant as workers are already done
	# dictQ.join()
	logging.info("done reading files after %.2f minutes.", (time.time()-tStart)/60)
"""

def populateCites(patns):
	'''Populate the patents' "citedby" lists'''
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

"""

logging.info("-------------------------------------")

#Alternate, smaller patent file lists for testing
#xmlfilelist = [frXML + 'ipgb20081104.xml', frXML + 'ipgb20091215.xml']
#datfilelist = [datfilelist[-1]]
#xmlfilelist = ['test.xml']
#datfilelist = ['test.dat']


loadPatnFiles(db, xmlfilelist + datfilelist)
execfile('fixDates.py')
execfile('checkCoverage.py')
''' DB: I commented out the next two funcs just for testing
populateCites(patns)
'''
