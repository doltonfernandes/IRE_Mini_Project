import time
import json
import sys
import re
import os
from nltk.stem import PorterStemmer

start = time.time()
invertedIdxPath = sys.argv[1]
query = sys.argv[2]

docIdTitleMap = {}
with open(invertedIdxPath + '/titles.txt', 'r') as f:
	for line in f:
		lineSplitted = line.strip().split('-')
		docIdTitleMap[int(lineSplitted[0])] = '-'.join(lineSplitted[1:])

emptyQuery = {
	"title": [],
	"body": [],
	"infobox": [],
	"categories": [],
	"references": [],
	"links": [],
}

mapping = {}
for idx, i in enumerate(sorted(emptyQuery.keys())):
	mapping[i] = chr(97 + idx)

def getDocIds(word, c, invertedIdx):
	docIds = []
	if c == 'f':
		for d in invertedIdx:
			if int(d.split('f')[1]) > 0:
				docIds.append(int(d.split('a')[0]))
		return docIds

	for d in invertedIdx:
		if int(d.split(c)[1].split(chr(ord(c) + 1))[0]) > 0:
			docIds.append(int(d.split('a')[0]))

	return docIds

invertedIdxFiles = [ f for f in os.listdir(invertedIdxPath) if os.path.isfile(os.path.join(invertedIdxPath, f)) and f != 'titles.txt']

def getInvIdxFileName(w):
	for f in invertedIdxFiles:
		lowerW = f.split('.')[0].split('_')[0]
		upperW = f.split('.')[0].split('_')[1]
		if w >= lowerW and w <= upperW:
			return f
	return ""

def getInvertedIndex(w):
	fileName = getInvIdxFileName(w)
	if fileName == "":
		return []

	match = []
	with open(invertedIdxPath + '/' + fileName, 'r') as f:
		for line in f:
			if line.split('-')[0] == w:
				match = line.strip().split('-')[1:]
				break

	return match

ans = {}
stemmer = PorterStemmer()
if ':' not in query:
	query = re.findall(r"[\w']{1,}", query)
	query = list(set(query))

	for q in query:
		ans[q] = emptyQuery.copy()
		stemmedWord = stemmer.stem(q.lower())
		invertedIdx = getInvertedIndex(stemmedWord)
		for k in ans[q].keys():
			try:
				ans[q][k] = getDocIds(stemmedWord, mapping[k], invertedIdx)
			except:
				pass
else:
	queryFormatted = {}
	for k in emptyQuery.keys():
		if k[:1] + ':' in query:
			text = query.split(k[:1] + ':')[1]
			if ':' in text:
				text = text.split(':')[0][:-1]
			text = re.findall(r"[\w']{1,}", text)
			text = list(set(text))
			for w in text:
				try:
					queryFormatted[w].append(k)
				except:
					queryFormatted[w] = [k]

	for w in queryFormatted.keys():
		ans[w] = emptyQuery.copy()
		stemmedWord = stemmer.stem(w.lower())
		invertedIdx = getInvertedIndex(stemmedWord)
		for q in queryFormatted[w]:
			try:
				ans[w][q] = getDocIds(stemmedWord, mapping[q], invertedIdx)
			except:
				pass

for k in ans.keys():
	alldocs = set()
	for el in ans[k].keys():
		for i in ans[k][el]:
			alldocs.add(i)
	ans[k] = list(alldocs)

end = time.time()

for k in ans.keys():
	print(k, '---')
	for idd in ans[k]:
		print(str(idd) + ', ' + docIdTitleMap[idd])

print(end - start)