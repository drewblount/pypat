# Simply fixes typos in the year fields of some patents, assuming
# the database has already been built.

# Note that client, dbname, and db are all parameters which might
# differ depending on the implementation

from pymongo import MongoClient

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patents = client[dbname]['patns']

# format is (pno, correctDateInDateTime)

fixes = [
		 (3943504, datetime.datetime(1975, 2, 25, 0, 0, 0)), # not 2975
		 (3964954, datetime.datetime(1973, 5, 31, 0, 0, 0)), # not 9173
		 (3969699, datetime.datetime(1975, 4, 11, 0, 0, 0)), # not 9175
		 (4010353, datetime.datetime(1974, 9, 11, 0, 0, 0)), # not 9174
		 (4020425, datetime.datetime(1976, 3, 26, 0, 0, 0)), # not 2976
		 (4032532, datetime.datetime(1973, 3, 1,  0, 0, 0)), # not 9173
		 (4041523, datetime.datetime(1976, 6, 1,  0, 0, 0)), # not 9176
		 (4135654, datetime.datetime(1977, 4, 11, 0, 0, 0)), # not 9177
		 (4198308, datetime.datetime(1978, 7, 21, 0, 0, 0)), # not 7978
		 (4255928, datetime.datetime(1978, 12,11, 0, 0, 0)), # not 9178
		 (4474874, datetime.datetime(1983, 3, 11, 0, 0, 0)), # not 9183
		 (4542062, datetime.datetime(1982, 1, 20, 0, 0, 0)), # not 2982
		 (4596904, datetime.datetime(1984, 5, 25, 0, 0, 0)), # not 2984
		 (4709214, datetime.datetime(1986, 4, 28, 0, 0, 0)), # not 2986
		 (4725260, datetime.datetime(1987, 3, 24, 0, 0, 0)), # not 2987
		 (4732727, datetime.datetime(1986, 4, 3,  0, 0, 0)), # not 9186
		 (4739365, datetime.datetime(1987, 5, 28, 0, 0, 0))  # not 2987
		 ]

for fix in fixes:
	patents.update({ 'pno': fix[0] },
				   { '$set': { 'apd': fix[1]}})