# Populates the patents' "citedby" lists

from pymongo import MongoClient

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patents = client[dbname]['patns']

logging.info("Started reverse at %s", time.strftime("%X %x"))
	tStart = time.time()


for citingPatn in patents.find():
	citingNo = citingPatn['pno']
	for citedPNo in citingPatn['rawcites'] :
		inDB = patents.find_one({'pno':citedPNo})
		if inDB:
			newCites, newCitedBy = inDB['cites']+[citingNo], inDB['citedby']+[citingNo]
			patents.update({ 'pno' : citedPNo},
						   {'$set' :
						   {'cites': newCites, 'citedby': newCitedBy} },
						   # (below:) stops looking once it finds citedPNo
						   {'multi':false})
