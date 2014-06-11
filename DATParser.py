
# Originially written by Andy Buchanan to produce a dictionary of Patent objects,
# I'm modifying this so that it produces an array of dictionaries (which can
# easily be loaded into MongoDB or saved as .json)

import datetime, re, logging, os
import Patent

fr = '/Users/Shared/patent_raw_data/dat/'

class DATParser:
	def __init__(self):
		# self.patns = dict()
		self.patns = []
		self.badPatns = dict()
		# I've left badPatns alone for now; ultimately, we'll want to keep a list 
		# of bad patents in its own database, so badPatns should also be an array
		# of dicts, not a dict of Patents.
		
		# self.patn = Patent.Patent(-1)
		self.patn = {
            'rawcites' : [],
            'cites' : [],
            'citedby': []
        }
		
		self.state = 'PATN'
		
		self.reEOL = r"[ \t\r]*$"
		self.reDate = r"([0-9]{8})" + self.reEOL
		self.rePATN = r"PATN" + self.reEOL
		self.reWKU = r"WKU  0?([1-9][0-9]{6}).?" + self.reEOL
		self.reAPD = r"APD  " + self.reDate
		self.reTTL = r"TTL  (.*)$"
		self.reMoreTTL = r"     (.*)$"
		self.reISD = r"ISD  " + self.reDate
		self.reASSG = r"ASSG" + self.reEOL
		self.reNAM = r"NAM  (.*)" + self.reEOL
		self.reCLAS = r"CLAS" + self.reEOL
		self.reOCL = r"OCL  (.*)" + self.reEOL
		self.reICL = r"ICL  (.*)" + self.reEOL
		self.reUREF = r"UREF" + self.reEOL
		self.rePNO = r"PNO  (.*)" + self.reEOL # loose because some refs are crazy
		self.reNonUtil = r"WKU  (RE|D|T|PP|H)"
	
	def parseFile(self, fp):
		self.fn = os.path.basename(fp)
		with open(fp) as fPatn:
			# self.patn = Patent.Patent(-1)
			self.patn = {
                'rawcites' : [],
                'cites' : [],
                'citedby': []
            }
			for line in fPatn:
				if self.state == 'PATN' or self.state == 'UREF/PATN' or self.state == 'WKU':
					if re.match(self.rePATN, line) or self.state == 'WKU':
						self.parsePATN(line, fPatn)
					elif self.state == 'UREF/PATN' and re.match(self.reUREF, line):
						self.parseUREF(fPatn.next(), fPatn)
				elif self.state == 'APD':
					# need to store the match because APD is on the same line, not next
					match = re.match(self.reAPD, line)
					if match:
						self.parseAPD(match, fPatn)
				elif self.state == 'ASSG/CLAS':
					if re.match(self.reASSG, line):
						self.parseASSG(fPatn.next(), fPatn)
					if re.match(self.reCLAS, line):
						self.parseCLAS(fPatn.next(), fPatn)
		# catch that last damn patent
		if self.patn.pno not in self.badPatns:
			self.patns[self.patn.pno] = self.patn
		if -1 in self.patns:
			del(self.patns[-1])
		return (self.patns, self.badPatns)
		
	def parsePATN(self, line, fPatn):
		if self.state != 'WKU':
			line = fPatn.next()
		match = re.match(self.reWKU, line)
		if match:
			pno = int(match.group(1))
            # if self.patn.pno not in self.badPatns:
			if pno not in self.badPatns:
                # self.patns[self.patn.pno] = self.patn
                self.patns.append = self.patn
			self.patn['pno'] = pno
			self.state = 'APD'
		elif re.match(self.reNonUtil, line):
			self.state = 'PATN' # it's some other type, just keep going
		else:
			# this has never happened
			logging.warning("%s: PATN w/o WKU near %d in %s", self.state, self.patn.pno, self.fn)
			# self.badPatns[self.patn.pno] = self.patn
            self.badPatns[pno] = self.patn
			self.state='PATN'
			
	def parseUREF(self, line, fPatn):
		match = re.match(self.rePNO, line)
		if match:
			try:
				pno = int(match.group(1))
			except ValueError:
				# TODO this should probably include all citations
				pass # bad reference, ignore
			else:
                # self.patn.rawcites.append(pno)
                self.patn['rawcites'].append(pno)
		else:
			# this happens frequently
			# just one less rawcite, no big deal even if it's findable
			# be sure that next line isn't a PATN or something though
			logging.warning("UREF w/o PNO in %d in %s (%s)",\
			 	self.patn['pno'], self.fn, line.rstrip())
			
	def parseAPD(self, match, fPatn):
		if re.search(r'[12][0-9]{5}00', match.group(1)):	# occurs not infrequently
			# I trust that this will never go wrong
			# self.patn.apd = datetime.datetime.strptime(match.group(1), "%Y%m00").date()
            self.patn['apd'] = datetime.datetime.strptime(match.group(1), "%Y%m00").date()
			self.patn['apq'] = Patent.d2q(self.patn['apd'])
		else:
			try:
				self.patn['apd'] = datetime.datetime.strptime(match.group(1), "%Y%m%d").date()
			except ValueError:
				# this happens frequently, often subtly wrong: 1980-06-31 &c
				# so we'll chop the end off to preserve some date
				self.patn['apd'] = datetime.datetime.strptime(match.group(1)[0:6], "%Y%m").date()
				logging.warning("Bad apd date: '%s' in %d in %s", match.group(1), self.patn['pno'], self.fn)
			self.patn['apq'] = Patent.d2q(self.patn['apd'])
		
		line = fPatn.next()
		
		match = re.match(self.reTTL, line)
		self.patn['title'] = ''
		if match:
			self.patn['title'] = str(match.group(1).rstrip())
			line = fPatn.next() # only advance if matched
		else:
			# happens to 5001050 in 1991.dat (only)
			logging.warning("APD w/o TTL in %d in %s", self.patn['pno'], self.fn)
			self.badPatns[self.patn['pno']] = self.patn
			
		match = re.match(self.reMoreTTL, line)
		while match:
			self.patn['title'] += str(match.group(1).rstrip())
			line = fPatn.next()
			if re.match(self.rePATN, line) or re.match(self.reWKU, line):
				# has never happened
				logging.warning("Found PATN/WKU looking for title in %d in %s", self.patn['pno'], self.fn)
				self.badPatns[self.patn['pno']] = self.patn
				break
			match = re.match(self.reMoreTTL, line)
			
		match = re.match(self.reISD, line)
		if match:
			try:
				self.patn['isd'] = datetime.datetime.strptime(match.group(1), "%Y%m%d").date()
			except ValueError:
				# never happens
				logging.warning("Bad isd date: '%s' in %d in %s", match.group(1), self.patn['pno'], self.fn)
				self.badPatns[self.patn['pno']] = self.patn
			else:
				self.patn['isq'] = Patent.d2q(self.patn['isd'])
		else:
			# never happens
			logging.warning("TTL w/o ISD in %d in %s", self.patn['pno'], self.fn)
			self.badPatns[self.patn['pno']] = self.patn
		self.state = 'ASSG/CLAS'
		
	def parseASSG(self, line, fPatn):
		match = re.match(self.reNAM, line)
		if match:
			self.patn['assignee'] = str(match.group(1).rstrip())
		else:
			# happens frequently
			logging.warning("ASSG w/o NAM in %d in %s", self.patn['pno'], self.fn)
			if re.match(self.reCLAS, line):
				# looks like we ate the CLAS line
				self.parseCLAS(line, fPatn)
				
	def parseCLAS(self, line, fPatn):
		match = re.match(self.reOCL, line)
		if match:
			self.patn['uspc'] = str(match.group(1).rstrip())
		else:
			# never happens
			logging.warning("CLAS w/o OCL in %d in %s", self.patn['pno'], self.fn)
			self.badPatns[self.patn['pno']] = self.patn
		line = fPatn.next()
		match = re.match(self.reICL, line)
		while not match:
			if re.match(self.reUREF, line):
				# happens frequently
				logging.warning("Found UREF looking for ICL in %d in %s", self.patn['pno'], self.fn)
				self.state = 'UREF/PATN'
				break
			if re.match(self.rePATN, line):
				# happens frequently
				logging.warning("Found PATN looking for ICL in %d in %s", self.patn['pno'], self.fn)
				self.state = 'WKU'
				break
			line = fPatn.next()
			match = re.match(self.reICL, line)
		if match:
			self.patn['ipc'] = str(match.group(1).rstrip())
			self.state = 'UREF/PATN'
		# TODO doesn't get all IPCs
		# below version does, but eats next line
		# if next line's UREF, you lose a UREF
		#while match:
		#	self.patn.ipc += match.group(1).rstrip()
		#	line = fPatn.next()
		#	match = re.match(self.reICL, line)
