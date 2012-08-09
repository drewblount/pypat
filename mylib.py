frOutputData = 'html/data/'
firstYear = 1976

def rangef(start, stop, step):
	'''range function that can handle floats'''
	result = []
	while True:
		result.append(start)
		start = start+step
		if start>=stop:
			break
	return result

def Lines2File(ls, fn):
	with open(frOutputData + fn, 'w') as f:
		for l in ls:
			f.write(' '.join(map(str,l)) + '\n')

def CHs2File(chs, fn, yr=firstYear, perYr=4):
	with open(frOutputData + fn, 'w') as f:
		yrs = rangef(yr, yr + 1.0 * len(chs[0][1:]) / perYr, 1.0 / perYr)
		f.write(' ' + ' '.join(map(str, yrs)) + '\n')
		for ch in chs:
			f.write(' '.join(map(repr,ch)) + '\n')

def Dict2File(dic, fn):
	with open(frOutputData + fn, 'w') as f:
		# sorted to maintain ordering from one run to the next
		for a in sorted(dic.keys()):
			f.write(str(a) + ' ' + str(dic[a]) + '\n')
