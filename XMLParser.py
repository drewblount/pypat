
# Originially written by Andy Buchanan to produce a dictionary of Patent objects,
# I've modified this so that it produces an array of dictionaries (which can
# easily be loaded into MongoDB or saved as .json)

import datetime, os, xml.dom.minidom, logging
import Patent

# fr = '/Users/Shared/patent_raw_data/ipgb-2005-present/'
# DB: The following line is the source directory for the xml files to be parsed.
fr = '/Users/drewblunt/Desktop/tests/'

class XMLParser:
	def __init__(self):
				# self.patns will be an array of dicts
		self.patns = []
		self.badPatns = {}
		# self.badPatns isn't used anywhere in the code (it's always left empty)
	def parseFile(self, fp):
		self.fn = os.path.basename(fp)
		buf = ''
		bufs = []
		with open(fp) as fXml:
			for line in fXml:
				if line[0:5] == '<?xml':
					if buf != '':
						bufs.append(buf)
					buf = line
				else:
					buf += line
			bufs.append(buf) # make sure to catch the last one
		# print "Found",len(bufs),"xml entities to parse in",os.path.basename(fp)
		for sPatn in bufs:
			self.dom = xml.dom.minidom.parseString(sPatn)	# save dom for debugging convenience
			self.patn = self.parseXMLDom(self.dom)
			
			''' I comment this out because badpatns is apparently never used
			if self.patn != None and self.patn.pno not in self.badPatns:
				self.patns[self.patn.pno] = self.patn
			'''
			self.patns.append(self.patn)
		# print(self.patns)
		return (self.patns, self.badPatns)
	
	# previously returned a patent, should now return a patent dict
	def parseXMLDom(self, dom):
		
		self.patn = {
			'rawcites' : [],
			'cites' : [],
			'citedby': []
		}
		'''print("patent: ")
		print(self.patn)
		'''
		elmPubRef = dom.getElementsByTagName('publication-reference')[0].getElementsByTagName('document-id')[0]
		print("elmPubRef: " + elmPubRef.toprettyxml())
		try:
			pno = int(elmPubRef.getElementsByTagName('doc-number')[0].childNodes[0].data)
			self.patn['pno'] = pno
		except ValueError:
			print("ValueError")
			# presume that pno found is not a utility patent and ignore
			return
						
		# self.patn = Patent.Patent(pno)
		
		isd = elmPubRef.getElementsByTagName('date')[0].childNodes[0].data
		# self.patn.isd = datetime.datetime.strptime(isd, "%Y%m%d").date()
		isd = datetime.datetime.strptime(isd, "%Y%m%d").date()
		# Mongo cannot accept dates, only date+time. Gotta pad isd with time = midnight.
		self.patn['isd'] = datetime.datetime.combine(isd, datetime.datetime.min.time())
		self.patn['isq'] = Patent.d2q(self.patn['isd'])

		elmAppRef = dom.getElementsByTagName('application-reference')[0].getElementsByTagName('document-id')[0]
		apd = elmAppRef.getElementsByTagName('date')[0].childNodes[0].data
		# self.patn.apd = datetime.datetime.strptime(apd, "%Y%m%d").date()
		apd = datetime.datetime.strptime(apd, "%Y%m%d").date()
		# again, have to pad the date to make it a date+time
		self.patn['apd'] = datetime.datetime.combine(apd, datetime.datetime.min.time())
		self.patn['apq'] = Patent.d2q(self.patn['apd'])	# NB: may be out of nQuarters range
		
		uspc = dom.getElementsByTagName('classification-national')[0]
		uspc = uspc.getElementsByTagName('main-classification')[0].childNodes[0].data
		
		# self.patn.uspc = str(uspc.encode('ascii','replace'))
		self.patn['uspc'] = str(uspc.encode('ascii','replace'))
		
		''' DB:
			The most recent 2014 xmls don't have ipc or ipcr classifications, so the below code doesn't work. 
			Since we've never concerned ourselves with that data anyway, I'm not worrying about loading it
			for the years where it was stored.
			
		# they switched from classification-ipc to classification-ipcr at some point, search both
		ipc = (dom.getElementsByTagName('classification-ipc') + dom.getElementsByTagName('classification-ipcr'))[0]
		
		print "help?"
		
		print "here?"
		print self.patn
		
	
		
		try:
			# for classification-ipcr which breaks out each part of the IPC
			# section-class-subclass group/subgroup
			# NB: this is not the same format for these as in the DAT files
			ipc = "%s%s%s %s/%s" % tuple([x.childNodes[0].data for x in ipc.childNodes[5:14] if x.nodeType == 1])
		except IndexError:
			# sometimes the main-group is just <main-group/> instead of a real value
			# this is treated as '1' in the online database
			# so that's what we'll do too
			ipc1 = "%s%s%s" % tuple([x.childNodes[0].data for x in ipc.childNodes[5:10] if x.nodeType == 1])
			ipc2 = " 01/%s" % (ipc.childNodes[13],)
			ipc = ipc1 + ipc2
		except TypeError:
			# for classification-ipc which just gives a single string for each IPC
			ipc = ipc.getElementsByTagName('main-classification')[0].childNodes[0].data
		
		# self.patn.ipc = str(ipc.encode('ascii','replace'))
		self.patn['ipc'] = str(ipc.encode('ascii','replace'))

		'''

		elmsTitles = dom.getElementsByTagName('invention-title')[0].childNodes
		# self.patn.title = ''
		self.patn['title'] = ''
		for node in elmsTitles:
			# sometimes the title has subelements like italic text or what have you
			# sometimes the subelements don't have text at the bottom
			# 7632827, I'm looking at you here
			while node.nodeType != node.TEXT_NODE and node.childNodes:
				node = node.childNodes[0]
			if node.nodeType == node.TEXT_NODE:
				# self.patn.title += str(node.data.encode('ascii','replace'))
				self.patn['title'] += str(node.data.encode('ascii','replace'))
			else:
				# logging.warning('Skipped part of title %d in %s: %s', self.patn.pno, self.fn, node)
				logging.warning('Skipped part of title %d in %s: %s', self.patn['pno'], self.fn, node)


		elmAssig = dom.getElementsByTagName('assignees')

		if elmAssig:
			elmAssig = elmAssig[0]
			# sometimes it's an orgname, sometimes first + last, get all
			ass = (elmAssig.getElementsByTagName('orgname') + elmAssig.getElementsByTagName('first-name') + elmAssig.getElementsByTagName('last-name'))
			# self.patn.assignee = str(' '.join([x.childNodes[0].data.encode('ascii','replace') for x in ass]))
			self.patn['assignee'] = str(' '.join([x.childNodes[0].data.encode('ascii','replace') for x in ass]))

		elmRefCit = dom.getElementsByTagName('references-cited')
		# self.patn.rawcites = []
		self.patn['rawcites'] = []
		if elmRefCit:
			for cite in elmRefCit[0].getElementsByTagName('patcit'):
				if cite.getElementsByTagName('country')[0].childNodes[0].data == 'US':
					try:
						pno = int(cite.getElementsByTagName('doc-number')[0].childNodes[0].data)
					except ValueError:
						# presume that pno cited is not a utility patent and ignore
						continue
					else:
						# self.patn.rawcites.append(pno)
						self.patn['rawcites'].append(pno)
		return self.patn
