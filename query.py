import os
import re
import sys
import json
import time
import math
from nltk.stem import PorterStemmer
from collections import defaultdict

start = time.time()
invertedIdxPath = sys.argv[1]
query = sys.argv[2]

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
	if c == 'f':
		for d in invertedIdx:
			if int(d.split('f')[1]) > 0:
				listt.append(d)
		return listt

	for d in invertedIdx:
		if int(d.split(c)[1].split(chr(ord(c) + 1))[0]) > 0:
			listt.append(d)

	return listt

# Files holding inverted index
invertedIdxFiles = [ f for f in os.listdir(invertedIdxPath) if os.path.isfile(os.path.join(invertedIdxPath, f)) and f.count('_') == 1]
# Files holding titles
titleFiles = [ f for f in os.listdir(invertedIdxPath) if os.path.isfile(os.path.join(invertedIdxPath, f)) and f.count('_') == 2]

# Returns inverted index filname having posting list for word 'w'
def getInvIdxFileName(w):
	for f in invertedIdxFiles:
		lowerW = f.split('.')[0].split('_')[0]
		upperW = f.split('.')[0].split('_')[1]
		if w >= lowerW and w <= upperW:
			return f
	return ""

# Returns inverted index for word 'w'
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
# cache for posting list
postingListCache = {}
if ':' not in query:
	# If plain query
	query = re.findall(r"[\w']{1,}", query)
	query = list(set(query))

	for q in query:
		ans[q] = emptyQuery.copy()
		stemmedWord = stemmer.stem(q.lower())
		invertedIdx = getInvertedIndex(stemmedWord)
		postingListCache[stemmedWord] = invertedIdx
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
		postingListCache[stemmedWord] = invertedIdx
		for q in queryFormatted[w]:
			try:
				ans[w][q] = getPostingList(stemmedWord, mapping[q], invertedIdx)
			except:
				pass

# weights for different fields
weights = {
	"title": 0.3,
	"body": 0.25,
	"infobox": 0.2,
	"categories": 0.1,
	"references": 0.05,
	"links": 0.05,
}

# stores score for all docs
docScores = defaultdict(float)

# adds score for word 'word' in field 'field'
def addScore(word, field, postingList):
	c = 0
	for p in postingList:
		if mapping[field] == 'f':
			c += (int(p.split(mapping[field])[1]) > 0)
		else:
			c += (int(p.split(mapping[field])[1].split(chr(ord(mapping[field]) + 1))[0]) > 0)

	# Need to divide by something
	for p in postingList:
		if mapping[field] == 'f':
			docScores[p.split('a')[0]] += weights[field] * (1 + math.log(21384756 / c)) * int(p.split(mapping[field])[1])
		else:
			docScores[p.split('a')[0]] += weights[field] * (1 + math.log(21384756 / c)) * int(p.split(mapping[field])[1].split(chr(ord(mapping[field]) + 1))[0])

for w in ans.keys():
	for f in ans[w].keys():
		addScore(w, f, ans[w][f])

docsWithScores = [[k, v] for k, v in docScores.items()]
docsWithScores = sorted(docsWithScores, key=lambda x: x[1], reverse=True)
# get top 10 docs
docsWithScores = docsWithScores[:10]

# Returns title filname having title for doc with doc ID = 'docId'
def getTitleFileName(docId):
	docId = int(docId)
	for f in titleFiles:
		lowerID = int(f.split('.')[0].split('_')[1])
		upperID = int(f.split('.')[0].split('_')[2])
		if docId >= lowerID and docId <= upperID:
			return f
	return ""

# returns title for doc with doc ID = 'docId'
def getTitle(docId):
	fileName = getTitleFileName(docId)
	f = open(invertedIdxPath + '/' + fileName)
	for line in f:
		if line.startswith(docId + '-'):
			f.close()
			return '-'.join(line.strip().split('-')[1:])
	f.close()
	return ""

for i in range(len(docsWithScores)):
	docsWithScores[i][1] = getTitle(docsWithScores[i][0])

end = time.time()

if len(docsWithScores) == 0:
	print("No docs found!")
else:
	for d in docsWithScores:
		print(', '.join(d))

print(end - start, '\n')