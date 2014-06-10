#check the data for every patent that shows up in the log
#   maybe the patent after them too
#   or buffer the patn search
#BUGBUG look into pickling again (highest protocol slowest? cause it's slow as **fuck**)
#fewer lines in poolsize
#nPatnsEachIPC-A needs labels -- cumhits!
#make a bunch of the perQuarter graphs peryear
#   esp. nisdPerQuarter
#make dictQ FIFO to make auditting easier
#   -> figure out why totals aren't right!
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
from numpy import array, unique

fnLog = 'patents.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"

if not 'patns' in dir():    # assume this is first time running
    # don't overwrite patns!
    patns = dict()
    # no need to re-run logging config
    logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)
    # purposely leave errorQ untouched on rerun, ditto filelists
    fileQ = multiprocessing.JoinableQueue()
    dictQ = multiprocessing.JoinableQueue()
    errorQ = multiprocessing.JoinableQueue()
    #   xmlfilelist = [XMLParser.fr + x for x in os.listdir(XMLParser.fr) if x[-4:] == '.xml']
    #   datfilelist = [DATParser.fr + x for x in os.listdir(DATParser.fr) if x[-4:] == '.dat']
    xmlfilelist = []
    #   DATParser.fr = './'
    #   datfilelist = [DATParser.fr + x for x in ['2000.dat', '2001.dat']]
    datfilelist = [DATParser.fr + x for x in ['1976.dat', '1977.dat', '1978.dat', '1979.dat', '1980.dat', '1981.dat', '1982.dat', '1983.dat', '1984.dat', '1985.dat', '1986.dat', '1987.dat', '1988.dat', '1989.dat', '1990.dat', '1991.dat', '1992.dat', '1993.dat', '1994.dat', '1995.dat', '1996.dat', '1997.dat', '1998.dat', '1999.dat', '2000.dat', '2001.dat']]

else:
    logging.info('Found existing patns dict, continuing')

# because having trouble with exec('checkCoverage.py')...
def checkCoverage(patns):
    checkXMLs = {\
    'ipgb20050104' : 6836899,\
    'ipgb20050111' : 6839904,\
    'ipgb20050118' : 6842908,\
    'ipgb20050125' : 6845513,\
    'ipgb20050201' : 6848118,\
    'ipgb20050208' : 6851123,\
    'ipgb20050215' : 6854128,\
    'ipgb20050222' : 6857133,\
    'ipgb20050301' : 6859938,\
    'ipgb20050308' : 6862743,\
    'ipgb20050315' : 6865748,\
    'ipgb20050322' : 6868553,\
    'ipgb20050329' : 6871357,\
    'ipgb20050405' : 6874162,\
    'ipgb20050412' : 6877167,\
    'ipgb20050419' : 6880172,\
    'ipgb20050426' : 6883177,\
    'ipgb20050503' : 6886182,\
    'ipgb20050510' : 6889387,\
    'ipgb20050517' : 6892392,\
    'ipgb20050524' : 6895597,\
    'ipgb20050531' : 6898802,\
    'ipgb20050607' : 6901607,\
    'ipgb20050614' : 6904612,\
    'ipgb20050621' : 6907617,\
    'ipgb20050628' : 6910222,\
    'ipgb20050705' : 6912727,\
    'ipgb20050712' : 6915532,\
    'ipgb20050719' : 6918137,\
    'ipgb20050726' : 6920642,\
    'ipgb20050802' : 6922847,\
    'ipgb20050809' : 6925652,\
    'ipgb20050816' : 6928657,\
    'ipgb20050823' : 6931662,\
    'ipgb20050830' : 6934967,\
    'ipgb20050906' : 6938272,\
    'ipgb20050913' : 6941577,\
    'ipgb20050920' : 6944882,\
    'ipgb20050927' : 6948187,\
    'ipgb20051004' : 6951032,\
    'ipgb20051011' : 6952837,\
    'ipgb20051018' : 6954942,\
    'ipgb20051025' : 6957447,\
    'ipgb20051101' : 6959452,\
    'ipgb20051108' : 6961957,\
    'ipgb20051115' : 6964062,\
    'ipgb20051122' : 6966067,\
    'ipgb20051129' : 6968572,\
    'ipgb20051206' : 6971122,\
    'ipgb20051213' : 6973672,\
    'ipgb20051220' : 6976272,\
    'ipgb20051227' : 6978477,\
    'ipgb20060103' : 6981282,\
    'ipgb20060110' : 6983487,\
    'ipgb20060117' : 6986162,\
    'ipgb20060124' : 6988281,\
    'ipgb20060131' : 6990686,\
    'ipgb20060207' : 6993791,\
    'ipgb20060214' : 6996846,\
    'ipgb20060221' : 7000251,\
    'ipgb20060228' : 7003801,\
    'ipgb20060307' : 7007306,\
    'ipgb20060314' : 7010811,\
    'ipgb20060321' : 7013486,\
    'ipgb20060328' : 7017191,\
    'ipgb20060404' : 7020896,\
    'ipgb20060411' : 7024701,\
    'ipgb20060418' : 7028341,\
    'ipgb20060425' : 7032246,\
    'ipgb20060502' : 7036151,\
    'ipgb20060509' : 7039956,\
    'ipgb20060516' : 7043761,\
    'ipgb20060523' : 7047566,\
    'ipgb20060530' : 7051371,\
    'ipgb20060606' : 7055176,\
    'ipgb20060613' : 7058981,\
    'ipgb20060620' : 7062786,\
    'ipgb20060627' : 7065791,\
    'ipgb20060704' : 7069596,\
    'ipgb20060711' : 7073201,\
    'ipgb20060718' : 7076806,\
    'ipgb20060725' : 7080411,\
    'ipgb20060801' : 7082616,\
    'ipgb20060808' : 7086091,\
    'ipgb20060815' : 7089596,\
    'ipgb20060822' : 7093301,\
    'ipgb20060829' : 7096506,\
    'ipgb20060905' : 7100211,\
    'ipgb20060912' : 7103916,\
    'ipgb20060919' : 7107621,\
    'ipgb20060926' : 7111326,\
    'ipgb20061003' : 7114186,\
    'ipgb20061010' : 7117536,\
    'ipgb20061017' : 7120936,\
    'ipgb20061024' : 7124446,\
    'ipgb20061031' : 7127746,\
    'ipgb20061107' : 7131146,\
    'ipgb20061114' : 7134146,\
    'ipgb20061121' : 7137146,\
    'ipgb20061128' : 7140046,\
    'ipgb20061205' : 7143446,\
    'ipgb20061212' : 7146646,\
    'ipgb20061219' : 7150046,\
    'ipgb20061226' : 7152246,\
    'ipgb20070102' : 7155746,\
    'ipgb20070109' : 7159246,\
    'ipgb20070116' : 7162746,\
    'ipgb20070123' : 7165270,\
    'ipgb20070130' : 7168095,\
    'ipgb20070206' : 7171695,\
    'ipgb20070213' : 7174570,\
    'ipgb20070220' : 7178170,\
    'ipgb20070227' : 7181770,\
    'ipgb20070306' : 7185370,\
    'ipgb20070313' : 7188370,\
    'ipgb20070320' : 7191470,\
    'ipgb20070327' : 7194770,\
    'ipgb20070403' : 7197770,\
    'ipgb20070410' : 7200870,\
    'ipgb20070417' : 7203970,\
    'ipgb20070424' : 7207070,\
    'ipgb20070501' : 7210170,\
    'ipgb20070508' : 7213270,\
    'ipgb20070515' : 7216370,\
    'ipgb20070522' : 7219370,\
    'ipgb20070529' : 7222370,\
    'ipgb20070605' : 7225470,\
    'ipgb20070612' : 7228570,\
    'ipgb20070619' : 7231670,\
    'ipgb20070626' : 7234170,\
    'ipgb20070703' : 7237270,\
    'ipgb20070710' : 7240370,\
    'ipgb20070717' : 7243375,\
    'ipgb20070724' : 7246380,\
    'ipgb20070731' : 7249385,\
    'ipgb20070807' : 7251835,\
    'ipgb20070814' : 7254840,\
    'ipgb20070821' : 7257845,\
    'ipgb20070828' : 7260850,\
    'ipgb20070904' : 7263725,\
    'ipgb20070911' : 7266850,\
    'ipgb20070918' : 7269855,\
    'ipgb20070925' : 7272860,\
    'ipgb20071002' : 7275265,\
    'ipgb20071009' : 7278170,\
    'ipgb20071016' : 7281275,\
    'ipgb20071023' : 7284280,\
    'ipgb20071030' : 7287285,\
    'ipgb20071106' : 7290290,\
    'ipgb20071113' : 7293295,\
    'ipgb20071120' : 7296300,\
    'ipgb20071127' : 7299505,\
    'ipgb20071204' : 7302710,\
    'ipgb20071211' : 7305715,\
    'ipgb20071218' : 7308719,\
    'ipgb20071225' : 7310824,\
    'ipgb20080101' : 7313829,\
    'ipgb20080108' : 7316034,\
    'ipgb20080115' : 7318239,\
    'ipgb20080122' : 7320144,\
    'ipgb20080129' : 7322049,\
    'ipgb20080205' : 7325254,\
    'ipgb20080212' : 7328459,\
    'ipgb20080219' : 7331064,\
    'ipgb20080226' : 7334269,\
    'ipgb20080304' : 7337474,\
    'ipgb20080311' : 7340779,\
    'ipgb20080318' : 7343629,\
    'ipgb20080325' : 7346934,\
    'ipgb20080401' : 7350239,\
    'ipgb20080408' : 7353544,\
    'ipgb20080415' : 7356849,\
    'ipgb20080422' : 7360254,\
    'ipgb20080429' : 7363659,\
    'ipgb20080506' : 7367064,\
    'ipgb20080513' : 7370368,\
    'ipgb20080520' : 7373673,\
    'ipgb20080527' : 7376978,\
    'ipgb20080603' : 7380283,\
    'ipgb20080610' : 7383588,\
    'ipgb20080617' : 7386893,\
    'ipgb20080624' : 7389543,\
    'ipgb20080701' : 7392548,\
    'ipgb20080708' : 7395553,\
    'ipgb20080715' : 7398558,\
    'ipgb20080722' : 7401363,\
    'ipgb20080729' : 7404213,\
    'ipgb20080805' : 7406718,\
    'ipgb20080812' : 7409723,\
    'ipgb20080819' : 7412728,\
    'ipgb20080826' : 7415733,\
    'ipgb20080902' : 7418738,\
    'ipgb20080909' : 7421743,\
    'ipgb20080916' : 7424748,\
    'ipgb20080923' : 7426753,\
    'ipgb20080930' : 7428758,\
    'ipgb20081007' : 7430763,\
    'ipgb20081014' : 7434268,\
    'ipgb20081021' : 7437773,\
    'ipgb20081028' : 7441278,\
    'ipgb20081104' : 7444683,\
    'ipgb20081111' : 7448088,\
    'ipgb20081118' : 7451493,\
    'ipgb20081125' : 7454798,\
    'ipgb20081202' : 7458103,\
    'ipgb20081209' : 7461408,\
    'ipgb20081216' : 7464413,\
    'ipgb20081223' : 7467418,\
    'ipgb20081230' : 7469423,\
    'ipgb20090106' : 7472428,\
    'ipgb20090113' : 7475433,\
    'ipgb20090120' : 7478438,\
    'ipgb20090127' : 7480943,\
    'ipgb20090203' : 7484248,\
    'ipgb20090210' : 7487553,\
    'ipgb20090217' : 7490358,\
    'ipgb20090224' : 7493663,\
    'ipgb20090303' : 7496968,\
    'ipgb20090310' : 7500273,\
    'ipgb20090317' : 7503078,\
    'ipgb20090324' : 7506383,\
    'ipgb20090331' : 7509688,\
    'ipgb20090407' : 7512993,\
    'ipgb20090414' : 7516498,\
    'ipgb20090421' : 7520003,\
    'ipgb20090428' : 7523508,\
    'ipgb20090505' : 7526813,\
    'ipgb20090512' : 7530118,\
    'ipgb20090519' : 7533423,\
    'ipgb20090526' : 7536728,\
    'ipgb20090602' : 7540033,\
    'ipgb20090609' : 7543338,\
    'ipgb20090616' : 7546643,\
    'ipgb20090623' : 7549178,\
    'ipgb20090630' : 7552483,\
    'ipgb20090707' : 7555788,\
    'ipgb20090714' : 7559093,\
    'ipgb20090721' : 7562398,\
    'ipgb20090728' : 7565703,\
    'ipgb20090804' : 7568238,\
    'ipgb20090811' : 7571493,\
    'ipgb20090818' : 7574748,\
    'ipgb20090825' : 7578003,\
    'ipgb20090901' : 7581258,\
    'ipgb20090908' : 7584513,\
    'ipgb20090915' : 7587768,\
    'ipgb20090922' : 7591023,\
    'ipgb20090929' : 7594278,\
    'ipgb20091006' : 7596813,\
    'ipgb20091013' : 7600268,\
    'ipgb20091020' : 7603723,\
    'ipgb20091027' : 7607178,\
    'ipgb20091103' : 7610633,\
    'ipgb20091110' : 7614088,\
    'ipgb20091117' : 7617543,\
    'ipgb20091124' : 7620998,\
    'ipgb20091201' : 7624453,\
    'ipgb20091208' : 7627908,\
    'ipgb20091215' : 7631363,\
    'ipgb20091222' : 7634818,\
    'ipgb20091229' : 7636948,\
    'ipgb20100105' : 7640598,\
    'ipgb20100112' : 7644448,\
    'ipgb20100119' : 7647648,\
    'ipgb20100126' : 7650648,\
    'ipgb20100202' : 7653948,\
    'ipgb20100209' : 7657948,\
    'ipgb20100216' : 7661148,\
    'ipgb20100223' : 7665148,\
    'ipgb20100302' : 7669248,\
    'ipgb20100309' : 7673348,\
    'ipgb20100316' : 7676848,\
    'ipgb20100323' : 7681248,\
    'ipgb20100330' : 7685648,\
    'ipgb20100406' : 7690048,\
    'ipgb20100413' : 7694348,\
    'ipgb20100420' : 7698748,\
    'ipgb20100427' : 7703148,\
    'ipgb20100504' : 7707648,\
    'ipgb20100511' : 7712148,\
    'ipgb20100518' : 7716748,\
    'ipgb20100525' : 7721348,\
    'ipgb20100601' : 7725948,\
    'ipgb20100608' : 7730548,\
    'ipgb20100615' : 7735148,\
    'ipgb20100622' : 7739748,\
    'ipgb20100629' : 7743428,\
    'ipgb20100706' : 7748053,\
    'ipgb20100713' : 7752678,\
    'ipgb20100720' : 7757303,\
    'ipgb20100727' : 7761928,\
    'ipgb20100803' : 7765608,\
    'ipgb20100810' : 7770233,\
    'ipgb20100817' : 7774858,\
    'ipgb20100824' : 7779483,\
    'ipgb20100831' : 7784108,\
    'ipgb20100907' : 7788733,\
    'ipgb20100914' : 7793358,\
    'ipgb20100921' : 7797758,\
    'ipgb20100928' : 7802313,\
    'ipgb20101005' : 7805767,\
    'ipgb20101012' : 7810167,\
    'ipgb20101019' : 7814567,\
    'ipgb20101026' : 7818817,\
    'ipgb20101102' : 7823217,\
    'ipgb20101109' : 7827617,\
    'ipgb20101116' : 7832017,\
    'ipgb20101123' : 7836517,\
    'ipgb20101130' : 7841017,\
    'ipgb20101207' : 7845017,\
    'ipgb20101214' : 7849517,\
    'ipgb20101221' : 7854017,\
    'ipgb20101228' : 7856667,\
    }
    checkd = {1976:3930271, 1977:4000520, 1978:4065812, 1979:4131952,\
        1980:4180867, 1981:4242757, 1982:4308622, 1983:4366579, 1984:4423523,\
        1985:4490855, 1986:4562596, 1987:4633526, 1988:4716594, 1989:4794652,\
        1990:4890335, 1991:4980927, 1992:5077836, 1993:5175886, 1994:5274846,\
        1995:5377359, 1996:5479658, 1997:5590420, 1998:5704062, 1999:5855021,\
        2000:6009555, 2001:6167569, 2002:6334220, 2003:6502244, 2004:6671884}
    checkd.update(checkXMLs)
    nGood = 0
    missing = []
    for check in checkd:
        if not patns.has_key(checkd[check]):
            logging.error('Missing %d from %s', checkd[check], str(check))
            print 'Missing', checkd[check], 'from', check
            missing.append(check)
        else:
            nGood += 1
    if nGood == len(checkd):
        logging.info('Coverage good for %d', nGood)
        print 'Coverage good for', nGood
    else:
        return missing


def loadPatnFiles(patns, fl):
    logging.info("Started read at %s", time.strftime("%X %x"))
    tStart = time.time()
    workerProcesses = []
    
    map(fileQ.put, fl)
    
    def work(fQ, dQ, eQ):
        xmlp = XMLParser.XMLParser()
        datp = DATParser.DATParser()
        
        while not fQ.empty():
            fp = fQ.get()
            if fp[-4:] == '.xml':
                parser = xmlp
            else:
                parser = datp
            logging.info("Parsing %s", os.path.basename(fp))
            try:
                dpatns,badpatns = parser.parseFile(fp)
                logging.info("%d (%d bad) found in %s", len(dpatns), len(badpatns), os.path.basename(fp))
                dQ.put(dpatns)
                parser.patns = dict()   # toss old patns
                # BUGBUG tossing bad patns instead of dealing with them
                parser.badpatns = dict()
            except:
                logging.error("Error parsing %s", os.path.basename(fp), exc_info=True)
                eQ.put(fp)
            fQ.task_done()
        #dictQ.close()
        logging.info("Worker finished.")
        
    for i in range(0, multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=work, args=(fileQ, dictQ, errorQ))
        p.daemon = True
        p.start()
        workerProcesses.append(p)
        
    while True in map(multiprocessing.Process.is_alive, workerProcesses) or not dictQ.empty():
        try:
            dpatns = dictQ.get(timeout=1)
            patns.update(dpatns)
            dictQ.task_done()
            logging.info("patns now %d", len(patns))
        except Queue.Empty:
            pass
            
    # all workers are done, join up extraneous queues and such
    for p in workerProcesses:
        p.join()
    fileQ.join()    # should be instant as workers are already done
    dictQ.join()
    #if not dictQ.empty():  logging.error("dictQ not empty before close!")
    #dictQ.close()
    #dictQ.join_thread()
    logging.info("done reading files after %.2f minutes.", (time.time()-tStart)/60)

def sanityCheck(patns):
    # misc cleanup
    def handFix(patns):
        # bad, but fixable, apds
        if 3943504 in patns:
            patns[3943504].apd = datetime.date(1975, 2, 25) # not 2975
        if 3964954 in patns:
            patns[3964954].apd = datetime.date(1973, 5, 31) # not 9173
        if 3969699 in patns:
            patns[3969699].apd = datetime.date(1975, 4, 11) # not 9175
        if 4010353 in patns:
            patns[4010353].apd = datetime.date(1974, 9, 11) # not 9174
        if 4020425 in patns:
            patns[4020425].apd = datetime.date(1976, 3, 26) # not 2976
        if 4032532 in patns:
            patns[4032532].apd = datetime.date(1973, 3, 1) # not 9173
        if 4041523 in patns:
            patns[4041523].apd = datetime.date(1976, 6, 1) # not 9176
        if 4135654 in patns:
            patns[4135654].apd = datetime.date(1977, 4, 11) # not 9177
        if 4198308 in patns:
            patns[4198308].apd = datetime.date(1978, 7, 21) # not 7978
        if 4255928 in patns:
            patns[4255928].apd = datetime.date(1978, 12, 11) # not 9178
        if 4474874 in patns:
            patns[4474874].apd = datetime.date(1983, 3, 11) # not 9183
        if 4542062 in patns:
            patns[4542062].apd = datetime.date(1982, 1, 20) # not 2982
        if 4596904 in patns:
            patns[4596904].apd = datetime.date(1984, 5, 25) # not 2984
        if 4709214 in patns:
            patns[4709214].apd = datetime.date(1986, 4, 28) # not 2986
        if 4725260 in patns:
            patns[4725260].apd = datetime.date(1987, 3, 24) # not 2987
        if 4732727 in patns:
            patns[4732727].apd = datetime.date(1986, 4, 3) # not 9186
        if 4739365 in patns:
            patns[4739365].apd = datetime.date(1987, 5, 28) # not 2987
        for pno in [3943504, 3964954, 3969699, 4010353, 4020425, 4032532, 4041523, 4135654, 4198308,\
            4255928, 4474874, 4542062, 4596904, 4709214, 4725260, 4732727, 4739365]:
            if pno in patns:
                patns[pno].apq = Patent.d2q(patns[pno].apd)
            
        # datetime.date(8198, 4, 5) ???? even on patn image!
            if 4469216 in patns:
                if hasattr(patns[4469216], 'apd'):
                    del(patns[4469216].apd, patns[4469216].apq)
            
        # the only bad (missing) TTL
        # b/c missing title, not included by current scripts
        # patns[5001050].title = 'PH.phi.29 DNA polymerase'
        # end handfix

    missing = checkCoverage(patns)
    handFix(patns)
    #for patn in patns.itervalues():
    #   if 
    # ipcs
    # <main-group/> : 89 from 2005 - 20101228
    
def populateCites(patns):
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


logging.info("-------------------------------------")
logging.info("$Id: readPatnsFromFiles.py 293 2011-04-04 20:45:34Z andy $")

#xmlfilelist = [frXML + 'ipgb20081104.xml', frXML + 'ipgb20091215.xml']
#datfilelist = [datfilelist[-1]]
#xmlfilelist = ['test.xml']
#datfilelist = ['test.dat']
print 'loading...'
loadPatnFiles(patns, xmlfilelist + datfilelist)
print 'sanity...'
sanityCheck(patns)
print 'cites...'
populateCites(patns)

#########################################################
# Load the tfidf stuff

import sys
sys.path = sys.path+['../gensim/']
from gensim.corpora import Dictionary,MmCorpus
import pickle as pk
logging.info("-------------------------------------")
logging.info("loading dictionary and corpus")
tStart=time.time()
dic = Dictionary.load('trim1000.dic')
corp = MmCorpus('tfidftrim1kall__tfidf.mm')
logging.info("done after %.2f minutes.", (time.time()-tStart)/60.0)
logging.info("loading patnums")
tStart=time.time()
patnums = pk.load(open('patnums.pickle'))
patnums = array(patnums)
logging.info("done after %.2f minutes.", (time.time()-tStart)/60.0)

logging.info("putting the tfidf info into the patns...")
tStart=time.time()

i = -1
cntgot=0
cntnotgot = 0
newkeys = []
for k in patnums:
    i += 1
    try:
        patns[k]
        patns[k].tfidf = corp[i]
        cntgot +=1
        newkeys.append(k)
    except:
        cntnotgot += 1
logging.info("done after %.2f minutes.", (time.time()-tStart)/60)
logging.info("got %d, skipped %d not in patns or without tfidf",cntgot, cntnotgot)

# <codecell>
logging.info("%d duplicates keys",len(newkeys)-len(unique(newkeys)))
newkeys = unique(newkeys)
logging.info("%d unique keys stored in newkeys",len(newkeys))

