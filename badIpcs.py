import logging
badIpcs = []
for patn in patns.itervalues():
	if not hasattr(patn, 'ipc') or len(patn.ipc) < 9 or patn.ipc[0] not in catInfo.A\
	 	or patn.ipc[0:3] not in catInfo.A00:
		badIpcs.append(patn)
logging.info('Found %d bad ipcs', len(badIpcs))
