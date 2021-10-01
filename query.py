import os
import re
import sys
import time
import math
import pickle
import linecache as lc
from nltk.stem import PorterStemmer
from collections import defaultdict

start = time.time()
invertedIdxPath = sys.argv[1]
query = sys.argv[2]

with open(invertedIdxPath + "/docFreq.txt", "rb") as fp:
	arr = pickle.load(fp)

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

# Returns posting list containing 'word' in field 'c'
def getPostingList(word, c, invertedIdx):
	listt = []
	if c == 'a':
		c = 'f'

	if c == 'f':
		for d in invertedIdx:
			if int(d.split('f')[1]) > 0:
				listt.append(d.split('a')[0] + '-' + d.split('f')[1])
		return listt

	for d in invertedIdx:
		if int(d.split(c)[1].split(chr(ord(c) + 1))[0]) > 0:
			listt.append(d.split('a')[0] + '-' + d.split(c)[1].split(chr(ord(c) + 1))[0])
	return listt

# Files holding inverted index
invertedIdxFiles = [ f for f in os.listdir(invertedIdxPath) if os.path.isfile(os.path.join(invertedIdxPath, f)) and f.count('_') == 1]
# Files holding titles
titleFiles = [ f for f in os.listdir(invertedIdxPath) if os.path.isfile(os.path.join(invertedIdxPath, f)) and f.count('_') == 2]

# Returns inverted index filname having posting
# list for word 'w' using binary search
def getInvIdxFileName(w):
	i = 0
	j = len(invertedIdxFiles) - 1
	while i <= j:
		m = i + ((j - i) // 2)
		lowerW = invertedIdxFiles[m].split('_')[0]
		upperW = invertedIdxFiles[m].split('_')[1].split('.')[0]
		if lowerW <= w and w <= upperW:
			return invertedIdxFiles[m]
		if w < lowerW:
			j = m - 1
		else:
			i = m + 1
	return ""

# Returns inverted index for word 'w'
def getInvertedIndex(w):
	fileName = getInvIdxFileName(w)
	if fileName == "":
		return []

	match = []
	with open(invertedIdxPath + '/' + fileName, 'r') as f:
		for line in f:
			if line.startswith(w + '-'):
				match = line.strip().split('-')[1:]
				break
	return match

ans = {}
stemmer = PorterStemmer()
if ':' not in query:
	# If plain query
	query = re.findall(r"[\w']{1,}", query)
	query = [ q.lower() for q in query]
	query = list(set(query))

	for q in query:
		ans[q] = emptyQuery.copy()
		stemmedWord = stemmer.stem(q)
		invertedIdx = getInvertedIndex(stemmedWord)
		for k in ans[q].keys():
			try:
				ans[q][k] = getPostingList(stemmedWord, mapping[k], invertedIdx)
			except:
				pass
else:
	# If field query
	queryFormatted = {}
	for k in emptyQuery.keys():
		if k[:1] + ':' in query:
			text = query.split(k[:1] + ':')[1]
			if ':' in text:
				text = text.split(':')[0][:-1]
			text = re.findall(r"[\w']{1,}", text)
			text = list(set([ q.lower() for q in text]))
			for w in text:
				try:
					queryFormatted[w].append(k)
				except:
					queryFormatted[w] = [k]

	for w in queryFormatted.keys():
		ans[w] = emptyQuery.copy()
		stemmedWord = stemmer.stem(w)
		invertedIdx = getInvertedIndex(stemmedWord)
		for q in queryFormatted[w]:
			try:
				ans[w][q] = getPostingList(stemmedWord, mapping[q], invertedIdx)
			except:
				pass

# weights for different fields
weights = {
	"title": 0.4,
	"body": 0.27,
	"infobox": 0.22,
	"categories": 0.1,
	"references": 0.05,
	"links": 0.05,
}

# stores score for all docs
docScores = defaultdict(float)

# Returns number of words in doc with doc ID = 'docId'
def getNumWords(docId):
	return arr[int(docId)]

# adds score for word 'word' in field 'field'
def addScore(field, postingList):
	if len(postingList) == 0:
		return

	tf = (1 + math.log(21384756 / (1 + len(postingList))))
	for p in postingList:
		splittedS = p.split('-')
		docScores[splittedS[0]] += weights[field] * tf * math.sqrt(int(splittedS[1]) / getNumWords(splittedS[0]))

for w in ans.keys():
	for f in ans[w].keys():
		addScore(f, ans[w][f])

# get top 10 docs
docsWithScores = [[k, v] for k, v in docScores.items()]
docsWithScores = sorted(docsWithScores, key=lambda x: x[1], reverse=True)[:10]

# Returns title filname having title for doc with doc ID = 'docId'
def getTitleFileName(docId):
	docId = int(docId)
	i = 0
	j = len(titleFiles) - 1
	while i <= j:
		m = i + ((j - i) // 2)
		lowerID = int(titleFiles[m].split('.')[0].split('_')[1])
		upperID = int(titleFiles[m].split('.')[0].split('_')[2])
		if lowerID <= docId and docId <= upperID:
			return titleFiles[m]
		if docId < lowerID:
			j = m - 1
		else:
			i = m + 1
	return ""

# returns title for doc with doc ID = 'docId'
def getTitle(docId):
	fileName = getTitleFileName(docId)
	return '-'.join(lc.getline(invertedIdxPath + '/' + fileName, int(docId) - int(fileName.split('_')[1]) + 1).split('-')[1:])

end = time.time()

for i in range(len(docsWithScores)):
	docsWithScores[i][1] = getTitle(docsWithScores[i][0])

if len(docsWithScores) == 0:
	print("No docs found!")
else:
	for d in docsWithScores:
		print(', '.join(d))

print(end - start, '\n')