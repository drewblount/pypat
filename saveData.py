import mylib

topPatns = sorted(patns.values(), key=lambda p: p.Activity(patns)[-1], reverse=True)[0:100]
topPatnsAct = [[str(patn.pno)+' '+patn.title] + patn.Activity(patns) for patn in topPatns]
topPatnsAct.sort(key=lambda x: x[0])	# sort by pno as proxy for date
mylib.CHs2File(topPatnsAct, 'TopActivity.data')

mylib.Lines2File(perQuarter.avgAct, 'avgActPerQuarter.data')
mylib.Lines2File(perQuarter.avgActApd, 'avgActPerQuarterApd.data')

mylib.Lines2File([perQuarter.nPatns], 'nPatnsIsdEachQuarter.data')
cites = [perQuarter.avgCitesMade, perQuarter.avgRawCitesMade]
mylib.Lines2File(cites, 'avgNoCitesMade.data')
mylib.Dict2File(dict(zip(mylib.rangef(1976.0,2010.75,0.25),perQuarter.avgCitesRecd)), "avgModernAct.data")
#mylib.Lines2File([perQuarter.avgApdIsdLag], 'avgDaysBtwApdAndIsd.data')
#mylib.Lines2File([perQuarter.avgIsdCiteIsdDiff], 'avgDaysBtwPatnAndCiteMade.data')
#mylib.Lines2File([perQuarter.avgApdCiteIsdDiff], 'avgDaysBtwApdAndCiteMade.data')

mylib.Lines2File([cat.nPatns for cat in catInfo.A.itervalues()], 'nPatnsEachIPC-A.data')
mylib.Lines2File([cat.avgCitesMade for cat in catInfo.A.itervalues()], 'avgCitesMadeEachIPC-A.data')
mylib.Lines2File([cat.avgCitesRecd for cat in catInfo.A.itervalues()], 'avgCitesRecdEachIPC-A.data')

#mylib.Dict2File(A00["tot"], 'nPatnsEachIPC-A00.data')
#mylib.Dict2File(A00["avgMade"], 'avgCitesMadeEachIPC-A00.data')
#mylib.Dict2File(A00["avgRecd"], 'avgCitesRecdEachIPC-A00.data')
