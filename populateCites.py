# Populates the patents' "citedby" lists

from pymongo import MongoClient

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patents = client[dbname]['patns']

# Below doesn't work, not sure why, but I just made the index in the mongo shell
# TODO: ensure that the following ensure ensures the index
# patents.ensureIndex({'pno': 1})

# Load only the pno and rawcites from each patent
for citingPatn in patents.find({}, {'rawcites':1, 'pno':1}):
	citingNo = citingPatn['pno']
	# makes sure the patents can be quickly addressed by pnum
	for citedPNo in citingPatn['rawcites'] :
		patents.update({ 'pno' : citedPNo},
					   # adds citingNo to the array citedby
					   {'$push' : {'citedby': citingNo} } )
