import logging
import Patent

# Top Activity Normalized (tan) graphs
logging.info("Started at %s", time.strftime("%H:%M"))
tStart = time.time()

# Normalizing for changing citation rate practices
inflCurve=[perQuarter.avgRawCitesMade[-1]/qAvg for qAvg in perQuarter.avgRawCitesMade]
# choice of avgRawCitesMade instead of avgCitesMade is conscious
# makes the math cleaner (no accounting for =0 in 1976), and more historically accurate

# hits are adjusted up to modern day hits (i.e., boost <today hits)
def tanModernHits(citingPatn):
	return inflCurve[citingPatn.isq]

# highest avg rate at the end of the dataset
maxPQCat = sorted(catInfo.A00.values(), key=lambda pqCat: pqCat.avgRawCitesMade[-1])[-1]
maxCat = maxPQCat.cat
logging.info('IPC baseline category: %s', maxCat)
print 'IPC baseline category:', maxCat
maxIpcAvg = max(maxPQCat.avgRawCitesMade)
for pqCat in catInfo.A00.itervalues():
	pqCat.inflCurve = [maxIpcAvg/ipcqAvg if ipcqAvg>0 else 0 for ipcqAvg in pqCat.avgRawCitesMade]
	#pqCat.inflCurve = [0] * nQuarters
	#for i in range(nQuarters):
	#	if pqCat.avgRawCitesMade[i] <= 0.0:
	#		continue
	#	pqCat.inflCurve[i] = maxIpcAvg/pqCat.avgRawCitesMade[i]

def tanIPCModernHits(citingPatn):
	#if citingPatn in badIpcs: return 0
	try:
		return catInfo.A00[citingPatn.ipc[0:3]].inflCurve[citingPatn.isq]
	except:
		return 0

# normalization based on how many patents were out there to potentially be hit
# a hit in modern times (largest pool) is worth 1,
# a hit in '76 (smallest pool) is worth ~0.5
poolCurve = [1.0*poolSize/perQuarter.cumIsd[-1] for poolSize in perQuarter.cumIsd]
def tanPoolSize(citingPatn):
	return poolCurve[citingPatn.isq]

# Weighting hits from different IPCs more
def ipcSplit(ipc):
	if ipc[7] == '/':
		return [ipc[0], ipc[1:3], ipc[3], ipc[4:7], ipc[8:]]
		#return [ipc[0], int(ipc[1:3]), ipc[3], int(ipc[4:7]), int(ipc[8:])]
	else:
		return [ipc[0], ipc[1:3], ipc[3], ipc[4:7], ipc[7:]]
		#return [ipc[0], int(ipc[1:3]), ipc[3], int(ipc[4:7]), int(ipc[7:])]

def tanIPCDistance(citingPatn, patn):
	# five matches is max possible
	#if citingPatn in badIpcs or patn in badIpcs:
	#	return 0
	
	matches = 6 # one more than hierarchy so even patents w/same class count a little
	#try:
	l = zip(ipcSplit(citingPatn.ipc), ipcSplit(patn.ipc))
	#except:
	#	return 0
	for p,cp in l:
		if p == cp: matches -= 1
		else: break
	return matches


def tanExpIPCDistance(citingPatn, patn):
	# five matches is max possible
	#if citingPatn in badIpcs or patn in badIpcs:
	#	return 0
	
	weight = 2**5
	#try:
	l = zip(ipcSplit(citingPatn.ipc), ipcSplit(patn.ipc))
	#except:
	#	noIpcSplit += 1
	#	return 0
	for p,cp in l:
		if p == cp: weight /= 2
		else: break
	return weight

# weighting by whether citing patent shares assignee
ding = 0.33
def tanIncest(citingPatn, patn):
	if hasattr(patn,'assignee') and hasattr(citingPatn, 'assignee')\
	 and patn.assignee == citingPatn.assignee:
		return ding
	return 1

def tanModernAndIncest(citingPatn, patn):
	return tanIPCModernHits(citingPatn) * tanIncest(citingPatn, patn)

def tanModernAndExpIPC(citingPatn, patn):
	return tanIPCModernHits(citingPatn) * tanExpIPCDistance(citingPatn, patn)

# a combination of PoolSize and IPCiteRate
def tanPrior(citingPatn, patn):
	if patn.pno < 4065812: return 0
	return 1.0/perQuarter.cumCitesPerPatn[citingPatn.isq]

def add(x,y): return x+y

def TotalHits(patn, f):
	'''Just does a quick check of the patent's cummulative hits in 2007'''
	return reduce(add, [f(patns[cPatnNo], patn) for cPatnNo in patn.citedby], 0)


def Activity(patn, f):
	'''Returns the patent's cumulative hits, weighted via f(patn, citingPatn)'''
	act = [0] * nQuarters
	
	for citingPatnNo in patn.citedby:
		act[patns[citingPatnNo].isq] += f(patns[citingPatnNo], patn)
	
	return Patent.Cumulate(act)
	#ch = [0] * nQuarters
	#accum = 0
	#for qi in range(len(act)):
	#	accum += act[qi]
	#	ch[qi] = accum
	#return ch

Nfuncs = [tanIPCModernHits, tanModernAndIncest, tanModernAndExpIPC]# tanModernHits, tanExpIPCDistance, tanIncest, tanPoolSize, tanIPCDistance]
Rfuncs = dict()
for func in Nfuncs:
	if func.func_code.co_argcount == 2: f = func
	else:
		def f(citingPatn, patn): return func(citingPatn)
	Rfuncs[func] = f

pcrTopPatn = patns[4683202]
actThreshes = dict()
scaling = dict()
for func in Nfuncs:	
	act = Activity(pcrTopPatn, Rfuncs[func])
	actThreshes[func] = 0.1 * TotalHits(pcrTopPatn, Rfuncs[func])
	print func.__name__, actThreshes[func]
	#actThreshes[func] = 0.8 * act[-1]
	#scaling[func] = 100.0/act[-1]


#topPatns = sorted(patns.values(), key=lambda p: p.Activity(patns)[-1], reverse=True)[0:1000000]
#topPatns.sort(key=lambda x: x.pno)	# sort by pno as proxy for date
results = dict()
for func in Nfuncs:
	print func.__name__
	logging.info(func.__name__)
	results[func] = []

	for patn in patns.itervalues():#topPatns:
		if patn.pno % 100000 == 0:
			print '\r',patn.pno,
		
		if TotalHits(patn, Rfuncs[func]) >= actThreshes[func]:
			act = Activity(patn, Rfuncs[func])
			results[func].append([str(patn.pno)+' '+patn.title] + act) # save pno too
	print
	# sort by num of hits, then just take 100
	results[func] = sorted(results[func], key=lambda x: x[-1], reverse=True)[0:100]
	results[func].sort(key=lambda x: x[0]) # then sort by first element (pno)
	if 'ncest' in func.__name__:
		mylib.CHs2File(results[func], func.__name__ + "-" + str(ding).replace('.', '-') + ".data")
	else:
		mylib.CHs2File(results[func], func.__name__ + ".data")	

print 'tanall'
logging.info('tanall')
resultsAll = []
#[4313124, 4340563, 4345262, 4459600, 4463359, 4558333, 4683195, 4683202, 4723129,\
# 4733665, 4740796, 4901307, 5103459, 5572643]:
for pno in []:
	patn = patns[pno]
#for patn in patns.values():
	act = [0] * nQuarters
	for func in Nfuncs:
		scact = [scaling[func]*x for x in Activity(patn, Rfuncs[func])]
		for i in range(len(scact)):	act[i] += scact[i]
	if act[-1] > 125: resultsAll.append([str(patn.pno)+' '+patn.title] + act) # save pno too

#CHs2File(resultsAll, "tanall.data")			


logging.info("done with TopAct after %.2f minutes.", ((time.time()-tStart)/60))
logging.info("Finished at %s", time.strftime("%H:%M"))
print "\a\a\a"
