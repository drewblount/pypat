import datetime
import Patent

class PerQuarter:
	def __init__(self, nQuarters):
		self.nPatns = [0] * nQuarters	# number of patns issued that quarter
		
		# total number of citations made that quarter
		self.nRawCitesMade = [0] * nQuarters
		self.nCitesMade = [0] * nQuarters	# only cites within our dataset
		self.nCitesRecd = [0] * nQuarters
		
		self.avgRawCitesMade = [0] * nQuarters	# average number of cites made
		self.avgCitesMade = [0] * nQuarters
		self.avgCitesRecd = [0] * nQuarters	# NB: this is activity
		
		self.totApdIsdLag = [0] * nQuarters
		self.avgApdIsdLag = [0] * nQuarters	# in years
		
		self.totIsdCiteIsdDiff = [0] * nQuarters
		self.avgIsdCiteIsdDiff = [0] * nQuarters
		self.totApdCiteIsdDiff = [0] * nQuarters
		self.avgApdCiteIsdDiff = [0] * nQuarters
		
		# for prior statistic
		self.cumIsd = None
		self.cumCitesMade = None
		self.cumCitesPerPatn = None
		
		# the summed activity *list* of all patents issued that quarter
		# each is an nQuarters-long list of nQuarters-long lists
		# so self.avgAct[0] is the average activity of all patns issued in 1976q1
		self.totAct = []
		self.avgAct = []
		self.totActApd = []
		self.avgActApd = []
		for i in range(nQuarters):
			self.totAct.append([0]*nQuarters)
			self.avgAct.append([0]*nQuarters)
			self.totActApd.append([0]*nQuarters)
			self.avgActApd.append([0]*nQuarters)
		
	def Stats(self, patns, nQuarters):
		'''Collect all the statistics needed'''
		for patn in patns.itervalues():
			if patn.pno % 100000 == 0:
				print '\r', patn.pno,
				
			isq = patn.isq
			self.nPatns[isq] += 1
			self.nRawCitesMade[isq] += len(patn.rawcites)
			self.nCitesMade[isq] += len(patn.cites)
			self.nCitesRecd[isq] += len(patn.citedby)
			
			# activity stuff
			self.totAct[isq] = [a+b for a,b in zip(self.totAct[isq],patn.Activity(patns))]
			self.totActApd[isq] = [a+b for a,b in zip(self.totActApd[isq],patn.ActivityApd(patns))]
		print
			
		for isq in range(nQuarters):
			nPatns = self.nPatns[isq]
			if nPatns < 1:	# mostly for testing
				continue
			self.avgRawCitesMade[isq] = 1.0 * self.nRawCitesMade[isq] / nPatns
			self.avgCitesMade[isq] = 1.0 * self.nCitesMade[isq] / nPatns
			self.avgCitesRecd[isq] = 1.0 * self.nCitesRecd[isq] / nPatns
			for i in range(nQuarters):
				self.avgAct[isq][i] = 1.0 * self.totAct[isq][i] / nPatns
				self.avgActApd[isq][i] = 1.0 * self.totActApd[isq][i] / nPatns
		
		self.cumIsd = Patent.Cumulate(self.nPatns)
		self.cumCitesMade = Patent.Cumulate(self.nCitesMade)
		self.cumCitesPerPatn = [1.0 * c / n for c,n in zip(self.cumCitesMade,self.cumIsd)]
		
	def DateStats(self, patns, nQuarters):
		nPatnsNoApd = [0] * nQuarters	# to adjust nPatns when averaging
		nPatnsNoCites = [0] * nQuarters
		nPatnsCiteNoApd = [0] * nQuarters
		
		# date information
		for patn in patns.itervalues():
			if patn.pno % 100000 == 0:
				print '\r', patn.pno,
			
			if patn.cites:
				avgICIdiff = 1.0 * sum([(patn.isd - patns[cpno].isd).days for cpno in patn.cites])/len(patn.cites)
				self.totIsdCiteIsdDiff[isq] += avgICIdiff
				if hasattr(patn, 'apd'):
					avgACIdiff = 1.0 * sum([(patn.apd - patns[cpno].isd).days for cpno in patn.cites])/len(patn.cites)
					self.totApdCiteIsdDiff[isq] += avgACIdiff
				else:
					nPatnsCiteNoApd[isq] += 1
			else:
				nPatnsNoCites[isq] += 1					
	
			if hasattr(patn, 'apd'):
				self.totApdIsdLag[isq] += (patn.isd - patn.apd).days
			else:
				nPatnsNoApd[isq] += 1
		print
		
		
		for isq in range(nQuarters):
			self.avgApdIsdLag[isq] = 1.0 * self.totApdIsdLag[isq] / (nPatns - nPatnsNoApd[isq]) / 365
			nPatns = nPatns - nPatnsNoCites[isq]	# don't average patents w/o any citations
			if nPatns < 1:	continue
			self.avgIsdCiteIsdDiff[isq] = 1.0 * self.totIsdCiteIsdDiff[isq] / nPatns / 365
			nPatns = nPatns - nPatnsNoCites[isq] - nPatnsCiteNoApd[isq]
			if nPatns < 1:	continue
			self.avgApdCiteIsdDiff[isq] = 1.0 * self.totApdCiteIsdDiff[isq] / nPatns / 365
