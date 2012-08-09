import datetime

nQuarters = 140	# set elsewhere, but chicken and egg here
dataStart = datetime.date(1976,1,1)
dataEnd = datetime.date(2010,12,31)

def Cumulate(l):
	def cumuiter(l):
		tot = 0
		for i in l:
			tot += i
			yield tot
	return list(cumuiter(l))

def d2q(d):
	'''Returns the number of quarters since start'''
	return (d.year-dataStart.year)*4 + (d.month-1)/3


class Patent(object):
	'''Class for a single patent'''
	
	# this eliminates the __dict__ from each instance, saving space
	# the downside is that more bits can't be added on the fly
	__slots__ = ['pno',\
				'title', 'isd', 'isq', 'uspc',\
	 			'apd', 'apq', 'ipc',\
				'assignee', 'cites', 'rawcites', 'citedby',\
				'_act']
	
	def __init__(self, pno):
		# this is the only attr that patns are truly guaranteed to have
		self.pno = pno
		
		# all patns will have, but may be empty:
		# rawcites, cites, citedby
		self.rawcites = []
		self.cites = []
		self.citedby = []
		
		# all patns should have:
		# title, isd, isq, uspc
		
		# all patns should also have
		# _act
		# but it should be accessed by Activity()
		
		# many patns will lack due to errors:
		# apd, apq, ipc
		
		# many patns will explicitly *not* have:
		# assignee
		# by design
		
	def __repr__(self):
		return "<Patent %d>" % self.pno
		
	def Print(self):
		print "patn %d" % self.pno
		for a in Patent.__slots__:
			if hasattr(self,a):
				print "%s: %s" % (a,getattr(self,a))
				
	def Activity(self, patns):
		'''Returns a list of the patent's cumulative hits'''
		if not hasattr(self, '_act'):
			actaccum = [0] * nQuarters
			for citingPatnNo in self.citedby:
				actaccum[patns[citingPatnNo].isq] += 1

			self._act = Cumulate(actaccum)
			
		return self._act
		
	def ActivityApd(self, patns):
		'''Returns a list of the patent's cumulative hits based on app date'''
		actaccum = [0] * nQuarters
		for citingPatnNo in self.citedby:
			citingPatn = patns[citingPatnNo]
			if hasattr(citingPatn, 'apd') and dataStart <= citingPatn.apd <= dataEnd:
				# below removed because it was coming up a lot
				#if citingPatn.apd < self.isd:
				#	print citingPatn.pno, "cites patn not issued yet:", self.pno
				#else:
				actaccum[citingPatn.apq] += 1
				
		return Cumulate(actaccum)
	