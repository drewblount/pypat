# Populates the patents' "citedby" lists

from pymongo import MongoClient

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patents = client[dbname]['patns']

logging.info("Started reverse at %s", time.strftime("%X %x"))
	tStart = time.time()

# Load only the pno and rawcites from each patent
for citingPatn in patents.find({}, {'rawcites':1, 'pno':1}):
	citingNo = citingPatn['pno']
	# makes sure the patents can be quickly addressed by pnum
	patents.ensureIndex({'pno': 1})
	for citedPNo in citingPatn['rawcites'] :
		newCites, newCitedBy = inDB['cites']+[citingNo], inDB['citedby']+[citingNo]
			patents.update({ 'pno' : citedPNo},
				       # adds citingNo to the array citedby
				       {'$push' : {'citedby': citingNo}},
				       # stops looking for patents to update once citedPNo is found
				       {'multi':false})
