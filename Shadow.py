import random, collections

#ShadowPatent = collections.namedtuple('ShadowPatent', 'citedby')

spatns = dict()
for patn in patns.itervalues():
	# don't need to cover edge cases like first patn bc cites will be empty
	for i in xrange(len(patn.cites)):
		rpno = random.randint(minPatn.pno, patn.pno-1)
		while not patns.has_key(rpno):
			# get a valid pno (shouldn't take long)
			rpno = random.randint(minPatn.pno, patn.pno-1)
		if not spatns.has_key(rpno):
			spatns[rpno] = []
		spatns[rpno].append(patn.pno)

# get the top 100 shadow patns
topSPatns = sorted(spatns.values(), key=lambda p: len(p))[-100:]

def ShAct(citedby):
	actaccum = [0] * nQuarters
	for citingPatnNo in citedby:
		actaccum[patns[citingPatnNo].isq] += 1
	return Patent.Cumulate(actaccum)

topShActs = []
c = 1
for spatn in topSPatns:
	# include dummy title (can't duplicate)
	c+=1
	topShActs.append([c] + ShAct(spatn))

mylib.CHs2File(topShActs,'TopShadowActivity.data')

print '\a\a\a'
