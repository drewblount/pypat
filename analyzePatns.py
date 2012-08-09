# requires patns to be around somehow
import os, time, logging
import PerQuarter, CatInfo

logging.info("Started analysis at %s", time.strftime("%X %x"))
tStart = time.time()
# now some random, but generally useful stuff
# nQuarters gets used a lot
minPatn = patns[min(patns)]
maxPatn = patns[max(patns)]
#nQuarters = maxPatn.isq - minPatn.isq + 1
# might as well set manually, necessary for testing
nQuarters = 140

topPatn = max(patns.values(), key=lambda p: len(p.citedby))
# 4683202 (PCR) at time of writing

perQuarter = PerQuarter.PerQuarter(nQuarters)	# general info about the dataset
perQuarter.Stats(patns, nQuarters)
catInfo = CatInfo.CatInfo(patns, nQuarters)	# category based info about the dataset

# gawk '/^.../ {printf("%s\n",substr($0,0,3))}' ipcr_treenodes_20* | sort | uniq > A00.txt
for cat in catInfo.A.keys():
	if cat not in 'ABCDEFGH':
		logging.info('Deleting category',cat)
		del(catInfo.A[cat])

validA00 = ['A01', 'A21', 'A22', 'A23', 'A24', 'A41', 'A42', 'A43', 'A44', 'A45', 'A46', 'A47',\
 	'A61', 'A62', 'A63', 'A99', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09',\
 	'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B28', 'B29', 'B30', 'B31', 'B32', 'B41',\
 	'B42', 'B43', 'B44', 'B60', 'B61', 'B62', 'B63', 'B64', 'B65', 'B66', 'B67', 'B68', 'B81',\
 	'B82', 'B99', 'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11',\
 	'C12', 'C13', 'C14', 'C21', 'C22', 'C23', 'C25', 'C30', 'C40', 'C99', 'D01', 'D02', 'D03',\
 	'D04', 'D05', 'D06', 'D07', 'D21', 'D99', 'E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E21',\
 	'E99', 'F01', 'F02', 'F03', 'F04', 'F15', 'F16', 'F17', 'F21', 'F22', 'F23', 'F24', 'F25',\
 	'F26', 'F27', 'F28', 'F41', 'F42', 'F99', 'G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07',\
 	'G08', 'G09', 'G10', 'G11', 'G12', 'G21', 'G99', 'H01', 'H02', 'H03', 'H04', 'H05', 'H99']
for cat in catInfo.A00.keys():
	if cat not in validA00:
		logging.info('Deleting category',cat,'with',sum(catInfo.A00[cat].nPatns),'patns')
		del(catInfo.A00[cat])

logging.info("done after %.2f minutes.", (time.time()-tStart)/60)
