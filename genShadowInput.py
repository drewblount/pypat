fo = open('pnodatecitesweight.txt', 'w')
for patn in patns.itervalues():
    # pno, quarter isd, number of cites made, initial weight
    fo.write("%d %d %d %d\n" % (patn.pno, Patent.d2q(patn.isd), len(patn.cites), len(patn.citedby)))
fo.close()
