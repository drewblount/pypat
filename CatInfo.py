'''For storage of IPC/USPC related statistics'''

import logging
import PerQuarter

class CatInfo(object):
	def __init__(self, patns, nQuarters):
		self.A = dict()
		self.A00 = dict()
		self.Stats(self.A, 1, patns, nQuarters)
		self.Stats(self.A00, 3, patns, nQuarters)
		logging.info('Number of A00 cats: %d', len(self.A00))
		print 'Number of A00 cats: %d' % len(self.A00)
		# TODO average act lines for each cat
	
	def Stats(self, d, depth, patns, nQuarters):
		for patn in patns.itervalues():
			if patn.pno % 100000 == 0:
				print '\r', patn.pno,
			if not hasattr(patn, 'ipc'):
				continue
			# TODO this should count 'A01' and 'A 1' as the same cat
			cat = patn.ipc[0:depth].upper()
			isq = patn.isq
			if not d.has_key(cat):	# new category
				d[cat] = PerQuarter.PerQuarter(nQuarters)
			
			d[cat].cat = cat	# add a little something
			d[cat].nPatns[isq] += 1
			d[cat].nRawCitesMade[isq] += len(patn.rawcites)
			d[cat].nCitesMade[isq] += len(patn.cites)
			d[cat].nCitesRecd[isq] += len(patn.citedby)
		print
		
		# remove bum keys
		badCats = []
		for cat in d:
			if sum(d[cat].nPatns) < 10:	# total number of patns in that category < 10
				print "Bad cat:",cat,"only has",sum(d[cat].nPatns),"patents"
				badCats.append(cat)
		for cat in badCats:
			del(d[cat])
				# TODO maybe a bit arbitrary, but spot checks have supported it
		# TODO need to deal with these or they'll error later
		r = range(nQuarters)
		for dc in d.itervalues():
			n = dc.nPatns
			dc.avgRawCitesMade = [(1.0 * dc.nRawCitesMade[isq] / n[isq]) if dc.nRawCitesMade[isq] > 0 else 0 for isq in r]
			dc.avgCitesMade = [(1.0 * dc.nCitesMade[isq] / n[isq]) if dc.nCitesMade[isq] > 0 else 0 for isq in r]
			dc.avgCitesRecd = [(1.0 * dc.nCitesRecd[isq] / n[isq]) if dc.nCitesRecd[isq] > 0 else 0 for isq in r]
